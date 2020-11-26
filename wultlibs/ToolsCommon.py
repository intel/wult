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
import contextlib
import time
from pathlib import Path
from wultlibs.helperlibs import Logging, Trivial, FSHelpers, KernelVersion, Procs, SSH
from wultlibs.helperlibs.Exceptions import Error

HELPERS_LOCAL_DIR = Path(".local")
_DRV_SRC_SUBPATH = Path("drivers/idle")
_HELPERS_SRC_SUBPATH = Path("helpers")

_LOG = Logging.main_log

def get_proc(args, hostname):
    """
    Returns and "SSH" object or the 'Procs' object depending on 'hostname'.
    """

    if hostname == "localhost":
        return Procs.Proc()

    return SSH.SSH(hostname=hostname, username=args.username, privkeypath=args.privkey,
                   timeout=args.timeout)

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

def remove_deploy_tmpdir(args, hostname):
    """Remove temporary files on host 'hostname'"""

    if args.tmpdir:
        with contextlib.closing(get_proc(args, hostname)) as proc:
            proc.run_verify(f"rm -rf -- '{args.tmpdir}'")

def deploy_prepare(args, toolname, minkver):
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

def build(args):
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

def deploy(args):
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
            FSHelpers.mkdir(dstdir, parents=True, default=None, proc=iproc)

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
