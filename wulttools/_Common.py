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

# pylint: disable=no-member

import sys
import logging
from pathlib import Path
from pepclibs.helperlibs import Trivial, YAML, ProcessManager
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
from wultlibs import Devices
from wultlibs.deploylibs import _Deploy
from wultlibs.helperlibs import Human
from statscollectlibs.helperlibs import ReportID
from statscollectlibs.collector import StatsCollectBuilder

_LOG = logging.getLogger()

# By default 'ReportID' module does not allow for the ":" character, but it is part of the PCI
# address, and we allow for PCI addresses as device IDs. Here are few constants that we use to
# extend the default allowed report ID characters set.
_REPORTID_ADDITIONAL_CHARS = ":"

# Description for the '--datapoints' option of the 'start' command.
DATAPOINTS_DESCR = """How many datapoints should the test result include, default is 1000000. Note,
                      unless the '--start-over' option is used, the pre-existing datapoints are
                      taken into account. For example, if the test result already has 6000
                      datapoints and '-c 10000' is used, the tool will collect 4000 datapoints and
                      exit. Warning: collecting too many datapoints may result in a very large test
                      result file, which will be difficult to process later, because that would
                      require a lot of memory."""

# Description for the '--time-limit' option of the 'start' command.
TIME_LIMIT_DESCR = f"""The measurement time limit, i.e., for how long the SUT should be measured.
                       The default unit is minute, but you can use the following handy specifiers
                       as well: {Human.DURATION_SPECS_DESCR}. For example '1h25m' would be 1 hour
                       and 25 minutes, or 10m5s would be 10 minutes and 5 seconds. Value '0' means
                       "no time limit", and this is the default. If this option is used along with
                       the '--datapoints' option, then measurements will stop as when either the
                       time limit is reached, or the required amount of datapoints is collected."""

# Description for the '--start-over' option of the 'start' command.
START_OVER_DESCR = """If the output directory already contains the datapoints CSV file with some
                      amount of datapoints in it, the default behavior is to keep them and append
                      more datapoints if necessary. But with this option all the pre-existing
                      datapoints will be removed as soon as the tool starts writing new
                      datapoints."""

# Description for the '--outdir' option of the 'start' command.
START_OUTDIR_DESCR = """Path to the directory to store the results at."""

_REPORTID_CHARS_DESCR = ReportID.get_charset_descr(additional_chars=_REPORTID_ADDITIONAL_CHARS)
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
STATS_DESCR = f"""Comma-separated list of statistics to collect. The statistics are collected in
                  parallel with measuring C-state latency. They are stored in the the "stats"
                  sub-directory of the output directory. By default, only '{default_stnames}'
                  statistics are collected. Use 'all' to collect all possible statistics. Use
                  '--stats=""' or '--stats="none"' to disable statistics collection. If you know
                  exactly what statistics you need, specify the comma-separated list of statistics
                  to collect. For example, use 'turbostat,acpower' if you need only turbostat and AC
                  power meter statistics. You can also specify the statistics you do not want to be
                  collected by pre-pending the '!' symbol. For example, 'all,!turbostat' would mean:
                  collect all the statistics supported by the SUT, except for 'turbostat'. Use the
                  '--list-stats' option to get more information about available statistics. By
                  default, only 'sysinfo' statistics are collected."""

# Description for the '--stat-intervals' option of the 'start' command.
STAT_INTERVALS_DESCR =  """The intervals for statistics. Statistics collection is based on doing
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
    Returns description for the '--outdir' option of the 'report' command for the 'toolname' tool.
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
    Returns description for the '--all' option of the 'scan' command for the 'toolname' tool.
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

# Description for the '--relocatable' option of the 'report' command.
RELOCATABLE_DESCR = """Generate a report which contains a copy of the raw test results. With this
                       option, viewers of the report will also be able to browse raw statistics
                       files which are copied across with the raw test results."""

# Description for the '--list-metrics' option of the 'report' and other commands.
LIST_METRICS_DESCR = "Print the list of the available metrics and exit."

# Description for the 'filter' command.
FILT_DESCR = """Filter datapoints out of a test result by removing CSV rows and metrics according to
                specified criteria. The criteria is specified using the row and metric filter and
                selector options ('--include', '--exclude-metrics', etc). The options may be
                specified multiple times."""

_EXCL_DESCR_BASE = """Datapoints to exclude: remove all the datapoints satisfying the expression
                      'EXCLUDE'. Here is an example of an expression: '(WakeLatency < 10000) |
                      (PC6%% < 1)'. This filter expression will remove all datapoints with
                      'WakeLatency' smaller than 10000 nanoseconds or package C6 residency smaller
                      than 1%%."""

# Description for the '--exclude' option of the 'start' command.
EXCL_START_DESCR = f"""{_EXCL_DESCR_BASE} You can use any metrics in the expression."""

# Description for the '--exclude' option of the 'filter' command.
EXCL_DESCR = f"""{_EXCL_DESCR_BASE} The detailed expression syntax can be found in the documentation
                 for the 'eval()' function of Python 'pandas' module. You can use metrics in the
                 expression, or the special word 'index' for the row number (0-based index) of a
                 datapoint in the results. For example, expression 'index >= 10' will get rid of all
                 datapoints except for the first 10 ones."""

# Description for the '--include' option of the 'filter' command.
INCL_DESCR = """Datapoints to include: remove all datapoints except for those satisfying the
                expression 'INCLUDE'. In other words, this option is the inverse of '--exclude'.
                This means, '--include expr' is the same as '--exclude "not (expr)"'."""

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

def get_pman(args):
    """
    Returns the process manager object for host 'hostname'. The returned object should either be
    used with a 'with' statement, or closed with the 'close()' method.
    """

    if args.hostname == "localhost":
        username = privkeypath = timeout = None
    else:
        username = args.username
        privkeypath = args.privkey
        timeout = args.timeout

    return ProcessManager.get_pman(args.hostname, username=username, privkeypath=privkeypath,
                                   timeout=timeout)

def _validate_range(rng, what, single_ok):
    """Implements 'parse_ldist()'."""

    if single_ok:
        min_len = 1
    else:
        min_len = 2

    split_rng = Trivial.split_csv_line(rng)

    if len(split_rng) < min_len:
        raise Error(f"bad {what} range '{rng}', it should include {min_len} numbers")
    if len(split_rng) > 2:
        raise Error(f"bad {what} range '{rng}', it should not include more than 2 numbers")

    vals = [None] * len(split_rng)

    for idx, val in enumerate(split_rng):
        vals[idx] = Human.parse_duration_ns(val, default_unit="us", name=what)
        if vals[idx] < 0:
            raise Error(f"bad {what} value '{split_rng[idx]}', should be greater than zero")

    if len(vals) == 2:
        if vals[1] - vals[0] < 0:
            raise Error(f"bad {what} range '{rng}', first number cannot be greater than the second "
                        f"number")
        if not single_ok and vals[0] == vals[1]:
            raise Error(f"bad {what} range '{rng}', first number cannot be the same as the second "
                        f"number")
    if len(vals) == 1:
        vals.append(vals[0])

    return vals

def parse_ldist(ldist, single_ok=True):
    """
    Parse and validate the launch distance range ('--ldist' option). The 'ldist' argument is a
    string of single or two comma-separated launch distance values. The values are parsed with
    'Human.parse_duration_ns()', so they can include specifiers like 'ms' or 'us'. Returns launch
    launch distance range as a list of two integers in nanoseconds.

    My default, 'ldist' may include a single number, but if 'single_ok' is 'False', then this
    function will raise the exception in case there is only one number.
    """

    return _validate_range(ldist, "launch distance", single_ok)

def even_up_dpcnt(rsts):
    """
    This is a helper function for the '--even-up-datapoints' option. It takes a list of
    'RORawResult' objects ('rsts') and truncates them to the size of the smallest test result, where
    "size" is defined as the count of rows in the CSV file.
    """

    # Find test with the smallest CSV file. It should be a good approximation for the smallest test
    # result, ant it will be corrected as we go.
    min_size = min_res = None
    for res in rsts:
        try:
            size = res.dp_path.stat().st_size
        except OSError as err:
            msg = Error(err).indent(2)
            raise Error(f"'stat()' failed for '{res.dp_path}':\n{msg}") from None
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
            res.df = res.df.truncate(after=min_dpcnt-1)

def set_filters(args, res):
    """
    This is a helper function for the following command-line options: '--include', '--exclude',
    '--include-metrics', '--exclude-metrics'. The 'args' argument should be an 'helperlibs.ArgParse'
    object, where all the above mentioned options are represented by the 'oargs' (ordered arguments)
    field.  The 'res' argument is 'RORawResult' or 'WORawResult' object.
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
    Same as 'set_filters()' but filters are also applied to results in 'res'. The 'res' argument is
    'RORawResult'.
    """

    set_filters(args, res)
    res.load_df()

def scan_command(args):
    """Implements the 'scan' command for the 'wult' and 'ndl' tools."""

    pman = get_pman(args)

    found_something = False
    supported_msgs = unsupported_msgs = ""

    for dev in Devices.scan_devices(args.toolname, pman):
        err_msg= None
        found_something = True

        deploy_info = reduce_installables(args.deploy_info, dev)
        with _Deploy.DeployCheck("wult", args.toolname, deploy_info, pman=pman) as depl:
            try:
                depl.check_deployment()
            except ErrorNotFound as err:
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
            _LOG.info("There are compatible devices, but they are not supported by current %s "
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
    """Implements the 'filter' command for the 'wult' and 'ndl' tools."""

    from wultlibs.rawresultlibs import RORawResult # pylint: disable=import-outside-toplevel

    res = RORawResult.RORawResult(args.respath)

    if args.list_metrics:
        list_result_metrics([res])
        return

    if not getattr(args, "oargs", None):
        raise Error("please, specify at least one reduction criteria.")
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
    """Implements the 'calc' command  for the 'wult' and 'ndl' tools."""

    if args.list_funcs:
        from statscollectlibs import DFSummary # pylint: disable=import-outside-toplevel

        for name, descr in DFSummary.get_smry_funcs():
            _LOG.info("%s: %s", name, descr)
        return

    from wultlibs.rawresultlibs import RORawResult # pylint: disable=import-outside-toplevel

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
    Opens the input raw test results, and returns the list of 'RORawResult' objects.
      * respaths - list of paths to raw results.
      * toolname - name of the tool opening raw results.
      * reportids - list of reportids to override report IDs in raw results.
    """

    from wultlibs.rawresultlibs import RORawResult # pylint: disable=import-outside-toplevel

    if reportids:
        reportids = Trivial.split_csv_line(reportids)
    else:
        reportids = []

    if len(reportids) > len(respaths):
        raise Error(f"there are {len(reportids)} report IDs to assign to {len(respaths)} input "
                    f"test results. Please, provide {len(respaths)} or less report IDs.")

    # Append the required amount of 'None's to make the 'reportids' list be of the same length as
    # the 'respaths' list.
    reportids += [None] * (len(respaths) - len(reportids))

    rsts = []
    for respath, reportid in zip(respaths, reportids):
        if reportid:
            ReportID.validate_reportid(reportid, additional_chars=_REPORTID_ADDITIONAL_CHARS)

        res = RORawResult.RORawResult(respath, reportid=reportid)
        if toolname != res.info["toolname"]:
            raise Error(f"cannot generate '{toolname}' report, results are collected with the"
                        f"'{res.info['toolname']}':\n{respath}")
        rsts.append(res)

    return rsts

def list_result_metrics(rsts):
    """
    Implements the '--list-metrics' option by printing the metrics for each raw result 'rsts'.
    """

    for rst in rsts:
        _LOG.info("Metrics in '%s':", rst.dirpath)
        for metric in rst.metrics:
            if metric in rst.defs.info:
                _LOG.info("  * %s: %s", metric, rst.defs.info[metric]["title"])

def reduce_installables(deploy_info, dev):
    """
    Reduce full deployment information 'deploy_info' so that it includes only the installables
    required for using device 'dev'. The arguments are as follows.
      * deploy_info - full deployment information dictionary. Check the 'DeployBase.__init__()'
                      docstring for the format of the dictionary.
      * dev - the device object created by 'Devices.GetDevice()'.

    Returns the reduced version of 'deploy_info'.
    """

    # Copy the original dictionary, 2 levels are enough.
    result = {}
    for key, value in deploy_info.items():
        result[key] = value.copy()

    for installable, info in deploy_info["installables"].items():
        if info["category"] == "drivers" and not dev.drvname:
            del result["installables"][installable]
        elif info["category"] in ("shelpers", "bpfhelpers") and not dev.helpername:
            del result["installables"][installable]

    return result

def start_command_reportid(args, pman):
    """
    If user provided report ID for the 'start' command, this function validates it and returns.
    Otherwise, it generates the default report ID and returns it.
    """

    if not args.reportid and pman.is_remote:
        prefix = pman.hostname
    else:
        prefix = None

    return ReportID.format_reportid(prefix=prefix, reportid=args.reportid,
                                    strftime=f"{args.toolname}-{args.devid}-%Y%m%d",
                                    additional_chars=_REPORTID_ADDITIONAL_CHARS)

def start_command_check_network(args, pman, netif):
    """
    In case the device that is used for measurement is a network card, check that it is not in the
    'up' state. This makes sure users do not lose networking by specifying a wrong device by a
    mistake.
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
    """
    This helper handles the '--list-stats' command line option and print information about
    statistics.
    """

    from statscollectlibs.collector import StatsCollect # pylint: disable=import-outside-toplevel

    for stname in StatsCollect.get_stnames():
        stinfo = StatsCollect.get_stinfo(stname)

        _LOG.info("* %s", stname)
        if stinfo.get("interval"):
            _LOG.info("  - Default interval: %.1fs", stinfo["interval"])
        _LOG.info("  - %s", stinfo["description"])

def report_command_outdir(args, rsts):
    """Return the default or user-provided output directory path for the 'report' command."""

    if args.outdir is not None:
        return args.outdir

    if len(args.respaths) > 1:
        outdir = ReportID.format_reportid(prefix=f"{args.toolname}-report",
                                          reportid=rsts[0].reportid,
                                          additional_chars=_REPORTID_ADDITIONAL_CHARS)
    else:
        outdir = args.respaths[0]

    _LOG.info("Report output directory: %s", outdir)
    return Path(outdir)

def run_stats_collect_deploy(args):
    """Run the 'stats-collect deploy' command."""

    # pylint: disable=import-outside-toplevel
    from pepclibs.helperlibs import ProjectFiles, LocalProcessManager

    exe_path = ProjectFiles.find_project_helper("stat-collect", "stats-collect")

    cmd = str(exe_path)

    if _LOG.colored:
        cmd += " --force-color deploy"
    else:
        cmd += " deploy"

    if args.debug:
        cmd += " -d"
    if args.quiet:
        cmd += " -q"

    if args.hostname != "localhost":
        cmd += f" -H {args.hostname}"
        if args.username:
            cmd += f" -U {args.username}"
        if args.privkey:
            cmd += f" -K {args.privkey}"
        if args.timeout:
            cmd += f" -T {args.timeout}"

    with LocalProcessManager.LocalProcessManager() as lpman:
        try:
            lpman.run_verify(cmd)
        except Error as stderr:
            _LOG.notice(f"the statistics collection capability will not be available for "
                        f"'{args.toolname}'")
            _LOG.debug(stderr)
