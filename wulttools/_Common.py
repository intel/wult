# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module contains miscellaneous functions used by the tools in the 'wult' project. There is no a
single purpose this module serves, it is just a collection of shared code. Many functions in this
module require the 'args' object which represents the command-line arguments.
"""

# TODO: finish adding type hints to this module.
from __future__ import annotations # Remove when switching to Python 3.10+.

# TODO: Consider splitting this module into smaller modules. E.g., add _ToolStart.py,
# _ToolReport.py, etc - similar to existing _ToolDeploy.py.
import sys
import typing
from pathlib import Path
from pepclibs import ASPM
from pepclibs.helperlibs import Logging, Trivial, YAML, ProcessManager, ArgParse
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound, ErrorNotSupported
from statscollectlibs.helperlibs import ReportID
from statscollectlibs.collector import StatsCollectBuilder
from wultlibs import Devices
from wultlibs.deploy import _Deploy
from wultlibs.helperlibs import Human

if typing.TYPE_CHECKING:
    import argparse
    from typing import cast
    from pepclibs.helperlibs.ArgParse import SSHArgsTypedDict
    from pepclibs.helperlibs.ProcessManager import ProcessManagerType
    from statscollectlibs.deploy.DeployBase import DeployInfoTypedDict

    class StartCmdlArgsTypedDict(SSHArgsTypedDict, total=False):
        """
        Typed dictionary for the "wult start" command-line arguments.

        Attributes:
            (All attributes from 'SSHArgsTypedDict')
            toolname: Name of the tool.
            devid: Device ID used for measurements.
            reportid: The report ID ('--reportid' option). Empty string if not specified.
            outdir: Path to the output directory ('--outdir' option). Defaults to 'reportid'
                    sub-directory in the current directory.
        """

        toolname: str
        devid: str
        reportid: str
        outdir: Path
        ldist: tuple[int, int]

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

# Description for the '--datapoints' option of the 'start' command.
DATAPOINTS_DESCR = """How many datapoints should the test result include, default is 1000000."""

# Duration specifiers description.
DURATION_SPECS_DESCR = "d - days, h - hours, m - minutes, s - seconds"
DURATION_NS_SPECS_DESCR = "ms - milliseconds, us - microseconds, ns - nanoseconds"

# Description for the '--time-limit' option of the 'start' command.
TIME_LIMIT_DESCR = f"""The measurement time limit, i.e., for how long the SUT should be measured.
                       The default unit is minute, but you can use the following handy specifiers
                       as well: {DURATION_SPECS_DESCR}."""

# Description for the '--start-over' option of the 'start' command.
START_OVER_DESCR = """If the output directory already contains the datapoints CSV file with some
                      amount of datapoints in it, the default behavior is to keep them and append
                      more datapoints if necessary. But with this option all the pre-existing
                      datapoints will be removed as soon as the tool starts writing new
                      datapoints."""

# Description for the '--outdir' option of the 'start' command.
START_OUTDIR_DESCR = """Path to the directory to store the results at."""

_REPORTID_CHARS_DESCR = ReportID.get_charset_descr()
START_REPORTID_DESCR = f"""Any string which may serve as an identifier of this run. By default
                           report ID is the current date, prefixed with the remote host name in case
                           the '-H' option was used: [hostname-]YYYYMMDD. For example, "20150323" is
                           a report ID for a run made on March 23, 2015. The allowed characters are:
                           {_REPORTID_CHARS_DESCR}."""

# Description for the '--report' option of the 'start' command.
START_REPORT_DESCR = """Generate an HTML report for collected results (same as calling 'report'
                        command with default arguments)."""

# Description for the '--stats' option of the 'start' command.
default_stnames = ", ".join(StatsCollectBuilder.DEFAULT_STNAMES)
STATS_DESCR = f"""Comma-separated list of statistics to collect. By default, only
                  '{default_stnames}' statistics are collected. Use 'all' to collect all possible
                  statistics. Use '--stats=""' or '--stats="none"' to disable statistics collection.
                  If you know exactly what statistics you need, specify the comma-separated list of
                  statistics to collect."""

# Description for the '--stat-intervals' option of the 'start' command.
STAT_INTERVALS_DESCR = """The intervals for statistics. Statistics collection is based on doing
                          periodic snapshots of data. For example, by default the 'acpower'
                          statistics collector reads SUT power consumption for the last second
                          every second, and 'turbostat' default interval is 5 seconds. Use
                          'acpower:5,turbostat:10' to increase the intervals to 5 and 10 seconds
                          correspondingly. Use the '--list-stats' to get the default interval
                          values."""

# Description for the '--list-stats' option of the 'start' command.
LIST_STATS_DESCR = """Print information about the statistics '%s' can collect and exit."""

# Description for the '--outdir' option of the 'report' command.
def get_report_outdir_descr(toolname):
    """
    Return description for the '--outdir' option of the 'report' command. The arguments are as
    follows.
      * toolname - name of the tool to return the description for.
    """

    descr = f"""Path to the directory to store the report at. By default the report is stored in the
                '{toolname}-report-<reportid>' sub-directory of the test result directory. If there
                are multiple test results, the report is stored in the current directory. The
                '<reportid>' is report ID of {toolname} test result."""
    return descr

# Description for the '--force' option of the 'start' command.
START_FORCE_DESCR = """By default a network card is not accepted as a measurement device if it is
                       used by a Linux network interface and the interface is in an active state,
                       such as "up". Use '--force' to disable this safety mechanism. Use it with
                       caution."""

# Description of the '--all' option of the 'scan' command.
def get_scan_all_descr(toolname):
    """
    Return description for the '--all' option of the 'scan' command. The arguments are as follows.
      * toolname - name of the tool to return the description for.
    """

    descr = f"""By default this command prints only the compatible devices which are supported by
                current {toolname} installation. This option makes this command print about all the
                compatible devices."""
    return descr

# Description for the '--even-up-dp-count' option of the 'report' command.
EVEN_UP_DP_DESCR = """Even up datapoints count before generating the report. This option is useful
                      when generating a report for many test results (a diff). If the test results
                      contain different count of datapoints (rows count in the CSV file), the
                      resulting histograms may look a little bit misleading. This option evens up
                      datapoints count in the test results. It just finds the test result with the
                      minimum count of datapoints and ignores the extra datapoints in the other test
                      results."""

# Description for the '--xaxes' option of the 'report' command.
XAXES_DESCR = """A comma-separated list of metrics (or python style regular expressions matching the
                 names) to use on X-axes of the scatter plot(s), default is '%s'. Use
                 '--list-metrics' to get the list of the available metrics. Use value 'none' to
                 disable scatter plots."""

# Description for the '--yaxes' option of the 'report' command.
YAXES_DESCR = """A comma-separated list of metrics (or python style regular expressions matching the
                 names) to use on the Y-axes for the scatter plot(s). If multiple metrics are
                 specified for the X- or Y-axes, then the report will include multiple scatter plots
                 for all the X- and Y-axes combinations. The default is '%s'.  Use '--list-metrics'
                 to get the list of the available metrics. Use value 'none' to disable scatter
                 plots."""

# Description for the '--hist' option of the 'report' command.
HIST_DESCR = """A comma-separated list of metrics (or python style regular expressions matching the
                names) to add a histogram for, default is '%s'. Use '--list-metrics' to get the list
                of the available metrics. Use value 'none' to disable histograms."""

# Description for the '--chist' option of the 'report' command.
CHIST_DESCR = """A comma-separated list of metrics (or python style regular expressions matching the
                 names) to add a cumulative distribution for, default is '%s'. Use '--list-metrics'
                 to get the list of the available metrics. Use value 'none' to disable cumulative
                 histograms."""

# Description for the '--reportids' option of the 'report' command.
REPORTIDS_DESCR = """Every input raw result comes with a report ID. This report ID is basically a
                     short name for the test result, and it used in the HTML report to refer to the
                     test result. However, sometimes it is helpful to temporarily override the
                     report IDs just for the HTML report, and this is what the '--reportids' option
                     does. Please, specify a comma-separated list of report IDs for every input raw
                     test result. The first report ID will be used for the first raw rest result,
                     the second report ID will be used for the second raw test result, and so on.
                     Please, refer to the '--reportid' option description in the 'start' command for
                     more information about the report ID."""

# Description for the '--report-descr' option of the 'report' command.
REPORT_DESCR = """The report description - any text describing this report as whole, or path to a
                  file containing the overall report description. For example, if the report
                  compares platform A and platform B, the description could be something like
                  'platform A vs B comparison'. This text will be included into the very beginning
                  of the resulting HTML report."""

# Description for the '--copy-raw' option of the 'report' command.
COPY_RAW_DESCR = """Copy raw test results to the output directory."""

# Description for the '--list-metrics' option of the 'report' and other commands.
LIST_METRICS_DESCR = "Print the list of the available metrics and exit."

# Description for the 'filter' command.
FILT_DESCR = """Filter datapoints out of a test result by removing CSV rows and metrics according to
                specified criteria. The criteria is specified using the row and metric filter and
                selector options ('--include', '--exclude-metrics', etc). The options may be
                specified multiple times."""

EXCL_DESCR = """Datapoints to exclude: remove all the datapoints satisfying the expression
                'EXCLUDE'."""

# Description for the '--include' option of the 'filter' command.
INCL_DESCR = """Datapoints to include: remove all datapoints except for those satisfying the
                expression 'INCLUDE'. In other words, this option is the inverse of '--exclude'."""

KEEP_FILTERED_DESCR = """If the '--exclude' / '--include' options are used, then the datapoints not
                         matching the selector or matching the filter are discarded. This is the
                         default behavior which can be changed with this option. If
                         '--keep-filtered' has been specified, then all datapoints are saved in
                         result."""

# Description for the '--exclude-metrics' option of the 'filter' command.
MEXCLUDE_DESCR = """The metrics to exclude. Expects a comma-separated list of the metrics or python
                    style regular expressions matching the names. For example, the expression
                    'SilentTime,WarmupDelay,.*Cyc', would remove metrics 'SilentTime', 'WarmupDelay'
                    and all metrics with 'Cyc' in their name. Use '--list-metrics' to get the list
                    of the available metrics."""

# Description for the '--include-metrics' option of the 'filter' command.
MINCLUDE_DESCR = """The metrics to include: remove all metrics except for those specified by this
                    option. The syntax is the same as for '--exclude-metrics'."""

# Description for the '--human-readable' option of the 'filter' command.
FILTER_HUMAN_DESCR = """By default the result 'filter' command print the result as a CSV file to the
                        standard output. This option can be used to dump the result in a more
                        human-readable form."""

# Description for the '--outdir' option of the 'filter' command.
FILTER_OUTDIR_DESCR = """By default the resulting CSV lines are printed to the standard output. But
                         this option can be used to specify the output directly to store the result
                         at. This will create a filtered version of the input test result."""

# Description for the '--reportid' option of the 'filter' command.
FILTER_REPORTID_DESCR = """Report ID of the filtered version of the result (can only be used with
                           '--outdir')."""

# Description for the '--funcs' option of the 'calc' command.
FUNCS_DESCR = """Comma-separated list of summary functions to calculate. By default all generally
                 interesting functions are calculated (each metric is associated with a list of
                 functions that make sense for that metric). Use '--list-funcs' to get the list of
                 supported functions."""

# Description for the '--list-funcs' option of the 'calc' command.
LIST_FUNCS_DESCR = "Print the list of the available summary functions."

def _init_reportid(cmdl: StartCmdlArgsTypedDict):
    """
    Initialize the report ID if it is not specified by the user.

    Args:
        cmdl: The command line arguments dictionary.
    """

    if not cmdl["reportid"] and cmdl["hostname"] != "localhost":
        prefix = cmdl["hostname"]
    else:
        prefix = ""

    strftime = f"{cmdl['toolname']}-{cmdl['devid']}-%Y%m%d"
    cmdl["reportid"] = ReportID.format_reportid(prefix=prefix, reportid=cmdl["reportid"],
                                                strftime=strftime)

def _init_ldist(cmdl: StartCmdlArgsTypedDict, ldist_str: str):
    """
    Parse and intialize the launch distance range.

    Args:
        cmdl: The command line arguments dictionary.
        ldist_str: A string of two comma-separated launch distance values.

    Returns:
        Launch distance range as a tuple of two integers in nanoseconds.
    """

    ldist = Human.parse_human_range(ldist_str, unit="us", target_unit="ns", what="launch distance")
    if ldist[0] < 0 or ldist[1] < 0:
        raise Error(f"Bad launch distance range '{ldist_str}', values cannot be negative")

    cmdl["ldist"] = int(ldist[0]), int(ldist[1])

def format_start_command_args(args: argparse.Namespace, toolname: str) -> StartCmdlArgsTypedDict:
    """
    Build and return a typed dictionary containing the formatted command-line arguments.

    Args:
        args: The command-line arguments.
        toolname: Name of the tool.

    Returns:
        StartCmdlArgsTypedDict: A typed dictionary containing the formatted arguments.
    """

    if typing.TYPE_CHECKING:
        cmdl = cast(StartCmdlArgsTypedDict, ArgParse.format_ssh_args(args))
    else:
        cmdl = ArgParse.format_ssh_args(args)

    cmdl["toolname"] = toolname
    cmdl["reportid"] = getattr(args, "reportid", "")
    cmdl["devid"] = args.devid

    _init_reportid(cmdl)

    if getattr(args, "outdir", ""):
        cmdl["outdir"] = args.outdir
    else:
        cmdl["outdir"] = Path(f"./{cmdl['reportid']}")

    _init_ldist(cmdl, args.ldist)

    return cmdl

def get_pman(args):
    """
    Return the process manager object for host 'hostname'. The arguments are as follows.
      * args - the command line arguments object.

    The returned object should either be used with the 'with' statement, or closed with the
    'close()' method.
    """

    cmdl = ArgParse.format_ssh_args(args)
    return ProcessManager.get_pman(cmdl["hostname"], cmdl["username"],
                                   privkeypath=cmdl["privkey"], timeout=cmdl["timeout"])

def even_up_dpcnt(rsts):
    """
    Implement the '--even-up-datapoints' option. The arguments are as follows.
      * rsts -  a list of 'RORawResult' objects to even up datapoints count in.

    Truncate datapoints count in 'rsts' to the size of the smallest test result, where "size" is
    defined as the count of rows in the CSV file.
    """

    # Find test with the smallest CSV file. It should be a good approximation for the smallest test
    # result, ant it will be corrected as we go.
    min_size = min_res = None
    for res in rsts:
        try:
            size = res.dp_path.stat().st_size
        except OSError as err:
            errmsg = Error(str(err)).indent(2)
            raise Error(f"'stat()' failed for '{res.dp_path}':\n{errmsg}") from None
        if min_size is None or size < min_size:
            min_size = size
            min_res = res

    min_res.load_df()
    min_dpcnt = len(min_res.df.index)

    # Load only 'min_dpcnt' datapoints for every test result, correcting 'min_dpcnt' as we go.
    for res in rsts:
        res.load_df(nrows=min_dpcnt)
        min_dpcnt = min(min_dpcnt, len(res.df.index))

    # And in case our initial 'min_dpcnt' estimation was incorrect, truncate all the results to the
    # final 'min_dpcnt'.
    for res in rsts:
        dpcnt = len(res.df.index)
        if dpcnt > min_dpcnt:
            res.df = res.df.truncate(after=min_dpcnt - 1)

def set_filters(args, res):
    """
    Implement the following command-line options: '--include', '--exclude', '--include-metrics',
    '--exclude-metrics'. The arguments are as follows.
      * args - the command line arguments object.
      * res - a 'RORawResult' or 'WORawResult' object to set filters for.
    """

    def set_filter(res, ops):
        """Set filter operations in 'ops' to test result 'res'."""

        res.clear_filts()
        for name, expr in ops.items():
            # The '--include-metrics' and '--exclude-metrics' options may have comma-separated list
            # of metrics.
            if name in ("minclude", "mexclude"):
                expr = Trivial.split_csv_line(expr)
            getattr(res, f"set_{name}")(expr)

    if not getattr(args, "oargs", None):
        return

    set_filter(res, args.oargs)
    keep_filtered = getattr(args, "keep_filtered", None)
    setattr(res, "keep_filtered", keep_filtered)

def apply_filters(args, res):
    """
    Set and apply filters. The arguments are as follows.
      * args - the command line arguments object.
      * res - a 'RORawResult' or 'WORawResult' object to set and apply filters for.
    """

    set_filters(args, res)
    res.load_df()

def scan_command(args: argparse.Namespace, deploy_info: DeployInfoTypedDict):
    """
    Implement 'wult scan' command.

    Args:
        args: The command-line arguments.
        deploy_info: The deployment information dictionary, used for checking the tool deployment.
    """

    pman = get_pman(args)

    found_something = False
    supported_msgs = unsupported_msgs = ""

    for dev in Devices.scan_devices(args.toolname, pman):
        err_msg = None
        found_something = True

        deploy_info = reduce_installables(deploy_info, dev)
        with _Deploy.DeployCheck("wult", args.toolname, deploy_info, pman=pman) as depl:
            try:
                depl.check_deployment()
            except (ErrorNotFound, ErrorNotSupported) as err:
                if not getattr(args, "all", False):
                    _LOG.debug(err)
                    continue
                err_msg = str(err)

        msg = f"* Device ID: {dev.info['devid']}\n"
        if dev.info.get("alias"):
            msg += f"   - Alias: {dev.info['alias']}\n"
        if err_msg:
            # The error message may include newlines, align them to match our indentation.
            err_msg = err_msg.replace("\n", "\n            ")
            msg += f"   - Error: {err_msg}\n"
        msg += f"   - Resolution: {dev.info['resolution']} ns\n"
        msg += f"   - Description: {dev.info['descr']}\n"

        if err_msg:
            unsupported_msgs += msg
        else:
            supported_msgs += msg

    if not supported_msgs and not unsupported_msgs:
        if not found_something:
            _LOG.info("No %s compatible devices found", args.toolname)
        else:
            _LOG.info("There are compatible devices, but they are not supported by the current %s "
                      "installation", args.toolname)
        return

    if supported_msgs:
        _LOG.info("Compatible and supported device(s)%s:", pman.hostmsg)
        _LOG.info("%s", supported_msgs.strip())
    if unsupported_msgs:
        if supported_msgs:
            _LOG.info("")
        _LOG.info("Compatible, but unsupported device(s)%s:", pman.hostmsg)
        _LOG.info("%s", unsupported_msgs.strip())

def filter_command(args):
    """
    Implement the 'filter' command for the 'wult' and 'ndl' tools. The arguments are as follows.
      * args - the command line arguments object.
    """

    # pylint: disable=import-outside-toplevel
    from wultlibs.result import RORawResult

    res = RORawResult.RORawResult(args.respath)

    if args.list_metrics:
        list_result_metrics([res])
        return

    if not getattr(args, "oargs", None):
        raise Error("please, specify at least one reduction criterion")
    if args.reportid and not args.outdir:
        raise Error("'--reportid' can be used only with '-o'/'--outdir'")

    if args.human_readable and args.outdir:
        raise Error("'--human-readable' and '--outdir' are mutually exclusive")

    apply_filters(args, res)

    if args.outdir:
        res.save(args.outdir, reportid=args.reportid)
    elif not args.human_readable:
        res.df.to_csv(sys.stdout, index=False, header=True)
    else:
        for idx, (_, dp) in enumerate(res.df.iterrows()):
            if idx > 0:
                _LOG.info("")
            _LOG.info(Human.dict2str(dict(dp)))

def calc_command(args):
    """
    Implement the 'calc' command for the 'wult' and 'ndl' tools. The arguments are as follows.
      * args - the command line arguments object.
    """

    # pylint: disable=import-outside-toplevel

    if args.list_funcs:
        from statscollectlibs import DFSummary

        for name, descr in DFSummary.get_smry_funcs():
            _LOG.info("%s: %s", name, descr)
        return

    from wultlibs.result import RORawResult

    if args.funcs:
        funcnames = Trivial.split_csv_line(args.funcs)
    else:
        funcnames = None

    res = RORawResult.RORawResult(args.respath)

    if args.list_metrics:
        list_result_metrics([res])
        return

    apply_filters(args, res)

    non_numeric = res.get_non_numeric_metrics()
    if non_numeric:
        minclude = mexclude = []
        if args.minclude:
            minclude = set(Trivial.split_csv_line(args.minclude))
        if args.mexclude:
            mexclude = set(Trivial.split_csv_line(args.mexclude))
        skip = []

        for metric in non_numeric:
            if metric in minclude or metric in mexclude:
                skip.append(metric)

        if skip:
            _LOG.warning("skipping non-numeric metric(s): %s", ", ".join(skip))

    res.calc_smrys(funcnames=funcnames)

    _LOG.info("Datapoints count: %d", len(res.df))
    YAML.dump(res.smrys, sys.stdout, float_format="%.2f")

def open_raw_results(respaths, toolname, reportids=None):
    """
    Open the input raw test results and return the list of 'RORawResult' objects. The arguments are
    as follows.
      * respaths - list of paths to raw results.
      * toolname - name of the tool opening raw results.
      * reportids - list of reportids to override report IDs in raw results.
    """

    # pylint: disable=import-outside-toplevel
    from wultlibs.result import RORawResult

    if reportids:
        reportids = Trivial.split_csv_line(reportids)
    else:
        reportids = []

    if len(reportids) > len(respaths):
        raise Error(f"there are {len(reportids)} report IDs to assign to {len(respaths)} input "
                    f"test results. Please, provide {len(respaths)} or fewer report IDs.")

    # Append the required amount of 'None's to make the 'reportids' list be of the same length as
    # the 'respaths' list.
    reportids += [None] * (len(respaths) - len(reportids))

    rsts = []
    for respath, reportid in zip(respaths, reportids):
        if reportid:
            ReportID.validate_reportid(reportid)

        res = RORawResult.RORawResult(respath, reportid=reportid)
        if toolname != res.info["toolname"]:
            raise Error(f"cannot generate '{toolname}' report, results are collected with the"
                        f"'{res.info['toolname']}':\n{respath}")
        rsts.append(res)

    from statscollectlibs.result import RORawResult as StatsCollectRORawResult

    StatsCollectRORawResult.reportids_dedup(rsts)

    return rsts

def list_result_metrics(rsts):
    """
    Implement the '--list-metrics' option by printing the metrics for each raw result 'rsts'. The
    arguments are as follows.
      * rsts - an iterable collection of test results to print the metrics for.
    """

    for res in rsts:
        _LOG.info("Metrics in '%s':", res.dirpath)
        for metric in res.metrics:
            if metric in res.mdo.mdd:
                _LOG.info("  * %s: %s", metric, res.mdo.mdd[metric]["title"])

def reduce_installables(deploy_info, dev):
    """
    Reduce full deployment information 'deploy_info' so that it includes only the installables
    required for using device 'dev'. The arguments are as follows.
      * deploy_info - full deployment information dictionary. Check the 'DeployBase.__init__()'
                      docstring for the format of the dictionary.
      * dev - the device object created by 'Devices.GetDevice()'.

    Return the reduced version of 'deploy_info'.
    """

    # Copy the original dictionary, 2 levels are enough.
    result = {}
    for key, value in deploy_info.items():
        result[key] = value.copy()

    for installable, info in deploy_info["installables"].items():
        if info["category"] == "drivers" and not dev.drvname:
            del result["installables"][installable]
        elif info["category"] in ("shelpers",) and not dev.helpername:
            del result["installables"][installable]

    return result

def start_command_check_network(args, pman, netif):
    """
    In case the device that is used for measurement is a network card, check that it is not in the
    'up' state. This makes sure users do not lose networking by specifying a wrong device by a
    mistake. The arguments are as follows.
      * args - the command line arguments object.
      * pman - the process manager object that defines the host to measure.
      * netif - the network interface object ('NetIface.NetIface()') that will be used for measuring
                the host.
    """

    if args.force:
        return

    # Make sure the device is not used for networking and users do not lose networking by
    # specifying a wrong device by a mistake.
    if netif.get_operstate() == "up":
        msg = ""
        if args.devid != netif.ifname:
            msg = f" (network interface '{netif.ifname}')"

        raise Error(f"refusing to use device '{args.devid}'{msg}{pman.hostmsg}: it is up and "
                    f"might be used for networking. Please, bring it down if you want to use "
                    "it for measurements.")

def start_command_list_stats():
    """Implement the '--list-stats' command line option."""

    # pylint: disable=import-outside-toplevel
    from statscollectlibs.collector import StatsCollect

    StatsCollect.list_stats()

def report_command_outdir(args, rsts):
    """
    Return the default or user-provided output directory path for the 'report' command. The
    arguments are as follows.
      * args - the command line arguments object.
      * rsts -  a list of 'RORawResult' objects to return the output directory for.
    """

    if args.outdir is not None:
        return args.outdir

    if len(args.respaths) > 1:
        outdir = ReportID.format_reportid(prefix=f"{args.toolname}-report",
                                          reportid=rsts[0].reportid)
    else:
        outdir = args.respaths[0]
        # Don't create report in results directory, use 'html-report' subdirectory instead.
        outdir = outdir.joinpath("html-report")

    _LOG.info("Report output directory: %s", outdir)
    return Path(outdir)

def check_aspm_setting(pman, dev, devname):
    """
    If PCI ASPM is enabled for a device, print a notice message. The arguments are as follows.
      * dev - the delayed event device object created by 'Devices.GetDevice()'.
      * pman - the process manager object for the target system.
      * devname - the device name to use in the message.
    """

    if not dev.is_pci:
        return

    with ASPM.ASPM(pman=pman) as aspm:
        if aspm.is_l1_enabled(dev.info["devid"]):
            _LOG.notice("PCI L1 ASPM is enabled for %s, and this typically increases the measured "
                        "latency", devname)

def configure_log_file(outdir: Path, toolname: str) -> Path:
    """
    Configure the logger to mirror all the standard output and standard error a log file.

    Args:
        outdir: the log file directory.
        toolname: name of the tool to use in the log file name.

    Returns:
        Path: the path to the log file.
    """

    try:
        outdir.mkdir(parents=True, exist_ok=True)
    except OSError as err:
        errmsg = Error(str(err)).indent(2)
        raise Error(f"Cannot create log directory '{outdir}':\n{errmsg}") from None

    logpath = Path(outdir) / f"{toolname}.log.txt"
    contents = f"Command line: {' '.join(sys.argv)}\n"
    logger = Logging.getLogger(Logging.MAIN_LOGGER_NAME)
    logger.configure_log_file(logpath, contents=contents)

    return logpath
