# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2020 Intel Corporation
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
from wultlibs import Devices
from wultlibs.helperlibs import Trivial, ReportID, Procs, SSH, YAML, Human
from wultlibs.helperlibs.Exceptions import Error
from wultlibs.pepclibs import CPUInfo
from wultlibs.rawresultlibs import RORawResult

HELPERS_LOCAL_DIR = Path(".local")
_DRV_SRC_SUBPATH = Path("drivers/idle")
_HELPERS_SRC_SUBPATH = Path("helpers")

_LOG = logging.getLogger()

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

# Description for the '--reportid' option of the 'start' command.
def get_start_reportid_descr(allowed_chars):
    """
    Returns description for the '--reportid' option of the 'start' command. The 'allowed_chars'
    argument should be the allowed report ID characters description string.
    """

    descr = f"""Any string which may serve as an identifier of this run. By default report ID is the
                current date, prefixed with the remote host name in case the '-H' option was used:
                [hostname-]YYYYMMDD. For example, "20150323" is a report ID for a run made on March
                23, 2015. The allowed characters are: {allowed_chars}."""
    return descr

# Description for the '--post-trigger' option of the 'start' command.
def get_post_trigger_descr(name):
    """
    Returns description for the '--post-trigger' option of the 'start' command. The 'name' argument
    should be the trigger metric name.
    """

    descr = f"""The post-measurement trigger. Please, provide path to a trigger program that should
                be executed after a datapoint had been collected. The next measurement cycle will
                start only after the trigger program finishes. The trigger program will be executed
                as 'POST_TRIGGER --value <value>', where '<value>' is the last observed {name} in
                nanoseconds. This option exists for debugging and troubleshooting purposes only."""
    return descr

# Description for the '--post-trigger-range' option of the 'start' command.
def get_post_trigger_range_descr(name):
    """
    Returns description for the '--post-trigger-range' option of the 'start' command. The 'name'
    argument should be the name of the trigger metric name..
    """

    descr = f"""By default, the post trigger is executed for every datapoint, but this option allows
                for setting the {name} range - the trigger program will be executed only when
                observed {name} value is in the range (inclusive). Specify a comma-separated range,
                e.g '--post-trigger-range 50,600'. The default unit is microseconds, but you can use
                the following specifiers as well: {Human.DURATION_NS_SPECS_DESCR}. For example,
                '--post-trigger-range 100us,1ms' would be a [100,1000] microseconds range."""
    return descr

# Description for the '--report' option of the 'start' command.
START_REPORT_DESCR = """Generate an HTML report for collected results (same as calling 'report'
                        command with default arguments)."""

# Description for the '--outdir' option of the 'report' command.
def get_report_outdir_descr(toolname):
    """
    Returns description for the '--outdir' option of the 'report' command for the 'toolname' tool.
    """

    descr = f"""Path to the directory to store the report at. By default the report is stored in the
                '{toolname}-report-<reportid>' sub-directory of the current working directory, where
                '<reportid>' is report ID of {toolname} test result (the first one if there are
                multiple)."""
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
                 matching the names) to use on X-axes, default is '%s'. Use '--list-columns' to get
                 the list of the available column names."""

# Description for the '--yaxes' option of the 'report' command.
YAXES_DESCR = """A comma-separated list of CSV column names (or python style regular expressions
                 matching the names) to use on the Y-axes. If multiple CSV column names are
                 specified for the X- or Y-axes, then the report will include all the X- and Y-axes
                 combination. The default is '%s'. Use '--list-columns' to get the list of the
                 available column names."""

# Description for the '--hist' option of the 'report' command.
HIST_DESCR = """A comma-separated list of CSV column names (or python style regular expressions
                matching the names) to add a histogram for, default is '%s'. Use '--list-columns' to
                get the list of the available column names. Use value 'none' to disable histograms.
                """

# Description for the '--chist' option of the 'report' command.
CHIST_DESCR = """A comma-separated list of CSV column names (or python style regular expressions
                 matching the names) to add a cumulative distribution for, default is '%s'. Use
                 '--list-columns' to get the list of the available column names. Use value 'none' to
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
RELOCATABLE_DESCR = """The generated report includes references to the test results. By default,
                       these references are symlinks to the raw result directories. However, this
                       makes the generated report be not relocatable. Use this option to make the
                       report relocatable in expense of increased disk space consumption - this
                       tool will make a copy of the test results."""

# Description for the '--list-columns' option of the 'report' and other commands.
LIST_COLUMNS_DESCR = "Print the list of the available column names and exit."

# Description for the 'filter' command.
FILT_DESCR = """Filter datapoints out of a test result by removing CSV rows and columns according to
                specified criteria. The criteria is specified using the row and column filter and
                selector options ('--rsel', '--cfilt', etc). The options may be specified multiple
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

# Description for the '--cfilt' option of the 'filter' command.
CFILT_DESCR = """The columns filter: remove all column specified in the filter. The columns filter
                 is just a comma-separated list of the CSV file column names or python style regular
                 expressions matching the names. For example expression
                 'SilentTime,WarmupDelay,.*Cyc', would remove columns 'SilentTime', 'WarmupDelay'
                 and all columns with 'Cyc' in the column name. Use '--list-columns' to get the list
                 of the available column names."""

# Description for the '--csel' option of the 'filter' command.
CSEL_DESCR = """The columns selector: remove all column except for those specified in the selector.
                The syntax is the same as for '--cfilt'."""

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

def get_proc(args, hostname):
    """Returns an "SSH" or 'Procs' object for host 'hostname'."""

    if hostname == "localhost":
        return Procs.Proc()
    return SSH.SSH(hostname=hostname, username=args.username, privkeypath=args.privkey,
                   timeout=args.timeout)

def _validate_range(rng, what, single_ok):
    """Implements 'parse_ldist()' and 'parse_trange()'."""

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

def parse_trange(trange, single_ok=True):
    """Similar to 'parse_ldist()', but for the '--post-trigger-range' option."""

    return _validate_range(trange, "post-trigger range", single_ok)

def parse_cpunum(cpunum, proc=None):
    """
    Parse and validate CPU number 'cpunum'. If 'proc' is provided, then this function discovers CPU
    count on the host associated with the 'proc' object, and verifies that 'cpunum' does not exceed
    the host CPU count and the CPU is online. Note, 'proc' should be an 'SSH' or 'Proc' object. If
    'proc' is not provided, this function just checks that 'cpunum' is a positive integer number.
    """

    if not Trivial.is_int(cpunum) or int(cpunum) < 0:
        raise Error(f"bad CPU number '{cpunum}', should be a positive integer")

    cpunum = int(cpunum)

    if proc:
        with CPUInfo.CPUInfo(proc=proc) as cpuinfo:
            cpugeom = cpuinfo.get_cpu_geometry()

        if cpunum in cpugeom["offcpus"]:
            raise Error(f"CPU '{cpunum}'{proc.hostmsg} is offline")
        if cpunum not in cpugeom["cpus"]:
            raise Error(f"CPU '{cpunum}' does not exist{proc.hostmsg}")

    return cpunum

def get_dpcnt(res, dpcnt):
    """
    This helper function validates number of datapoints the user requested to collect ('dpcnt'). It
    also looks at how many datapoints are already present in the 'res' object (represents a raw test
    result) and returns the number datapoints to collect in order for 'rest' to end up with 'dpcnt'
    datapoints.
    """

    if not Trivial.is_int(dpcnt) or int(dpcnt) <= 0:
        raise Error(f"bad datapoints count '{dpcnt}', should be a positive integer")

    dpcnt = int(dpcnt) - res.csv.initial_rows_cnt
    if dpcnt <= 0:
        _LOG.info("Raw test result at '%s' already includes %d datapoints",
                  res.dirpath, res.csv.initial_rows_cnt)
        _LOG.info("Nothing to collect")
        return 0

    return dpcnt

def add_ssh_options(parser, argcomplete=None):
    """
    Add the '--host', '--timeout' and other SSH-related options to argument parser object 'parser'.
    """

    text = "System Under Test (SUT) host name to run on (default is the local host)."
    parser.add_argument("-H", "--host", help=text, default="localhost", dest="hostname")
    text = """Name of the user to use for logging into the SUT over SSH. The default user
              name is 'root'."""
    parser.add_argument("-U", "--username", dest="username", default="root", metavar="USERNAME",
                        help=text)
    text = """Path to the private SSH key that should be used for logging into the SUT. By default
              the key is automatically found from standard paths like '~/.ssh'."""
    arg = parser.add_argument("-K", "--priv-key", dest="privkey", type=Path, help=text)
    if argcomplete:
        arg.completer = argcomplete.completers.FilesCompleter()
    text = """SSH connect timeout in seconds, default is 8."""
    parser.add_argument("-T", "--timeout", default=8, help=text)

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
    '--cfilt'. The 'args' argument should be an 'helperlibs.ArgParse' object, where all the above
    mentioned options are represented by the 'oargs' (ordered arguments) field. The 'res' argument
    is 'RORawResult' or 'WORawResultBase' object.
    """

    def set_filter(res, ops):
        """Set filter operations in 'ops' to test result 'res'."""

        res.clear_filts()
        for name, expr in ops.items():
            # The '--csel' and '--cfilt' options may have comma-separated list of column names.
            if name.startswith("c"):
                expr = Trivial.split_csv_line(expr)
            getattr(res, f"set_{name}")(expr)

    if not getattr(args, "oargs", None):
        return

    # Note, the assumption is that dictionary preserves insertion order, which is true starting from
    # Python 3.6.
    ops = {}
    for name, expr in args.oargs:
        if name in ops:
            set_filter(res, ops)
            ops = {}
        ops[name] = expr

    if ops:
        set_filter(res, ops)

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

    proc = get_proc(args, args.hostname)

    msg = ""
    for devid, alias, descr in Devices.scan_devices(proc, args.devtypes):
        msg += f" * Device ID: {devid}\n"
        if alias:
            msg += f"   - Alias: {alias}\n"
        msg += f"   - Description: {descr}\n"

    if not msg:
        _LOG.info("No %s compatible devices found", args.toolname)
        return

    _LOG.info("Compatible device(s)%s:\n%s", proc.hostmsg, msg.rstrip())

def filter_command(args):
    """Implements the 'filter' command for the 'wult' and 'ndl' tools."""

    res = RORawResult.RORawResult(args.respath)

    if args.list_columns:
        for colname in res.colnames:
            _LOG.info("%s: %s", colname, res.defs.info[colname]["title"])
        return

    if not getattr(args, "oargs", None):
        raise Error("please, specify at least one reduction criteria.")
    if args.reportid and not args.outdir:
        raise Error("'--reportid' can be used only with '-o'/'--outdir'")

    apply_filters(args, res)

    if not args.outdir:
        res.df.to_csv(sys.stdout, index=False, header=True)
    else:
        res.save(args.outdir, reportid=args.reportid)

def calc_command(args):
    """Implements the 'calc' command  for the 'wult' and 'ndl' tools."""

    if args.list_funcs:
        for name, descr in RORawResult.get_smry_funcs():
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

    non_numeric = res.get_non_numeric_colnames()
    if non_numeric and (args.csel or args.cfilt):
        non_numeric = ", ".join(non_numeric)
        _LOG.warning("skipping non-numeric column(s): %s", non_numeric)

    res.calc_smrys(funcnames=funcnames, all_funcs=all_funcs)

    _LOG.info("Datapoints count: %d", len(res.df))
    YAML.dump(res.smrys, sys.stdout, float_format="%.2f")

def open_raw_results(respaths, toolname, reportids=None, reportid_additional_chars=None):
    """
    Opens the input raw test results, and returns the list of 'RORawResult' objects.
      * respaths - list of paths to raw results.
      * toolname - name of the tool opening raw results.
      * reportids - list of reportids to override report IDs in raw results.
      * reportid_additional_chars - string of characters allowed in report ID on top of default
                                    characters.
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
            ReportID.validate_reportid(reportid, additional_chars=reportid_additional_chars)

        res = RORawResult.RORawResult(respath, reportid=reportid)
        if toolname != res.info["toolname"]:
            raise Error(f"cannot generate '{toolname}' report, results are collected with the"
                        f"'{res.info['toolname']}':\n{respath}")
        rsts.append(res)

    return rsts

def list_result_columns(rsts):
    """
    Implements the '--list-columns' option by printing the column names for each raw result 'rsts'.
    """

    for rst in rsts:
        _LOG.info("Column names in '%s':", rst.dirpath)
        for colname in rst.colnames:
            _LOG.info("  * %s: %s", colname, rst.defs.info[colname]["title"])
