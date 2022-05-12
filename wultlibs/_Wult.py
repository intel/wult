#!/usr/bin/python*
#
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
wult - a tool for measuring C-state latency.
"""

import sys
import logging
import contextlib
from pathlib import Path

try:
    import argcomplete
except ImportError:
    # We can live without argcomplete, we only lose tab completions.
    argcomplete = None

from pepclibs.helperlibs import Logging, ArgParse, Trivial
from pepclibs.helperlibs.Exceptions import Error, ErrorNotSupported
from pepclibs import CStates, CPUInfo
from pepclibs.msr import PowerCtl
from wultlibs.helperlibs import ReportID, Human
from wultlibs.htmlreport import WultReport
from wultlibs.rawresultlibs import WORawResult
from wultlibs import Deploy, ToolsCommon, Devices, EventsProvider, WultRunner, WultStatsCollect

VERSION = "1.9.21"
OWN_NAME = "wult"

# By default 'ReportID' module does not allow for the ":" character, but it is part of the PCI
# address, and we allow for PCI addresses as device IDs. Here are few constants that we use to
# extend the default allowed report ID characters set.
REPORTID_ADDITIONAL_CHARS = ":"
REPORTID_CHARS_DESCR = ReportID.get_charset_descr(additional_chars=REPORTID_ADDITIONAL_CHARS)

# Regular expressions for the datapoint CSV file columns names that should show up in the hover
# text of the scatter plot. The middle element selects all the core and package C-state residency
# columns.
HOVER_COLNAME_REGEXS = [".*Latency", "IntrOff", ".*Delay", "LDist", "ReqCState", r"[PC]C.+%",
                        "SMI.*", "NMI.*"]

LOG = logging.getLogger()
Logging.setup_logger(prefix=OWN_NAME)

def get_axes(optname, report_size=None):
    """
    Returns the CSV column name regex for a given plot option name and report size setting.
      * optname - plot option name ('xaxes', 'yaxes', 'hist' or 'chist')
      * report_size - report size setting ('small', 'medium' or 'large'), defaults to 'small'.
    """

    if not report_size:
        report_size = "small"

    optnames = getattr(WultReport, f"{report_size.upper()}_{optname.upper()}")
    # The result is used for argparse, which does not accept '%' symbols.
    if optnames:
        return optnames.replace("%", "%%")
    return None

def build_arguments_parser():
    """Build and return the arguments parser object."""

    text = f"{OWN_NAME} - a tool for measuring C-state latency."
    parser = ArgParse.SSHOptsAwareArgsParser(description=text, prog=OWN_NAME, ver=VERSION)

    text = "Force coloring of the text output."
    parser.add_argument("--force-color", action="store_true", help=text)
    subparsers = parser.add_subparsers(title="commands", metavar="")
    subparsers.required = True

    #
    # Create parsers for the "deploy" command.
    #
    with Deploy.Deploy(OWN_NAME) as depl:
        depl.add_deploy_cmdline_args(subparsers, deploy_command, argcomplete=argcomplete)

    #
    # Create parsers for the "scan" command.
    #
    text = "Scan for device id."
    descr = """Scan for compatible device."""
    subpars = subparsers.add_parser("scan", help=text, description=descr)
    subpars.set_defaults(func=ToolsCommon.scan_command)

    ArgParse.add_ssh_options(subpars)

    #
    # Create parsers for the "load" command.
    #
    text = f"Load {OWN_NAME} drivers and exit."
    descr = f"""Load {OWN_NAME} drivers and exit without starting the measurements."""
    subpars = subparsers.add_parser("load", help=text, description=descr)
    subpars.set_defaults(func=load_command)

    text = """This command exists for debugging and troubleshooting purposes. Please, do not use for
              other reasons. keep in mind that if the the specified \'devid\' device was bound to
              some driver (e.g., a network driver), it will be unbinded and with this option It
              won't be binded back."""

    subpars.add_argument("--no-unload", action="store_true", help=text)

    text = f"""By default {OWN_NAME} refuses to load network card drivers if its Linux network
               interface is in an active state, such as "up". Use '--force' to disable this safety
               mechanism. Use '--force' option with caution."""
    subpars.add_argument("--force", action="store_true", help=text)

    text = "The device ID, same as in the 'start' command."""
    subpars.add_argument("devid", help=text)

    ArgParse.add_ssh_options(subpars)

    #
    # Create parsers for the "start" command.
    #
    text = "Start the measurements."
    descr = """Start measuring and recording C-state latency."""
    subpars = subparsers.add_parser("start", help=text, description=descr)
    subpars.set_defaults(func=start_command)

    ArgParse.add_ssh_options(subpars)

    subpars.add_argument("-c", "--datapoints", default=1000000, metavar="COUNT", dest="dpcnt",
                         help=ToolsCommon.DATAPOINTS_DESCR)
    subpars.add_argument("--time-limit", dest="tlimit", metavar="LIMIT",
                         help=ToolsCommon.TIME_LIMIT_DESCR)
    subpars.add_argument("--rfilt", action=ArgParse.OrderedArg, help=ToolsCommon.RFILT_START_DESCR)
    subpars.add_argument("--rsel", action=ArgParse.OrderedArg, help=ToolsCommon.RSEL_DESCR)
    text = f"""{ToolsCommon.KEEP_FILTERED_DESCR} Here is an example. Suppose you want to collect
               100000 datapoints where PC6 residency is greater than 0. In this case, you can use
               these options: -c 100000 --rfilt="PC6%% == 0". The result will contain 100000
               datapoints, all of them will have non-zero PC6 residency. But what if you do not want
               to simply discard the other datapoints, because they are also interesting? Well, add
               the '--keep-filtered' option. The result will contain, say, 150000 datapoints, 100000
               of which will have non-zero PC6 residency."""
    subpars.add_argument("--keep-filtered", action="store_true", help=text)

    arg = subpars.add_argument("-o", "--outdir", type=Path, help=ToolsCommon.START_OUTDIR_DESCR)
    if argcomplete:
        arg.completer = argcomplete.completers.DirectoriesCompleter()

    text = ToolsCommon.get_start_reportid_descr(REPORTID_CHARS_DESCR)
    subpars.add_argument("--reportid", help=text)

    text = """Comma-separated list of statistics to collect. The statistics are collected in
              parallel with measuring C-state latency. They are stored in the the "stats"
              sub-directory of the output directory. By default, only 'sysinfo' statistics are
              collected. Use 'all' to collect all possible statistics. Use '--stats=""' or
              --stats='none' to disable statistics collection. If you know exactly what statistics
              you need, specify the comma-separated list of statistics to collect. For example, use
              'turbostat,acpower' if you need only turbostat and AC power meter statistics. You can
              also specify the statistics you do not want to be collected by pre-pending the '!'
              symbol. For example, 'all,!turbostat' would mean: collect all the statistics supported
              by the SUT, except for 'turbostat'.  Use the '--list-stats' option to get more
              information about available statistics. By default, only 'sysinfo' statistics are
              collected."""
    subpars.add_argument("--stats", default="sysinfo", help=text)

    text = """The intervals for statistics. Statistics collection is based on doing periodic
              snapshots of data. For example, by default the 'acpower' statistics collector reads
              SUT power consumption for the last second every second, and 'turbostat' default
              interval is 5 seconds. Use 'acpower:5,turbostat:10' to increase the intervals to 5 and
              10 seconds correspondingly.  Use the '--list-stats' to get the default interval
              values."""
    subpars.add_argument("--stats-intervals", help=text)

    text = f"""Print information about the statistics '{OWN_NAME}' can collect and exit."""
    subpars.add_argument("--list-stats", action="store_true", help=text)

    text = f"""This tool works by scheduling a delayed event, then sleeping and waiting for it to
                happen. This step is referred to as a "measurement cycle" and it is usually repeated
                many times. The launch distance defines how far in the future the delayed event is
                sceduled. By default this tool randomly selects launch distance within a range. The
                default range is [0,4ms], but you can override it with this option. Specify a
                comma-separated range (e.g '--ldist 10,5000'), or a single value if you want launch
                distance to be precisely that value all the time.  The default unit is microseconds,
                but you can use the following specifiers as well: {Human.DURATION_NS_SPECS_DESCR}.
                For example, '--ldist 10us,5ms' would be a [10,5000] microseconds range. Too small
                values may cause failures or prevent the SUT from reaching deep C-states. If the
                range starts with 0, the minimum possible launch distance value allowed by the
                delayed event source will be used. The optimal launch distance range is
                system-specific."""
    subpars.add_argument("-l", "--ldist", help=text, default="0,4000")

    text = """The logical CPU number to measure, default is CPU 0."""
    subpars.add_argument("--cpunum", help=text, type=int, default=0)

    text = f"""Enable interrupt latency focused measurements. Most C-states are entered using the
               'mwait' instruction with interrupts disabled. When there is an interrupt, the CPU
               wakes up and continues running the instructions after the 'mwait'. The CPU first runs
               some housekeeping code, and only then the interrupts get enabled and the CPU jumps to
               the interrupt handler. {OWN_NAME.title()} measures 'WakeLatency' during the
               "housekeeping" stage, and 'IntrLatency' is measured in the interrupt handler.
               However, the 'WakeLatency' measurement takes time and affects the measured
               'IntrLatency'. This option disables 'WakeLatency' measurements, which improves
               'IntrLatency' measurements' accuracy."""
    subpars.add_argument("--intr-focus", action="store_true", help=text)

    text = f"""{OWN_NAME.title()} receives raw datapoints from the driver, then processes them, and
               then saves the processed datapoint in the 'datapoints.csv' file. The processing
               involves converting TSC cycles to microseconds, so {OWN_NAME} needs SUT's TSC rate.
               TSC rate is calculated from the datapoints, which come with TSC counters and
               timestamps, so TSC rate can be calculated as "delta TSC / delta timestamp". In other
               words, {OWN_NAME} needs two datapoints to calculate TSC rate. However, the datapoints
               have to be far enough apart, and this option defines the distance between the
               datapoints (in seconds). The default distance is 10 seconds, which means that
               {OWN_NAME} will keep collecting and buffering datapoints for 10s without processing
               them (because processing requires TSC rate to be known). After 10s, {OWN_NAME} will
               start processing all the buffered datapoints, and then the newly collected
               datapoints. Generally, longer TSC calculation time translates to better accuracy."""
    subpars.add_argument("--tsc-cal-time", default="10s", help=text)

    text = f"""{OWN_NAME.title()} receives raw datapoints from the driver, then processes them, and
               then saves the processed datapoint in the 'datapoints.csv' file. In order to keep the
               CSV file smaller, {OWN_NAME} keeps only the esential information, and drops the rest.
               For example, raw timestamps are dropped. With this option, however, {OWN_NAME} saves
               all the raw data to the CSV file, along with the processed data."""
    subpars.add_argument("--keep-raw-data", action="store_true", dest="keep_rawdp", help=text)

    text = f"""This option exists for debugging and troubleshooting purposes. Please, do not use
               for other reasons. While normally {OWN_NAME} kernel modules are unloaded after the
               measurements are done, with this option the modules will stay loaded into the
               kernel. Keep in mind that if the the specified 'devid' device was bound to some
               driver (e.g., a network driver), it will be unbinded and with this option it won't be
               binded back."""
    subpars.add_argument("--no-unload", action="store_true", help=text)

    text = """This option is for research purposes and you most probably do not need it. Linux's
              'cpuidle' subsystem enters most C-states with interrupts disabled. So when the CPU
              exits the C-state becaouse of an interrupt, it will not jump to the interrupt
              handler, but instead, continue running some 'cpuidle' housekeeping code. After this,
              the 'cpuidle' subsystem enables interrupts, and the CPU jumps to the interrupt
              hanlder. Therefore, there is a tiny delay the 'cpuidle' subsystem adds on top of the
              hardware C-state latency. For fast C-states like C1, this tiny delay may even be
              measurable on some platforms. This option allows to measure that delay. It makes wult
              enable interrupts before linux enters the C-state. This option is generally a crude
              option along with '--intr-focus'. When this option is used, often it makes sense to
              use '--intr-focus' at the same time."""
    subpars.add_argument("--early-intr", action="store_true", help=text)

    text = f"""Deeper C-states like Intel CPU core C6 flush the CPU cache before entering the
               C-state. Therefore, the dirty CPU cache lines must be written back to the main memory
               before entering the C-state. This may increase C-state latency observed by the
               operating system. If this option is used, {OWN_NAME} will try to "dirty" the measured
               CPU cache before requesting C-states. This is done by writing zeroes to a
               pre-allocated 2MiB buffer."""
    subpars.add_argument("--dirty-cpu-cache", action="store_true", help=text)

    text = f"""By default, in order to make CPU cache be filled with dirty cache lines, {OWN_NAME}
               filles a 2MiB buffer with zeroes before requesting a C-state. This buffer is reffered
               to as "dirty cache buffer", or "dcbuf". This option allows for changing the dcbuf
               size. For example, in order to make it 4MiB, use '--dcbuf-size=4MiB'."""
    subpars.add_argument("--dcbuf-size", help=text)

    subpars.add_argument("--report", action="store_true", help=ToolsCommon.START_REPORT_DESCR)

    text = f"""By default {OWN_NAME} does not accept network card as a measurement device if its
               Linux network interface is in an active state, such as "up". Use '--force' to disable
               this safety mechanism. Use '--force' option with caution."""
    subpars.add_argument("--force", action="store_true", help=text)

    text = """The ID of the device to use for measuring the latency. For example, it can be a PCI
              address of the Intel I210 device, or "tdt" for the TSC deadline timer block of the
              CPU. Use the 'scan' command to get supported devices."""
    subpars.add_argument("devid", help=text)

    #
    # Create parsers for the "report" command.
    #
    text = "Create an HTML report."
    descr = """Create an HTML report for one or multiple test results."""
    subpars = subparsers.add_parser("report", help=text, description=descr)
    subpars.set_defaults(func=report_command)

    subpars.add_argument("-o", "--outdir", type=Path,
                         help=ToolsCommon.get_report_outdir_descr(OWN_NAME))
    subpars.add_argument("--rfilt", action=ArgParse.OrderedArg, help=ToolsCommon.RFILT_DESCR)
    subpars.add_argument("--rsel", action=ArgParse.OrderedArg, help=ToolsCommon.RSEL_DESCR)
    subpars.add_argument("--even-up-dp-count", action="store_true", dest="even_dpcnt",
                         help=ToolsCommon.EVEN_UP_DP_DESCR)
    subpars.add_argument("-x", "--xaxes", help=ToolsCommon.XAXES_DESCR % get_axes('xaxes'))
    subpars.add_argument("-y", "--yaxes", help=ToolsCommon.YAXES_DESCR % get_axes('yaxes'))
    subpars.add_argument("--hist", help=ToolsCommon.HIST_DESCR % get_axes('hist'))
    subpars.add_argument("--chist", help=ToolsCommon.CHIST_DESCR % get_axes('chist'))
    subpars.add_argument("--reportids", help=ToolsCommon.REPORTIDS_DESCR)
    subpars.add_argument("--title-descr", help=ToolsCommon.TITLE_DESCR)
    subpars.add_argument("--relocatable", action="store_true", help=ToolsCommon.RELOCATABLE_DESCR)
    subpars.add_argument("--list-columns", action="store_true", help=ToolsCommon.LIST_COLUMNS_DESCR)

    text = """Generate HTML report with a pre-defined set of diagrams and histograms. Possible
              values: 'small', 'medium' or 'large'. This option is mutually exclusive with
              '--xaxes', '--yaxes', '--hist', '--chist'."""
    subpars.add_argument("--size", dest="report_size", type=str, help=text)

    text = f"""One or multiple {OWN_NAME} test result paths."""
    subpars.add_argument("respaths", nargs="+", type=Path, help=text)

    #
    # Create parsers for the "filter" command.
    #
    text = "Filter datapoints out of a test result."
    subpars = subparsers.add_parser("filter", help=text, description=ToolsCommon.FILT_DESCR)
    subpars.set_defaults(func=ToolsCommon.filter_command)

    subpars.add_argument("--rfilt", action=ArgParse.OrderedArg, help=ToolsCommon.RFILT_DESCR)
    subpars.add_argument("--rsel", action=ArgParse.OrderedArg, help=ToolsCommon.RSEL_DESCR)
    subpars.add_argument("--cfilt", action=ArgParse.OrderedArg, help=ToolsCommon.CFILT_DESCR)
    subpars.add_argument("--csel", action=ArgParse.OrderedArg, help=ToolsCommon.CSEL_DESCR)
    subpars.add_argument("--human-readable", action="store_true",
                         help=ToolsCommon.FILTER_HUMAN_DESCR)
    subpars.add_argument("-o", "--outdir", type=Path, help=ToolsCommon.FILTER_OUTDIR_DESCR)
    subpars.add_argument("--list-columns", action="store_true", help=ToolsCommon.LIST_COLUMNS_DESCR)
    subpars.add_argument("--reportid", help=ToolsCommon.FILTER_REPORTID_DESCR)

    text = f"The {OWN_NAME} test result path to filter."
    subpars.add_argument("respath", type=Path, help=text)

    #
    # Create parsers for the "calc" command.
    #
    text = f"Calculate summary functions for a {OWN_NAME} test result."
    descr = f"""Calculates various summary functions for a {OWN_NAME} test result (e.g., the median
                value for one of the CSV columns)."""
    subpars = subparsers.add_parser("calc", help=text, description=descr)
    subpars.set_defaults(func=ToolsCommon.calc_command)

    subpars.add_argument("--rfilt", action=ArgParse.OrderedArg, help=ToolsCommon.RFILT_DESCR)
    subpars.add_argument("--rsel", action=ArgParse.OrderedArg, help=ToolsCommon.RSEL_DESCR)
    subpars.add_argument("--cfilt", action=ArgParse.OrderedArg, help=ToolsCommon.CFILT_DESCR)
    subpars.add_argument("--csel", action=ArgParse.OrderedArg, help=ToolsCommon.CSEL_DESCR)
    subpars.add_argument("-f", "--funcs", help=ToolsCommon.FUNCS_DESCR)
    subpars.add_argument("--list-funcs", action="store_true", help=ToolsCommon.LIST_FUNCS_DESCR)

    text = f"""The {OWN_NAME} test result path to calculate summary functions for."""
    subpars.add_argument("respath", type=Path, help=text)

    if argcomplete:
        argcomplete.autocomplete(parser)

    return parser

def parse_arguments():
    """Parse input arguments."""

    parser = build_arguments_parser()

    args = parser.parse_args()
    args.toolname = OWN_NAME
    args.devtypes = Devices.DEVTYPES

    return args

def check_settings(pman, dev, csinfo, cpunum, devid):
    """
    Some settings of the SUT may lead to results that are potentially confusing for the user. This
    function looks for such settings and if found, prints a notice message.
      * pman - the process manager object that defines the host to run the measurements on.
      * dev - the delayed event device object created by 'Devices.WultDevice()'.
      * devid - the ID of the device used for measuring the latency.
      * csinfo - cstate info from 'CStates.get_cstates_info()'.
      * cpunum - the logical CPU number to measure.
    """

    if dev.info.get("aspm_enabled"):
        LOG.notice("PCI ASPM is enabled for the delayed event device '%s', and this "
                    "typically increases the measured latency.", devid)

    enabled_cstates = []
    for _, info in csinfo.items():
        if info["disable"] == 0 and info["name"] != "POLL":
            enabled_cstates.append(info["name"])

    with contextlib.suppress(ErrorNotSupported), PowerCtl.PowerCtl(pman=pman) as powerctl:
        # Check for the following 3 conditions to be true at the same time.
        # * C6 is enabled.
        # * C6 pre-wake is enabled.
        # * The "tdt" method is used.
        if devid == "tdt" and "C6" in enabled_cstates and \
            powerctl.is_cpu_feature_supported("cstate_prewake", cpunum) and \
            powerctl.is_cpu_feature_enabled("cstate_prewake", cpunum):
            LOG.notice("C-state prewake is enabled, and this usually hides the real "
                       "latency when using '%s' as delayed event device.", devid)

        # Check for the following 2 conditions to be true at the same time.
        # * C1 is enabled.
        # * C1E auto-promotion is enabled.
        if enabled_cstates in [["C1"], ["C1_ACPI"]]:
            if powerctl.is_cpu_feature_enabled("c1e_autopromote", cpunum):
                LOG.notice("C1E autopromote is enabled, all %s requests are converted to C1E.",
                            enabled_cstates[0])

def deploy_command(args):
    """Implements the 'deploy' command."""

    with ToolsCommon.get_pman(args) as pman, \
         Deploy.Deploy(OWN_NAME, pman=pman, debug=args.debug) as depl:
        depl.deploy()

def list_stats():
    """Print information about statistics."""

    if not WultStatsCollect.STATS_INFO:
        raise Error("statistics collection is not supported on your system")

    for stname, stinfo in WultStatsCollect.STATS_INFO.items():
        LOG.info("* %s", stname)
        if stinfo.get("interval"):
            LOG.info("  - Default interval: %.1fs", stinfo["interval"])
        LOG.info("  - %s", stinfo["description"])

def start_command(args):
    """Implements the 'start' command."""

    if args.list_stats:
        list_stats()
        return

    if args.dcbuf_size and not args.dirty_cpu_cache:
        raise Error("'--dcbuf-size' option must be used together with '--dirty-cpu-cache' option")

    stconf = None
    if args.stats and args.stats != "none":
        if not WultStatsCollect.STATS_NAMES:
            raise Error("statistics collection is not supported on your system")
        stconf = WultStatsCollect.parse_stats(args.stats, args.stats_intervals)

    with contextlib.ExitStack() as stack:
        pman = ToolsCommon.get_pman(args)
        stack.enter_context(pman)

        with Deploy.Deploy(OWN_NAME, pman=pman, debug=args.debug) as depl:
            if depl.is_deploy_needed():
                msg = f"'{OWN_NAME}' drivers are not up-to-date{pman.hostmsg}, " \
                      f"please run: {OWN_NAME} deploy"
                if pman.is_remote:
                    msg += f" -H {pman.hostname}"
                LOG.warning(msg)

        if not args.reportid and pman.is_remote:
            prefix = pman.hostname
        else:
            prefix = None
        args.reportid = ReportID.format_reportid(prefix=prefix, reportid=args.reportid,
                                                 strftime=f"{OWN_NAME}-{args.devid}-%Y%m%d",
                                                 additional_chars=REPORTID_ADDITIONAL_CHARS)

        if not args.outdir:
            args.outdir = Path(f"./{args.reportid}")
        if args.tlimit:
            args.tlimit = Human.parse_duration(args.tlimit, default_unit="m", name="time limit")
        if args.ldist:
            args.ldist = ToolsCommon.parse_ldist(args.ldist)

        if not Trivial.is_int(args.dpcnt) or int(args.dpcnt) <= 0:
            raise Error(f"bad datapoints count '{args.dpcnt}', should be a positive integer")
        args.dpcnt = int(args.dpcnt)

        args.tsc_cal_time = Human.parse_duration(args.tsc_cal_time, default_unit="s",
                                                name="TSC calculation time")

        if args.dirty_cpu_cache:
            if not args.dcbuf_size:
                args.dcbuf_size = "2MiB"

            args.dcbuf_size = Human.parse_bytesize(args.dcbuf_size)
            if args.dcbuf_size <= 0:
                raise Error(f"bad dirty CPU cache buffer size '{args.dcbuf_size}', must be a "
                            f"positive integer")

        cpuinfo = CPUInfo.CPUInfo(pman=pman)
        stack.enter_context(cpuinfo)

        args.cpunum = cpuinfo.normalize_cpu(args.cpunum)

        res = WORawResult.WultWORawResult(args.reportid, args.outdir, VERSION, args.cpunum)
        stack.enter_context(res)

        ToolsCommon.setup_stdout_logging(OWN_NAME, res.logs_path)
        ToolsCommon.set_filters(args, res)

        dev = Devices.WultDevice(args.devid, args.cpunum, pman, dmesg=True, force=args.force)
        stack.enter_context(dev)

        rcsobj = CStates.ReqCStates(pman=pman)
        csinfo = rcsobj.get_cpu_cstates_info(res.cpunum)

        check_settings(pman, dev, csinfo, args.cpunum, args.devid)

        runner = WultRunner.WultRunner(pman, dev, res, ldist=args.ldist, intr_focus=args.intr_focus,
                                       early_intr=args.early_intr, tsc_cal_time=args.tsc_cal_time,
                                       dcbuf_size=args.dcbuf_size, rcsobj=rcsobj, stconf=stconf)
        stack.enter_context(runner)

        runner.unload = not args.no_unload
        runner.prepare()
        runner.run(dpcnt=args.dpcnt, tlimit=args.tlimit, keep_rawdp=args.keep_rawdp)

    if not args.report:
        return

    rsts = ToolsCommon.open_raw_results([args.outdir], args.toolname)
    rep = WultReport.WultReport(rsts, args.outdir, title_descr=args.reportid)
    rep.relocatable = False
    rep.set_hover_colnames(HOVER_COLNAME_REGEXS)
    rep.generate()

def report_command(args):
    """Implements the 'report' command."""

    if args.report_size:
        if any({getattr(args, name) for name in ("xaxes", "yaxes", "hist", "chist")}):
            raise Error("'--size' and ('--xaxes', '--yaxes', '--hist', '--chist') options are "
                        "mutually exclusive, use either '--size' or the other options, not both")
        if args.report_size.lower() not in ("small", "medium", "large"):
            raise Error(f"bad '--size' value '{args.report_size}', use one of: small, medium, "
                         "large")

    # Split the comma-separated lists.
    for name in ("xaxes", "yaxes", "hist", "chist"):
        val = getattr(args, name)
        if val:
            if val == "none":
                setattr(args, name, "")
            else:
                setattr(args, name, Trivial.split_csv_line(val))
        elif args.report_size:
            size_default = get_axes(name, args.report_size)
            if size_default:
                setattr(args, name, Trivial.split_csv_line(size_default))
            else:
                setattr(args, name, None)

    rsts = ToolsCommon.open_raw_results(args.respaths, args.toolname, reportids=args.reportids,
                                        reportid_additional_chars=REPORTID_ADDITIONAL_CHARS)

    if args.list_columns:
        ToolsCommon.list_result_columns(rsts)
        return

    for res in rsts:
        ToolsCommon.set_filters(args, res)

    if args.even_dpcnt:
        ToolsCommon.even_up_dpcnt(rsts)

    if args.outdir is None:
        if len(args.respaths) > 1:
            args.outdir = ReportID.format_reportid(prefix=f"{OWN_NAME}-report",
                                                   reportid=rsts[0].reportid,
                                                   additional_chars=REPORTID_ADDITIONAL_CHARS)
        else:
            args.outdir = args.respaths[0]

        args.outdir = Path(args.outdir)
        LOG.info("Generating report into: %s", args.outdir)

    rep = WultReport.WultReport(rsts, args.outdir, title_descr=args.title_descr,
                                        xaxes=args.xaxes, yaxes=args.yaxes, hist=args.hist,
                                        chist=args.chist)
    rep.relocatable = args.relocatable
    rep.set_hover_colnames(HOVER_COLNAME_REGEXS)
    rep.generate()

def load_command(args):
    """Implements the 'load' command."""

    with ToolsCommon.get_pman(args) as pman:
        with Devices.WultDevice(args.devid, 0, pman, dmesg=True, force=args.force) as dev:
            with EventsProvider.EventsProvider(dev, 0, pman) as ep:
                ep.unload = not args.no_unload
                ep.prepare()
                LOG.info("Loaded the '%s' %s delayed event driver", ep.dev.drvname, OWN_NAME)

def main():
    """Script entry point."""

    try:
        args = parse_arguments()

        if not getattr(args, "func", None):
            LOG.error("please, run '%s -h' for help.", OWN_NAME)
            return -1

        args.func(args)
    except KeyboardInterrupt:
        LOG.info("Interrupted, exiting")
        return -1
    except Error as err:
        LOG.error_out(err)
        return -1

    return 0

# The script entry point.
if __name__ == "__main__":
    sys.exit(main())
