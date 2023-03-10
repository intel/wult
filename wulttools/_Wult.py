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
from pathlib import Path

try:
    import argcomplete
except ImportError:
    # We can live without argcomplete, we only lose tab completions.
    argcomplete = None

from pepclibs.helperlibs import Logging, Human, ArgParse
from pepclibs.helperlibs.Exceptions import Error
from wultlibs.deploylibs import _Deploy
from wulttools import _Common, _WultCommon

_VERSION = "1.11.4"
_OWN_NAME = "wult"

# The deployment information dictionary. See 'DeployBase.__init__()' for details.
_WULT_DEPLOY_INFO = {
    "installables" : {
        "wult" : {
            "category" : "drivers",
            "minkver"  : "5.6",
            "deployables" : ("wult", "wult_igb", "wult_tdt", "wult_hrt", ),
        },
        "wult-hrt-helper" : {
            "category" : "bpfhelpers",
            "minkver"  : "5.15",
            "deployables" : ("wult-hrt-helper", ),
        },
        "wult-tdt-helper" : {
            "category" : "bpfhelpers",
            "minkver"  : "5.15",
            "deployables" : ("wult-tdt-helper", ),
        },
    },
}

_LOG = logging.getLogger()
Logging.setup_logger(prefix=_OWN_NAME)

def _build_arguments_parser():
    """Build and return the arguments parser object."""

    text = f"{_OWN_NAME} - a tool for measuring C-state latency."
    parser = ArgParse.SSHOptsAwareArgsParser(description=text, prog=_OWN_NAME, ver=_VERSION)

    text = "Force coloring of the text output."
    parser.add_argument("--force-color", action="store_true", help=text)
    subparsers = parser.add_subparsers(title="commands", dest="a command")
    subparsers.required = True

    #
    # Create parsers for the "deploy" command.
    #
    subpars = _Deploy.add_deploy_cmdline_args(_OWN_NAME, _WULT_DEPLOY_INFO, subparsers,
                                              _deploy_command, argcomplete=argcomplete)
    text = """Deploy the eBPF helper, but do not deploy the drivers. This is a debug and development
              option, do not use it for other purposes."""
    subpars.add_argument("--skip-drivers", action="store_true", help=text)

    #
    # Create parsers for the "scan" command.
    #
    text = "Scan for available devices."
    descr = """Scan for available devices."""
    subpars = subparsers.add_parser("scan", help=text, description=descr)
    subpars.set_defaults(func=_Common.scan_command)
    subpars.add_argument("--all", action="store_true",
                         help=_Common.get_scan_all_descr(_OWN_NAME))

    ArgParse.add_ssh_options(subpars)

    #
    # Create parsers for the "start" command.
    #
    text = "Start the measurements."
    descr = """Start measuring and recording C-state latency."""
    subpars = subparsers.add_parser("start", help=text, description=descr)
    subpars.set_defaults(func=_start_command)

    ArgParse.add_ssh_options(subpars)

    subpars.add_argument("-c", "--datapoints", default=1000000, metavar="COUNT", dest="dpcnt",
                         help=_Common.DATAPOINTS_DESCR)
    subpars.add_argument("--time-limit", dest="tlimit", metavar="LIMIT",
                         help=_Common.TIME_LIMIT_DESCR)
    subpars.add_argument("--exclude", action=ArgParse.OrderedArg,
                         help=_Common.EXCL_START_DESCR)
    subpars.add_argument("--include", action=ArgParse.OrderedArg, help=_Common.INCL_DESCR)
    text = f"""{_Common.KEEP_FILTERED_DESCR} Here is an example. Suppose you want to collect
               100000 datapoints where PC6 residency is greater than 0. In this case, you can use
               these options: -c 100000 --exclude="PC6%% == 0". The result will contain 100000
               datapoints, all of them will have non-zero PC6 residency. But what if you do not want
               to simply discard the other datapoints, because they are also interesting? Well, add
               the '--keep-filtered' option. The result will contain, say, 150000 datapoints, 100000
               of which will have non-zero PC6 residency."""
    subpars.add_argument("--keep-filtered", action="store_true", help=text)

    arg = subpars.add_argument("-o", "--outdir", type=Path, help=_Common.START_OUTDIR_DESCR)
    if argcomplete:
        arg.completer = argcomplete.completers.DirectoriesCompleter()

    subpars.add_argument("--reportid", help=_Common.START_REPORTID_DESCR)

    subpars.add_argument("--stats", default="sysinfo", help=_Common.STATS_DESCR)

    subpars.add_argument("--stats-intervals", help=_Common.STAT_INTERVALS_DESCR)

    subpars.add_argument("--list-stats", action="store_true",
                         help=_Common.LIST_STATS_DESCR % _OWN_NAME)

    text = f"""This tool works by scheduling a delayed event, then sleeping and waiting for it to
               happen. This step is referred to as a "measurement cycle" and it is usually repeated
               many times. The launch distance defines how far in the future the delayed event is
               scheduled. By default this tool randomly selects launch distance within a range. The
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

    text = f"""{_OWN_NAME.title()} receives raw datapoints from the driver, then processes them, and
               then saves the processed datapoint in the 'datapoints.csv' file. The processing
               involves converting TSC cycles to microseconds, so {_OWN_NAME} needs SUT's TSC rate.
               TSC rate is calculated from the datapoints, which come with TSC counters and
               timestamps, so TSC rate can be calculated as "delta TSC / delta timestamp". In other
               words, {_OWN_NAME} needs two datapoints to calculate TSC rate. However, the datapoints
               have to be far enough apart, and this option defines the distance between the
               datapoints (in seconds). The default distance is 10 seconds, which means that
               {_OWN_NAME} will keep collecting and buffering datapoints for 10s without processing
               them (because processing requires TSC rate to be known). After 10s, {_OWN_NAME} will
               start processing all the buffered datapoints, and then the newly collected
               datapoints. Generally, longer TSC calculation time translates to better accuracy."""
    subpars.add_argument("--tsc-cal-time", default="10s", help=text)

    text = f"""{_OWN_NAME.title()} receives raw datapoints from the driver, then processes them, and
               then saves the processed datapoint in the 'datapoints.csv' file. In order to keep the
               CSV file smaller, {_OWN_NAME} keeps only the essential information, and drops the rest.
               For example, raw timestamps are dropped. With this option, however, {_OWN_NAME} saves
               all the raw data to the CSV file, along with the processed data."""
    subpars.add_argument("--keep-raw-data", action="store_true", dest="keep_rawdp", help=text)

    text = f"""This option exists for debugging and troubleshooting purposes. Please, do not use
               for other reasons. If {_OWN_NAME} loads kernel modules, they get unloaded after the
               measurements are done. But with this option {_OWN_NAME} will not unload the
               modules."""
    subpars.add_argument("--no-unload", action="store_true", help=text)

    text = """This option is for research purposes and you most probably do not need it. Linux's
              'cpuidle' subsystem enters most C-states with interrupts disabled. So when the CPU
              exits the C-state because of an interrupt, it will not jump to the interrupt
              handler, but instead, continue running some 'cpuidle' housekeeping code. After this,
              the 'cpuidle' subsystem enables interrupts, and the CPU jumps to the interrupt
              handler. Therefore, there is a tiny delay the 'cpuidle' subsystem adds on top of the
              hardware C-state latency. For fast C-states like C1, this tiny delay may even be
              measurable on some platforms. This option allows to measure that delay. It makes wult
              enable interrupts before linux enters the C-state."""
    subpars.add_argument("--early-intr", action="store_true", help=text)

    subpars.add_argument("--report", action="store_true", help=_Common.START_REPORT_DESCR)
    subpars.add_argument("--force", action="store_true", help=_Common.START_FORCE_DESCR)

    text = """The ID of the device to use for measuring the latency. For example, it can be a PCI
              address of the Intel I210 device, or "tdt" for the TSC deadline timer block of the
              CPU. Use the 'scan' command to get supported devices."""
    subpars.add_argument("devid", nargs= '?' if '--list-stats' in sys.argv else None, help=text)

    #
    # Create parsers for the "report" command.
    #
    text = "Create an HTML report."
    descr = """Create an HTML report for one or multiple test results."""
    subpars = subparsers.add_parser("report", help=text, description=descr)
    subpars.set_defaults(func=_report_command)

    subpars.add_argument("-o", "--outdir", type=Path,
                         help=_Common.get_report_outdir_descr(_OWN_NAME))
    subpars.add_argument("--exclude", action=ArgParse.OrderedArg, help=_Common.EXCL_DESCR)
    subpars.add_argument("--include", action=ArgParse.OrderedArg, help=_Common.INCL_DESCR)
    subpars.add_argument("--even-up-dp-count", action="store_true", dest="even_dpcnt",
                         help=_Common.EVEN_UP_DP_DESCR)

    # Format axes options' help texts with default axes.
    xaxes_help = _Common.XAXES_DESCR % _WultCommon.get_axes("xaxes", escape_percent=True)
    yaxes_help = _Common.YAXES_DESCR % _WultCommon.get_axes("yaxes", escape_percent=True)
    hist_help = _Common.HIST_DESCR % _WultCommon.get_axes("hist", escape_percent=True)
    chist_help = _Common.CHIST_DESCR % _WultCommon.get_axes("chist", escape_percent=True)
    subpars.add_argument("-x", "--xaxes", help=xaxes_help)
    subpars.add_argument("-y", "--yaxes", help=yaxes_help)
    subpars.add_argument("--hist", help=hist_help)
    subpars.add_argument("--chist", help=chist_help)

    subpars.add_argument("--reportids", help=_Common.REPORTIDS_DESCR)
    subpars.add_argument("--report-descr", help=_Common.REPORT_DESCR)
    subpars.add_argument("--relocatable", action="store_true", help=_Common.RELOCATABLE_DESCR)
    subpars.add_argument("--list-metrics", action="store_true",
                         help=_Common.LIST_METRICS_DESCR)

    text = """Generate HTML report with a pre-defined set of diagrams and histograms. Possible
              values: 'small' or 'large'. This option is mutually exclusive with '--xaxes',
              '--yaxes', '--hist', '--chist'."""
    subpars.add_argument("--size", dest="report_size", type=str, help=text)

    text = f"""One or multiple {_OWN_NAME} test result paths."""
    subpars.add_argument("respaths", nargs="+", type=Path, help=text)

    #
    # Create parsers for the "filter" command.
    #
    text = "Filter datapoints out of a test result."
    subpars = subparsers.add_parser("filter", help=text, description=_Common.FILT_DESCR)
    subpars.set_defaults(func=_Common.filter_command)

    subpars.add_argument("--exclude", action=ArgParse.OrderedArg, help=_Common.EXCL_DESCR)
    subpars.add_argument("--include", action=ArgParse.OrderedArg, help=_Common.INCL_DESCR)
    subpars.add_argument("--exclude-metrics", action=ArgParse.OrderedArg, dest="mexclude",
                         help=_Common.MEXCLUDE_DESCR)
    subpars.add_argument("--include-metrics", action=ArgParse.OrderedArg, dest="minclude",
                         help=_Common.MINCLUDE_DESCR)
    subpars.add_argument("--human-readable", action="store_true",
                         help=_Common.FILTER_HUMAN_DESCR)
    subpars.add_argument("-o", "--outdir", type=Path, help=_Common.FILTER_OUTDIR_DESCR)
    subpars.add_argument("--list-metrics", action="store_true",
                         help=_Common.LIST_METRICS_DESCR)
    subpars.add_argument("--reportid", help=_Common.FILTER_REPORTID_DESCR)

    text = f"The {_OWN_NAME} test result path to filter."
    subpars.add_argument("respath", type=Path, help=text)

    #
    # Create parsers for the "calc" command.
    #
    text = f"Calculate summary functions for a {_OWN_NAME} test result."
    descr = f"""Calculates various summary functions for a {_OWN_NAME} test result (e.g., the median
                value for one of the CSV columns)."""
    subpars = subparsers.add_parser("calc", help=text, description=descr)
    subpars.set_defaults(func=_Common.calc_command)

    subpars.add_argument("--exclude", action=ArgParse.OrderedArg, help=_Common.EXCL_DESCR)
    subpars.add_argument("--include", action=ArgParse.OrderedArg, help=_Common.INCL_DESCR)
    subpars.add_argument("--exclude-metrics", action=ArgParse.OrderedArg, dest="mexclude",
                         help=_Common.MEXCLUDE_DESCR)
    subpars.add_argument("--include-metrics", action=ArgParse.OrderedArg, dest="minclude",
                         help=_Common.MINCLUDE_DESCR)
    subpars.add_argument("-f", "--funcs", help=_Common.FUNCS_DESCR)
    subpars.add_argument("--list-funcs", action="store_true", help=_Common.LIST_FUNCS_DESCR)

    text = f"""The {_OWN_NAME} test result path to calculate summary functions for."""
    subpars.add_argument("respath", type=Path, help=text)

    if argcomplete:
        argcomplete.autocomplete(parser)

    return parser

def _parse_arguments():
    """Parse input arguments."""

    parser = _build_arguments_parser()

    args = parser.parse_args()
    args.toolname = _OWN_NAME
    args.toolver = _VERSION
    args.deploy_info = _WULT_DEPLOY_INFO

    return args

def _deploy_command(args):
    """Implements the 'wult deploy' command."""

    from wulttools import _WultDeploy # pylint: disable=import-outside-toplevel

    if args.skip_drivers:
        del args.deploy_info["installables"]["wult"]

    _WultDeploy.deploy_command(args)

def _start_command(args):
    """Implements the 'wult start' command."""

    from wulttools import _WultStart # pylint: disable=import-outside-toplevel

    _WultStart.start_command(args)

def _report_command(args):
    """Implements the 'wult report' command."""

    from wulttools import _WultReport # pylint: disable=import-outside-toplevel

    _WultReport.report_command(args)

def main():
    """Script entry point."""

    try:
        args = _parse_arguments()

        if not getattr(args, "func", None):
            _LOG.error("please, run '%s -h' for help.", _OWN_NAME)
            return -1

        args.func(args)
    except KeyboardInterrupt:
        _LOG.info("Interrupted, exiting")
        return -1
    except Error as err:
        _LOG.error_out(err)

    return 0

# The script entry point.
if __name__ == "__main__":
    sys.exit(main())
