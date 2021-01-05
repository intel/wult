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

import os
import sys
import time
import logging
import contextlib
from pathlib import Path
from collections import OrderedDict
from wultlibs.helperlibs import Logging, Trivial, FSHelpers, KernelVersion, Procs, SSH, YAML, Human
from wultlibs.helperlibs import ReportID
from wultlibs.helperlibs.Exceptions import Error
from wultlibs.sysconfiglibs import CPUInfo
from wultlibs import RORawResult

HELPERS_LOCAL_DIR = Path(".local")
_DRV_SRC_SUBPATH = Path("drivers/idle")
_HELPERS_SRC_SUBPATH = Path("helpers")

_LOG = logging.getLogger()

# Description for the 'filter' command.
FILT_DESCR = """Filter datapoints out of a test result by removing CSV rows and columns according to
                specified criteria. The criteria is specified using the row and column filter and
                selector options ('--rsel', '--cfilt', etc). The options may be specified multiple
                times."""

# Description for the '--rfilt' option of the 'filter' command.
RFILT_DESCR = """The row filter: remove all the rows satisfying the filter expression. Here is an
                 example of an expression: '(WakeLatency < 10000) | (PC6%% < 1)'. This row filter
                 expression will remove all rows with 'WakeLatency' smaller than 10000 nanoseconds or
                 package C6 residency smaller than 1%%. The detailed row filter expression syntax can
                 be found in the documentation for the 'eval()' function of Python 'pandas' module.
                 You can use column names in the expression, or the special word 'index' for the row
                 number. Value '0' is the header, value '1' is the first row, and so on. For example,
                 expression 'index >= 10' will get rid of all data rows except for the first 10
                 ones."""

# Description for the '--rsel' option of the 'filter' command.
RSEL_DESCR = """The row selector: remove all rows except for those satisfying the selector
                expression. In other words, the selector is just an inverse filter: '--rsel expr' is
                the same as '--rfilt "not (expr)"'."""

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

def get_proc(args, hostname):
    """
    Returns and "SSH" object or the 'Procs' object depending on 'hostname'.
    """

    if hostname == "localhost":
        return Procs.Proc()

    return SSH.SSH(hostname=hostname, username=args.username, privkeypath=args.privkey,
                   timeout=args.timeout)

def validate_ldist(ldist):
    """
    Parse and validate the launch distance range ('--ldist' option). The 'ldist' argument is a
    string of single or two comma-separated launch distance values. The values are parsed with
    'Human.parse_duration_ns()', so they can include specifiers like 'ms' or 'us'. Returns launch
    launch distance range as a list of two integers in nanoseconds.
    """

    split_ldst = Trivial.split_csv_line(ldist)
    ldst = [None] * len(split_ldst)

    for idx, val in enumerate(split_ldst):
        try:
            ldst[idx] = Human.parse_duration_ns(val, default_unit="us")
        except Error as err:
            raise Error(f"bad launch distance '{split_ldst[idx]}', {err}")
        if ldst[idx] <= 0:
            raise Error(f"bad launch distance value '{split_ldst[idx]}', should be greater than "
                        f"zero")

    if len(ldst) > 2:
        raise Error(f"bad launch distance range '{ldist}', it should include 2 numbers")
    if len(ldst) == 2 and ldst[1] - ldst[0] < 0:
        raise Error(f"bad launch distance range '{ldist}', first number cannot be "
                    f"greater than the second number")
    if len(ldst) == 1:
        ldst.append(ldst[0])

    return ldst

def validate_cpunum(cpunum, proc=None):
    """
    Validate CPU number 'cpunum'. If 'proc' is provided, then this function discovers CPU count on
    the host associated with the 'proc' object, and verifies that 'cpunum' does not exceed the host
    CPU count and the CPU is online. Note, 'proc' should be an 'SSH' or 'Proc' object. If 'proc' is
    not provided, this function just checks that 'cpunum' is a positive integer number.
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

def add_ssh_options(parser, argcomplete=None):
    """
    Add the '--host', '--timeout' and other SSH-related options to argument parser object 'parser'.
    """

    text = "Name of the host to run on (default is the local host)."
    parser.add_argument("-H", "--host", help=text, default="localhost", dest="hostname")
    text = """Name of the user to use for logging into the remote host over SSH. The default user
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
            raise Error(f"'stat()' failed for '{res.dp_path}': {err}")
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

def apply_filters(args, res):
    """
    This is a helper function for the following command-line options: '--rsel', '--rfilt', '--csel',
    '--cfilt'. The 'args' argument should be an 'helperlibs.ArgParse' object, where all the above
    mentioned options are represented by the 'oargs' (ordered arguments) field. The 'res' argument
    is a 'RORawResult' object.
    """

    def do_filter(res, ops):
        """Apply filter operations in 'ops' to wult test result 'res'."""

        res.clear_filts()
        for name, expr in ops.items():
            if name.startswith("c"):
                expr = Trivial.split_csv_line(expr)
            getattr(res, f"set_{name}")(expr)
        res.load_df()

    if not getattr(args, "oargs", None):
        return

    ops = OrderedDict()
    for name, expr in args.oargs:
        if name in ops:
            do_filter(res, ops)
            ops = OrderedDict()
        ops[name] = expr

    if ops:
        do_filter(res, ops)

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

def report_command_open_raw_results(args):
    """
    Opens the input raw test results for the 'report' command of the 'wult' and 'ndl' tools. Returns
    the list of 'RORawResult' objects. At the same time, implements the '--list-columns' option by
    printing the column names for each input raw result.
    """

    if args.reportids:
        reportids = Trivial.split_csv_line(args.reportids)
    else:
        reportids = []

    if len(reportids) > len(args.respaths):
        raise Error(f"there are {len(reportids)} report IDs to assign to {len(args.respaths)} "
                    f"input test results. Please, provide {len(args.respaths)} or less report IDs.")

    # Append the required amount of 'None's to make the 'reportids' list be of the same length as
    # the 'args.respaths' list.
    reportids += [None] * (len(args.respaths) - len(reportids))

    rsts = []
    for respath, reportid in zip(args.respaths, reportids):
        if reportid:
            additional_chars = getattr(args, "reportid_additional_chars", None)
            ReportID.validate_reportid(reportid, additional_chars=additional_chars)

        res = RORawResult.RORawResult(respath, reportid=reportid)
        rsts.append(res)

        if args.list_columns:
            _LOG.info("Column names in '%s':", respath)
            for colname in res.colnames:
                _LOG.info("  * %s: %s", colname, res.defs.info[colname]["title"])

    return rsts

def add_deploy_cmdline_args(parser, toolname, drivers=True, helpers=True, argcomplete=None):
    """
    Add command-line arguments for the 'deploy' command. The input arguments are as follows.
      o parse - the 'argparse' parser to add common argumets to.
      o toolname - name of the tool the command line arguments belong to.
      o drivers - whether the tool comes with out of tree drivers.
      o helpers - whether the tool comes with other helper tools.
      o argcomplete - optional 'argcomplete' command-line arguments completer object.
    """

    envarname = f"{toolname.upper()}_DATA_PATH"
    searchdirs = [f"{Path(sys.argv[0]).parent}/%s/{toolname}",
                  f"${envarname}/%s/{toolname} (if '{envarname}' environment variable is defined)",
                  f"$HOME/.local/share/wult/%s/{toolname}",
                  f"/usr/local/share/wult/%s/{toolname}", f"/usr/share/wult/%s/{toolname}"]

    if drivers:
        dirnames = [dirname % str(_DRV_SRC_SUBPATH) for dirname in searchdirs]
        text = f"""Path to {toolname} drivers sources to build and deploy. By default the drivers
                   are searched for in the following directories (and in the following order) on the
                   local host: %s.""" % ", ".join(dirnames)
        arg = parser.add_argument("--drivers-src", help=text, dest="drvsrc", type=Path)
        if argcomplete:
            arg.completer = argcomplete.completers.DirectoriesCompleter()

    if helpers:
        dirnames = [dirname % str(_HELPERS_SRC_SUBPATH) for dirname in searchdirs]
        text = f"""Path to {toolname} helpers directory to build and deploy. By default the helpers
                   to build are searched for in the following directories (and in the following
                   order) on the local host: %s.""" % ", ".join(dirnames)
        arg = parser.add_argument("--helpers-src", help=text, dest="helpersrc", type=Path)
        if argcomplete:
            arg.completer = argcomplete.completers.DirectoriesCompleter()

    if drivers:
        text = """Path to the Linux kernel sources to build the drivers against. The default is
                  '/lib/modules/$(uname -r)/build'. This is the path on the system the drivers are
                  going to be build on (BHOST)"""
        arg = parser.add_argument("--kernel-src", dest="ksrc", type=Path, help=text)
        if argcomplete:
            arg.completer = argcomplete.completers.DirectoriesCompleter()

        text = f"""Where the {toolname} drivers should be deploy to (IHOST). The default is
                   '/lib/modules/<kver>, where '<kver>' is version of the kernel in KSRC."""
        arg = parser.add_argument("--kmod-path", help=text, type=Path, dest="kmodpath")
        if argcomplete:
            arg.completer = argcomplete.completers.DirectoriesCompleter()

    if helpers:
        text = f"""Path to the directory to deploy {toolname} helper tools to. The default is the
                   path defined by the {toolname.upper()}_HELPERSPATH environment variable. If it is
                   not defined, the default path is '$HOME/{HELPERS_LOCAL_DIR}/bin', where '$HOME'
                   is the home directory of user 'USERNAME' on host 'IHOST' (see '--host' and
                   '--username' options)."""
        arg = parser.add_argument("--helpers-path", metavar="HELPERSPATH", type=Path, help=text)
        if argcomplete:
            arg.completer = argcomplete.completers.DirectoriesCompleter()

    what = ""
    if helpers and drivers:
        what = "helpers and drivers"
    elif helpers:
        what = "helpers"
    else:
        what = "helpers and drivers"

    text = f"""Name of the host {what} have to be deployed to (local host by default). In order to
               deploy to a remote host this program will log into it using the 'SSH' protocol."""
    parser.add_argument("-H", "--host", dest="ihost", default=None, help=text)

    text = f"""Name of the host {what} have to be built on. By default they are built on IHOST, but
               this option can be used to build on the local host ('use --build-host localhost')."""
    parser.add_argument("--build-host", dest="bhost", default=None, help=text)

    text = """Name of the user to use for logging into the SUT over SSH. The default user name is
              'root'."""
    parser.add_argument("-U", "--username", dest="username", help=text)

    text = """Path to the private SSH key that should be used for logging into the SUT. By default
              the key is automatically found from standard paths like '~/.ssh'."""
    arg = parser.add_argument("-K", "--privkey", dest="privkey", type=Path, help=text)
    if argcomplete:
        arg.completer = argcomplete.completers.FilesCompleter()

    text = """SSH connect timeout in seconds, default is 8."""
    parser.add_argument("-T", "--timeout", dest="timeout", help=text)

def _get_module_path(proc, name):
    """Return path to installed module. Return 'None', if module not found."""

    cmd = f"modinfo -n {name}"
    stdout, _, exitcode = proc.run(cmd)
    if exitcode != 0:
        return None

    modpath = Path(stdout.strip())
    if FSHelpers.isfile(modpath, proc):
        return modpath
    return None

def get_helpers_deploy_path(proc, toolname):
    """
    Get helpers deployment path for 'toolname' on the system associated with the 'proc' object.
    """

    helpers_path = os.environ.get(f"{toolname.upper()}_HELPERSPATH")
    if not helpers_path:
        helpers_path = FSHelpers.get_homedir(proc=proc) / HELPERS_LOCAL_DIR
    return helpers_path

def _get_deployables(srcpath, proc):
    """
    Returns the list of "deployables" (driver names or helper tool names) provided by tools or
    drivers source code directory 'srcpath' on a host defined by 'proc'.
    """

    cmd = f"make --silent -C '{srcpath}' list_deployables"
    deployables, _ = proc.run_verify(cmd)
    if deployables:
        deployables = Trivial.split_csv_line(deployables, sep=" ")

    return deployables

def is_deploy_needed(proc, toolname, helperpath=None):
    """
    Wult and other tools require additional helper programs and drivers to be installed on the
    measured system. This function tries to analyze the measured system and figure out whether
    drivers and helper programs are present and up-to-date. Returns 'True' if re-deployment is
    needed, and 'False' otherwise.

    This function works by simply matching the modification date of sources and binaries for every
    required helper and driver. If sources have later date, then re-deployment is probably needed.
      * proc - the 'Proc' or 'SSH' object associated with the measured system.
      * toolname - name of the tool to check the necessity of deployment for (e.g., "wult").
      * helperpath - optional path to the helper program that is required to be up-to-date for
                     'toolname' to work correctly. If 'helperpath' is not given, default paths
                     are used to locate helper program.
    """

    def get_path_pairs(proc, toolname, helperpath):
        """
        Yield paths for 'toolname' driver and helpertool source code and deployables. Arguments are
        same as in 'is_deploy_needed()'.
        """

        lproc = Procs.Proc()

        for path, is_drv in [(_DRV_SRC_SUBPATH, True), (_HELPERS_SRC_SUBPATH, False)]:
            srcpath = FSHelpers.search_for_app_data(toolname, path / toolname, default=None)
            # Some tools may not have helpers.
            if not srcpath:
                continue

            for deployable in _get_deployables(srcpath, lproc):
                deploypath = None
                # Deployable can be driver module or helpertool.
                if is_drv:
                    deploypath = _get_module_path(proc, deployable)
                else:
                    if helperpath and helperpath.name == deployable:
                        deploypath = helperpath
                    else:
                        deploypath = get_helpers_deploy_path(proc, toolname)
                        deploypath = Path(deploypath, "bin", deployable)
                yield srcpath, deploypath

    def get_newest_mtime(path):
        """Scan items in 'path' and return newest modification time among entries found."""

        newest = 0
        for _, fpath, _ in FSHelpers.lsdir(path, must_exist=False):
            mtime = os.path.getmtime(fpath)
            if mtime > newest:
                newest = mtime

        if not newest:
            raise Error(f"no files found in '{path}'")
        return newest

    delta = 0
    if proc.is_remote:
        # We are about to get timestamps for local and remote files. Take into account the possible
        # time shift between local and remote systems.

        remote_time = proc.run_verify("date +%s")[0].strip()
        delta = time.time() - float(remote_time)

    for srcpath, deploypath in get_path_pairs(proc, toolname, helperpath):
        if not deploypath or not FSHelpers.exists(deploypath, proc):
            return True

        srcmtime = get_newest_mtime(srcpath)
        if srcmtime + delta > FSHelpers.get_mtime(deploypath, proc):
            return True

    return False

def _deploy_prepare(args, toolname, minkver):
    """
    Validate command-line arguments of the "deploy" command and prepare for builing the helpers and
    drivers. The arguments are as follows.
      o args - the command line arguments.
      o toolname - name of the tool being deployed (e.g., 'ndl').
      o minkver - the minimum required version number.
    """

    args.tmpdir = None
    args.kver = None

    if not args.ihost:
        args.ihost = "localhost"
    if not args.bhost:
        args.bhost = args.ihost

    if args.ihost != args.bhost and not args.bhost == "localhost":
        raise Error("build host (--build-host) must be the local host or the same as deploy host "
                    "(--host)")

    if args.ihost == "localhost" and args.bhost == "localhost":
        for attr in ("username", "privkey", "timeout"):
            if getattr(args, attr) is not None:
                _LOG.warning("ignoring the '--%s' option as it not useful for a local host", attr)

    if not args.timeout:
        args.timeout = 8
    else:
        args.timeout = Trivial.str_to_num(args.timeout)
    if not args.username:
        args.username = "root"

    if args.privkey and not args.privkey.is_dir():
        raise Error(f"path '{args.privkey}' does not exist or it is not a directory")

    if hasattr(args, "drvsrc"):
        if not args.drvsrc:
            args.drvsrc = FSHelpers.search_for_app_data("wult", _DRV_SRC_SUBPATH/f"{toolname}",
                                                        pathdescr=f"{toolname} drivers sources")

        if not args.drvsrc.is_dir():
            raise Error(f"path '{args.drvsrc}' does not exist or it is not a directory")

    if hasattr(args, "helpersrc"):
        if not args.helpersrc:
            args.helpersrc = FSHelpers.search_for_app_data("wult",
                                                           _HELPERS_SRC_SUBPATH/f"{toolname}",
                                                           pathdescr=f"{toolname} helper sources")
        if not args.helpersrc.is_dir():
            raise Error(f"path '{args.helpersrc}' does not exist or it is not a directory")

    with contextlib.closing(get_proc(args, args.bhost)) as proc:
        if not FSHelpers.which("make", default=None, proc=proc):
            raise Error(f"please, install the 'make' tool{proc.hostmsg}")

        if not args.ksrc:
            args.kver = KernelVersion.get_kver(proc=proc)
            if not args.ksrc:
                args.ksrc = Path(f"/lib/modules/{args.kver}/build")
        else:
            args.ksrc = FSHelpers.abspath(args.ksrc, proc=proc)

        if not FSHelpers.isdir(args.ksrc, proc=proc):
            raise Error(f"kernel sources directory '{args.ksrc}' does not exist{proc.hostmsg}")

        if not args.kver:
            args.kver = KernelVersion.get_kver_ktree(args.ksrc, proc=proc)

        _LOG.info("Kernel sources path: %s", args.ksrc)
        _LOG.info("Kernel version: %s", args.kver)

        if KernelVersion.kver_lt(args.kver, minkver):
            raise Error(f"version of the kernel{proc.hostmsg} is {args.kver}, and it is not new "
                        f"enough.\nPlease, use kernel version {minkver} or newer.")

        args.tmpdir = FSHelpers.mktemp(prefix=f"{toolname}-", proc=proc)

        if hasattr(args, "drvsrc"):
            _LOG.debug("copying the drivers to %s:\n   '%s' -> '%s'",
                       proc.hostname, args.drvsrc, args.tmpdir)
            proc.rsync(f"{args.drvsrc}/", args.tmpdir / "drivers", remotesrc=False, remotedst=True)
            args.drvsrc = args.tmpdir / "drivers"
            _LOG.info("Drivers will be compiled on host '%s'", proc.hostname)

        if hasattr(args, "helpersrc"):
            _LOG.debug("copying the helpers to %s:\n  '%s' -> '%s'",
                       proc.hostname, args.helpersrc, args.tmpdir)
            proc.rsync(f"{args.helpersrc}/", args.tmpdir / "helpers", remotesrc=False,
                       remotedst=True)
            args.helpersrc = args.tmpdir / "helpers"
            _LOG.info("Helpers will be compiled on host '%s'", proc.hostname)

    with contextlib.closing(get_proc(args, args.ihost)) as proc:
        if not args.kmodpath:
            args.kmodpath = Path(f"/lib/modules/{args.kver}")
        if not FSHelpers.isdir(args.kmodpath, proc=proc):
            raise Error(f"kernel modules directory '{args.kmodpath}' does not exist{proc.hostmsg}")

        _LOG.info("Drivers will be deployed to '%s'%s", args.kmodpath, proc.hostmsg)
        _LOG.info("Kernel modules path%s: %s", proc.hostmsg, args.kmodpath)

        if hasattr(args, "helpersrc"):
            if not args.helpers_path:
                args.helpers_path = get_helpers_deploy_path(proc, toolname)
            _LOG.info("Helpers will be deployed to '%s'%s", args.helpers_path, proc.hostmsg)

def _log_cmd_output(args, stdout, stderr):
    """Print output of a command in case debugging is enabled."""

    if args.debug:
        if stdout:
            _LOG.log(Logging.ERRINFO, stdout)
        if stderr:
            _LOG.log(Logging.ERRINFO, stderr)

def _build(args):
    """Build drivers and helpers."""

    with contextlib.closing(get_proc(args, args.bhost)) as proc:
        if hasattr(args, "drvsrc"):
            _LOG.info("Compiling the drivers%s", proc.hostmsg)
            cmd = f"make -C '{args.drvsrc}' KSRC='{args.ksrc}'"
            if args.debug:
                cmd += " V=1"
            stdout, stderr = proc.run_verify(cmd)
            _log_cmd_output(args, stdout, stderr)

        if hasattr(args, "helpersrc"):
            _LOG.info("Compiling the helpers%s", proc.hostmsg)
            stdout, stderr = proc.run_verify(f"make -C '{args.helpersrc}'")
            _log_cmd_output(args, stdout, stderr)

def _deploy(args):
    """Deploy helpers and drivers."""

    with contextlib.closing(get_proc(args, args.ihost)) as iproc, \
         contextlib.closing(get_proc(args, args.bhost)) as bproc:
        remotesrc = args.bhost != "localhost"
        remotedst = args.ihost != "localhost"

        if hasattr(args, "helpersrc"):
            helpersdst = args.tmpdir / "helpers_deployed"
            _LOG.debug("Deploying helpers to '%s'%s", helpersdst, bproc.hostmsg)
            cmd = f"make -C '{args.helpersrc}' install PREFIX='{helpersdst}'"
            stdout, stderr = bproc.run_verify(cmd)
            _log_cmd_output(args, stdout, stderr)

            iproc.rsync(str(helpersdst) + "/", args.helpers_path,
                        remotesrc=remotesrc, remotedst=remotedst)

        if hasattr(args, "drvsrc"):
            dstdir = args.kmodpath.joinpath(_DRV_SRC_SUBPATH)
            FSHelpers.mkdir(dstdir, parents=True, exist_ok=True, proc=iproc)

            for name in _get_deployables(args.drvsrc, bproc):
                installed_module = _get_module_path(iproc, name)
                srcpath = args.drvsrc.joinpath(f"{name}.ko")
                dstpath = dstdir.joinpath(f"{name}.ko")
                _LOG.info("Deploying driver '%s' to '%s'%s", name, dstpath, iproc.hostmsg)
                iproc.rsync(srcpath, dstpath, remotesrc=remotesrc, remotedst=remotedst)

                if installed_module and installed_module.resolve() != dstpath.resolve():
                    _LOG.debug("removing old module '%s'%s", installed_module, iproc.hostmsg)
                    iproc.run_verify(f"rm -f '{installed_module}'")

            stdout, stderr = iproc.run_verify(f"depmod -a -- '{args.kver}'")
            _log_cmd_output(args, stdout, stderr)

            # Potentially the deployed driver may crash the system before it gets to write-back data
            # to the file-system (e.g., what 'depmod' modified). This may lead to subsequent boot
            # problems. So sync the file-system now.
            iproc.run_verify("sync")

def _remove_deploy_tmpdir(args):
    """Remove temporary files on the build host ('args.bhost')."""

    if getattr(args, "tmpdir", None):
        with contextlib.closing(get_proc(args, args.bhost)) as proc:
            proc.run_verify(f"rm -rf -- '{args.tmpdir}'")

def deploy_command(args):
    """Implements the 'deploy' command for the 'wult' and 'ndl' tools."""

    try:
        _deploy_prepare(args, args.toolname, args.minkver)
        _build(args)
        _deploy(args)
    finally:
        _remove_deploy_tmpdir(args)
