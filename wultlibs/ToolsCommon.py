# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module contains miscellaneous functions used by the 'wult' and 'ndl' tools. There is really no
single clear purpose this module serves, it is just a collection of shared code. Many functions in
this module require the  'args' object which represents the command-line arguments.
"""

# pylint: disable=no-member

import sys
import logging
from pathlib import Path
from pepclibs.helperlibs import Trivial, ProcessManager, Logging, YAML
from pepclibs.helperlibs.Exceptions import Error
from wultlibs import DFSummary, Devices
from wultlibs.helperlibs import ReportID, Human
from wultlibs.rawresultlibs import RORawResult

HELPERS_LOCAL_DIR = Path(".local")
_DRV_SRC_SUBPATH = Path("drivers/idle")
_HELPERS_SRC_SUBPATH = Path("helpers")

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
                       The default unit is minutes, but you can use the following handy specifiers
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

# Description for the '--force' option of the 'start' command.
START_FORCE_DESCR = """By default a network card is not accepted as a measurement device if it is "
                       used by a Linux network interface and the interface is in an active state, "
                       such as "up". Use '--force' to disable this safety mechanism. Use it with "
                       caution."""

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

# Description for the '--even-up-dp-count' option of the 'report' command.
EVEN_UP_DP_DESCR = """Even up datapoints count before generating the report. This option is useful
                      when generating a report for many test results (a diff). If the test results
                      contain different count of datapoints (rows count in the CSV file), the
                      resulting histograms may look a little bit misleading. This option evens up
                      datapoints count in the test results. It just finds the test result with the
                      minimum count of datapoints and ignores the extra datapoints in the other test
                      results."""

# Description for the '--xaxes' option of the 'report' command.
XAXES_DESCR = """A comma-separated list of CSV column names (or python style regular expressions
                 matching the names) to use on X-axes of the scatter plot(s), default is '%s'. Use
                 '--list-metrics' to get the list of the available metrics. Use value 'none' to
                 disable scatter plots."""

# Description for the '--yaxes' option of the 'report' command.
YAXES_DESCR = """A comma-separated list of CSV column names (or python style regular expressions
                 matching the names) to use on the Y-axes for the scatter plot(s). If multiple CSV
                 column names are specified for the X- or Y-axes, then the report will include
                 multiple scatter plots for all the X- and Y-axes combinations. The default is '%s'.
                 Use '--list-metrics' to get the list of the available metrics. se value 'none' to
                 disable scatter plots."""

# Description for the '--hist' option of the 'report' command.
HIST_DESCR = """A comma-separated list of CSV column names (or python style regular expressions
                matching the names) to add a histogram for, default is '%s'. Use '--list-metrics' to
                get the list of the available metrics. Use value 'none' to disable histograms.
                """

# Description for the '--chist' option of the 'report' command.
CHIST_DESCR = """A comma-separated list of CSV column names (or python style regular expressions
                 matching the names) to add a cumulative distribution for, default is '%s'. Use
                 '--list-metrics' to get the list of the available metrics. Use value 'none' to
                 disable cumulative histograms."""

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

# Description for the '--title-descr' option of the 'report' command.
TITLE_DESCR = """The report title description - any text describing this report as whole, or path to
                 a file containing the overall report description. For example, if the report
                 compares platform A and platform B, the description could be something like
                 'platform A vs B comparison'. This text will be included into the very beginning of
                 the resulting HTML report."""

# Description for the '--relocatable' option of the 'report' command.
RELOCATABLE_DESCR = """Generate a report which contains a copy of the raw test results. With this
                       option, viewers of the report will be able to browse raw logs and statistics
                       files which are copied across with the raw test results."""

# Description for the '--list-metrics' option of the 'report' and other commands.
LIST_METRICS_DESCR = "Print the list of the available metrics and exit."

# Description for the 'filter' command.
FILT_DESCR = """Filter datapoints out of a test result by removing CSV rows and metrics according to
                specified criteria. The criteria is specified using the row and metric filter and
                selector options ('--rsel', '--exclude-metrics', etc). The options may be specified multiple
                times."""

_RFILT_DESCR_BASE = """The row filter: remove all the rows satisfying the filter expression. Here is
                       an example of an expression: '(WakeLatency < 10000) | (PC6%% < 1)'. This row
                       filter expression will remove all rows with 'WakeLatency' smaller than 10000
                       nanoseconds or package C6 residency smaller than 1%%."""

# Description for the '--rfilt' option of the 'start' command.
RFILT_START_DESCR = f"""{_RFILT_DESCR_BASE} You can use any column names in the expression."""

# Description for the '--rfilt' option of the 'filter' command.
RFILT_DESCR = f"""{_RFILT_DESCR_BASE} The detailed row filter expression syntax can be found in the
                  documentation for the 'eval()' function of Python 'pandas' module. You can use
                  column names in the expression, or the special word 'index' for the row number.
                  Value '0' is the header, value '1' is the first row, and so on. For example,
                  expression 'index >= 10' will get rid of all data rows except for the first 10
                  ones."""

# Description for the '--rsel' option of the 'filter' command.
RSEL_DESCR = """The row selector: remove all rows except for those satisfying the selector
                expression. In other words, the selector is just an inverse filter: '--rsel expr' is
                the same as '--rfilt "not (expr)"'."""

KEEP_FILTERED_DESCR = """If the '--rfilt' / '--rsel' options are used, then the datapoints not
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

# Description for the '--csel' option of the 'filter' command.
CSEL_DESCR = """The columns selector: remove all column except for those specified in the selector.
                The syntax is the same as for '--exclude-metrics'."""

# Discription for the '--human-readable' option of the 'filter' command.
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
                 interesting functions are calculated (each column name is associated with a list of
                 functions that make sense for this column). Use '--list-funcs' to get the list of
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

    if len(vals) == 2 and vals[1] - vals[0] < 0:
        raise Error(f"bad {what} range '{rng}', first number cannot be greater than the second "
                    f"number")
    if len(vals) == 1:
        vals.append(vals[0])

    return vals

def setup_stdout_logging(toolname, logs_path):
    """
    Configure the logger to mirror all stdout and stderr messages to the log file in the 'logs_path'
    directory.
    """

    # Configure the logger to print to both the console and the log file.
    try:
        logs_path.mkdir(exist_ok=True)
    except OSError as err:
        raise Error(f"cannot create log directory '{logs_path}': {err}") from None
    logfile = logs_path / f"{toolname}.log.txt"

    try:
        with logfile.open("w+") as fobj:
            fobj.write(f"Command line: {' '.join(sys.argv)}\n")
    except OSError as err:
        raise Error("failed to write command line to '{logfile}':\n{err}") from None

    Logging.setup_logger(toolname, info_logfile=logfile, error_logfile=logfile)

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
            raise Error(f"'stat()' failed for '{res.dp_path}': {err}") from None
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
    This is a helper function for the following command-line options: '--rsel', '--rfilt', '--csel',
    '--exclude-metrics'. The 'args' argument should be an 'helperlibs.ArgParse' object, where all
    the above mentioned options are represented by the 'oargs' (ordered arguments) field. The 'res'
    argument is 'RORawResult' or 'WORawResultBase' object.
    """

    def set_filter(res, ops):
        """Set filter operations in 'ops' to test result 'res'."""

        res.clear_filts()
        for name, expr in ops.items():
            # The '--csel' and '--exclude-metrics' options may have comma-separated list of metrics.
            if name in ("csel", "mexclude"):
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

    msg = ""
    for info in Devices.scan_devices(args.toolname, pman):
        msg += f" * Device ID: {info['devid']}\n"
        if info["alias"]:
            msg += f"   - Alias: {info['alias']}\n"
        msg += f"   - Resolution: {info['resolution']} ns\n"
        msg += f"   - Description: {info['descr']}\n"

    if not msg:
        _LOG.info("No %s compatible devices found", args.toolname)
        return

    _LOG.info("Compatible device(s)%s:\n%s", pman.hostmsg, msg.rstrip())

def filter_command(args):
    """Implements the 'filter' command for the 'wult' and 'ndl' tools."""

    res = RORawResult.RORawResult(args.respath)

    if args.list_metrics:
        for colname in res.metrics:
            _LOG.info("%s: %s", colname, res.defs.info[colname]["title"])
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
        for name, descr in DFSummary.get_smry_funcs():
            _LOG.info("%s: %s", name, descr)
        return

    if args.funcs:
        funcnames = Trivial.split_csv_line(args.funcs)
        all_funcs = True
    else:
        funcnames = None
        all_funcs = False

    res = RORawResult.RORawResult(args.respath)
    apply_filters(args, res)

    non_numeric = res.get_non_numeric_metrics()
    if non_numeric and (args.csel or args.mexclude):
        non_numeric = ", ".join(non_numeric)
        _LOG.warning("skipping non-numeric column(s): %s", non_numeric)

    res.calc_smrys(funcnames=funcnames, all_funcs=all_funcs)

    _LOG.info("Datapoints count: %d", len(res.df))
    YAML.dump(res.smrys, sys.stdout, float_format="%.2f")

def open_raw_results(respaths, toolname, reportids=None):
    """
    Opens the input raw test results, and returns the list of 'RORawResult' objects.
      * respaths - list of paths to raw results.
      * toolname - name of the tool opening raw results.
      * reportids - list of reportids to override report IDs in raw results.
    """

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
    if netif.getstate() == "up":
        msg = ""
        if args.devid != netif.ifname:
            msg = f" (network interface '{netif.ifname}')"

        raise Error(f"refusing to use device '{args.devid}'{msg}{pman.hostmsg}: it is up and "
                    f"might be used for networking. Please, bring it down if you want to use "
                    "it for measurements.")


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
