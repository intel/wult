# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides various functions impelementing the 'wult' and 'ndl' tools deployment.
"""

import os
import sys
import time
import zipfile
import logging
from pathlib import Path
from pepclibs.helperlibs import LocalProcessManager, Trivial, FSHelpers, Logging, ArgParse
from pepclibs.helperlibs import ClassHelpers
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
from wultlibs import ToolsCommon
from wultlibs.helperlibs import KernelVersion, RemoteHelpers

_HELPERS_LOCAL_DIR = Path(".local")
_DRV_SRC_SUBPATH = Path("drivers/idle")
_HELPERS_SRC_SUBPATH = Path("helpers")

_LOG = logging.getLogger()

def add_deploy_cmdline_args(subparsers, toolname, func, drivers=True, helpers=None, pyhelpers=None,
                            argcomplete=None):
    """
    Add the the 'deploy' command. The input arguments are as follows.
      o subparsers - the 'argparse' subparsers to add the 'deploy' command to.
      o toolname - name of the tool the command line arguments belong to.
      o func - the 'deploy' command handling function.
      o drivers - whether out-of-tree kernel drivers have to be deployed to the SUT.
      o helpers - list of helpers required to be deployed on the SUT.
      o pyhelpers - list of python helpers required to be deployed on the SUT.
      o argcomplete - optional 'argcomplete' command-line arguments completer object.

      The difference about helpers and pyhelpers.
      1. Helpers are stand-alone tools residing in the 'helpers' subdirectory. They do not depend on
         any module/capability provided by this project. An example would be a stand-alone C
         program. Helpers are deployed by compiling them on the SUT using 'make' and installing them
         using 'make install'.
      2. Python helpers (pyhelpers) are helper tools written in python (e.g., 'stats-collect'). They
         also reside in the 'helpers' subdirectory, but they are not totally independent. They
         depend on multiple modules that come with 'wult' project (e.g.,
         'helperlibs/LocalProcessManager.py'). Therefore, in order to deploy python helpers, we need
         to deploy the dependencies. And the way we do this depends on whether we deploy to the
         local system or to a remote system. In case of the local system, python helpers are
         deployed by 'setup.py', just the 'wult' tool is deployed. In case of a remote system, we
         build and deploy a stand-alone version of the helper using python '__main__.py' + zip
         archive mechanism.
    """

    if not helpers:
        helpers = []
    if not pyhelpers:
        pyhelpers = []

    what = ""
    if (helpers or pyhelpers) and drivers:
        what = "helpers and drivers"
    elif helpers or pyhelpers:
        what = "helpers"
    else:
        what = "drivers"

    envarname = f"{toolname.upper()}_DATA_PATH"
    searchdirs = [f"{Path(sys.argv[0]).parent}/%s",
                  f"${envarname}/%s (if '{envarname}' environment variable is defined)",
                  "$HOME/.local/share/wult/%s",
                  "/usr/local/share/wult/%s", "/usr/share/wult/%s"]

    text = f"Compile and deploy {toolname} {what}."
    descr = f"""Compile and deploy {toolname} {what} to the SUT (System Under Test), which can be
                either local or a remote host, depending on the '-H' option."""
    if drivers:
        drvsearch = ", ".join([dirname % str(_DRV_SRC_SUBPATH) for dirname in searchdirs])
        descr += f"""The drivers are searched for in the following directories (and in the following
                     order) on the local host: {drvsearch}."""
    if helpers or pyhelpers:
        helpersearch = ", ".join([dirname % str(_HELPERS_SRC_SUBPATH) for dirname in searchdirs])
        helpernames = ", ".join(helpers + pyhelpers)
        descr += f"""The {toolname} tool also depends on the following helpers: {helpernames}. These
                     helpers will be compiled on the SUT and deployed to the SUT. The sources of the
                     helpers are searched for in the following paths (and in the following order) on
                     the local host: {helpersearch}. By default, helpers are deployed to the path
                     defined by the {toolname.upper()}_HELPERSPATH environment variable. If the
                     variable is not defined, helpers are deployed to
                     '$HOME/{_HELPERS_LOCAL_DIR}/bin', where '$HOME' is the home directory of user
                     'USERNAME' on host 'HOST' (see '--host' and '--username' options)."""
    parser = subparsers.add_parser("deploy", help=text, description=descr)

    if drivers:
        text = """Path to the Linux kernel sources to build the drivers against. The default is
                  '/lib/modules/$(uname -r)/build' on the SUT. In case of deploying to a remote
                  host, this is the path on the remote host (HOSTNAME)."""
        arg = parser.add_argument("--kernel-src", dest="ksrc", type=Path, help=text)
        if argcomplete:
            arg.completer = argcomplete.completers.DirectoriesCompleter()

    ArgParse.add_ssh_options(parser)

    parser.set_defaults(func=func)
    parser.set_defaults(helpers=helpers)
    parser.set_defaults(pyhelpers=pyhelpers)

def _get_module_path(pman, name):
    """Return path to installed module. Return 'None', if module not found."""

    cmd = f"modinfo -n {name}"
    stdout, _, exitcode = pman.run(cmd)
    if exitcode != 0:
        return None

    modpath = Path(stdout.strip())
    if FSHelpers.isfile(modpath, pman):
        return modpath
    return None

def get_helpers_deploy_path(pman, toolname):
    """
    Get helpers deployment path for 'toolname' on the system associated with the 'pman' object.
    """

    helpers_path = os.environ.get(f"{toolname.upper()}_HELPERSPATH")
    if not helpers_path:
        helpers_path = FSHelpers.get_homedir(pman=pman) / _HELPERS_LOCAL_DIR / "bin"
    return Path(helpers_path)

def _get_deployables(srcpath, pman=None):
    """
    Returns the list of "deployables" (driver names or helper tool names) provided by tools or
    drivers source code directory 'srcpath' on a host defined by 'pman'.
    """

    if not pman:
        pman = LocalProcessManager.LocalProcessManager()

    cmd = f"make --silent -C '{srcpath}' list_deployables"
    deployables, _ = pman.run_verify(cmd)
    if deployables:
        deployables = Trivial.split_csv_line(deployables, sep=" ")

    return deployables

def _get_pyhelper_dependencies(script_path):
    """
    Find and return a python helper script (pyhelper) dependencies. Only wult module dependencies
    are returned. An example of such a dependency would be:
        /usr/lib/python3.9/site-packages/helperlibs/Trivial.py
    """

    # All pyhelpers implement the '--print-module-paths' option, which prints the dependencies.
    cmd = f"{script_path} --print-module-paths"
    stdout, _ = LocalProcessManager.LocalProcessManager().run_verify(cmd)
    return [Path(path) for path in stdout.splitlines()]

def find_app_data(prjname, subpath, appname=None, descr=None):
    """
    Search for application 'appname' data. The data are searched for in the 'subpath' sub-path of
    the following directories (and in the following order):
      * in the directory the of the running process (sys.argv[0]/<subpath>)
      * in the directory specified by the f'{appname}_DATA_PATH' environment variable
      * $HOME/.local/share/<prjname>/, if it exists
      * /usr/local/share/<prjname>/, if it exists
      * /usr/share/<prjname>/, if it exists

    The 'descr' argument is a human-readable description of 'subpath', which will be used in the
    error message if error is raised.
    """

    if not appname:
        appname = prjname

    searched = []
    paths = []

    paths.append(Path(sys.argv[0]).parent)

    path = os.environ.get(f"{appname}_DATA_PATH".upper())
    if path:
        paths.append(Path(path))

    for path in paths:
        path /= subpath
        if path.exists():
            return path
        searched.append(path)

    path = Path("~").expanduser() / Path(f".local/share/{prjname}/{subpath}")
    if path.exists():
        return path

    searched.append(path)

    for path in (Path(f"/usr/local/share/{prjname}"), Path(f"/usr/share/{prjname}")):
        path /= subpath
        if path.exists():
            return path
        searched.append(path)

    if not descr:
        descr = f"'{subpath}'"
    searched = [str(s) for s in searched]
    dirs = " * " + "\n * ".join(searched)

    raise Error(f"cannot find {descr}, searched in the following directories on local host:\n"
                f"{dirs}")

def is_deploy_needed(pman, toolname, helpers=None, pyhelpers=None):
    """
    Wult and other tools require additional helper programs and drivers to be installed on the SUT.
    This function tries to analyze the SUT and figure out whether drivers and helper programs are
    present and up-to-date. Returns 'True' if re-deployment is needed, and 'False' otherwise.

    This function works by simply matching the modification date of sources and binaries for every
    required helper and driver. If sources have later date, then re-deployment is probably needed.
      * pman - the process manager object for the SUT.
      * toolname - name of the tool to check the necessity of deployment for (e.g., "wult").
      o helpers - list of helpers required to be deployed on the SUT.
      o pyhelpers - list of python helpers required to be deployed on the SUT.
    """

    def get_newest_mtime(paths):
        """
        Scan list of paths 'paths', find and return the most recent modification time (mtime) among
        files in 'path' and (in case 'path' is irectory) every file under 'path'.
        """

        newest = 0
        for path in paths:
            if not path.is_dir():
                mtime = path.stat().st_mtime
                if mtime > newest:
                    newest = mtime
            else:
                for root, _, files in os.walk(path):
                    for file in files:
                        mtime = Path(root, file).stat().st_mtime
                        if mtime > newest:
                            newest = mtime

        if not newest:
            paths_str = "\n* ".join([str(path) for path in paths])
            raise Error(f"no files found in the following paths:\n{paths_str}")
        return newest

    def deployable_not_found(what):
        """Called when a helper of driver was not found on the SUT to raise an exception."""

        err = f"{what} was not found on {pman.hostmsg}. Please, run:\n{toolname} deploy"
        if pman.is_remote:
            err += f" -H {pman.hostname}"
        raise Error(err)


    # Build the deploy information dictionary. Start with drivers.
    dinfos = {}
    srcpath = find_app_data("wult", _DRV_SRC_SUBPATH / toolname, appname=toolname)
    dstpaths = []
    for deployable in _get_deployables(srcpath):
        dstpath = _get_module_path(pman, deployable)
        if not dstpath:
            deployable_not_found(f"the '{deployable}' kernel module")
        dstpaths.append(_get_module_path(pman, deployable))
    dinfos["drivers"] = {"src" : [srcpath], "dst" : dstpaths}

    # Add non-python helpers' deploy information.
    if helpers or pyhelpers:
        helpers_deploy_path = get_helpers_deploy_path(pman, toolname)

    if helpers:
        for helper in helpers:
            srcpath = find_app_data("wult", _HELPERS_SRC_SUBPATH / helper, appname=toolname)
            dstpaths = []
            for deployable in _get_deployables(srcpath):
                dstpaths.append(helpers_deploy_path / deployable)
            dinfos[helper] = {"src" : [srcpath], "dst" : dstpaths}

    # Add python helpers' deploy information. Note, python helpers are deployed only to the remote
    # host. The local copy of python helpers comes via 'setup.py'. Therefore, check them only for
    # the remote case.
    if pyhelpers and pman.is_remote:
        for pyhelper in pyhelpers:
            datapath = find_app_data("wult", _HELPERS_SRC_SUBPATH / pyhelper, appname=toolname)
            srcpaths = []
            dstpaths = []
            lpman = LocalProcessManager.LocalProcessManager()

            for deployable in _get_deployables(datapath, lpman):
                if datapath.joinpath(deployable).exists():
                    # This case is relevant for running wult from sources - python helpers are
                    # in the 'helpers/pyhelper' directory.
                    srcpath = datapath
                else:
                    # When wult is installed with 'pip', the python helpers go to the "bindir",
                    # and they are not installed to the data directory.
                    srcpath = FSHelpers.which(deployable).parent

                srcpaths += _get_pyhelper_dependencies(srcpath / deployable)
                dstpaths.append(helpers_deploy_path / deployable)
            dinfos[pyhelper] = {"src" : srcpaths, "dst" : dstpaths}

    # We are about to get timestamps for local and remote files. Take into account the possible time
    # shift between local and remote systems.
    time_delta = 0
    if pman.is_remote:
        time_delta = time.time() - RemoteHelpers.time_time(pman=pman)

    # Compare source and destination files' timestamps.
    for what, dinfo in dinfos.items():
        src = dinfo["src"]
        src_mtime = get_newest_mtime(src)
        for dst in dinfo["dst"]:
            try:
                dst_mtime = FSHelpers.get_mtime(dst, pman)
            except ErrorNotFound:
                deployable_not_found(dst)

            if src_mtime > time_delta + dst_mtime:
                src_str = ", ".join([str(path) for path in src])
                _LOG.debug("%s src time %d + %d > dst_mtime %d\nsrc: %s\ndst %s",
                           what, src_mtime, time_delta, dst_mtime, src_str, dst)
                return True

    return False

def _log_cmd_output(args, stdout, stderr):
    """Print output of a command in case debugging is enabled."""

    if args.debug:
        if stdout:
            _LOG.log(Logging.ERRINFO, stdout)
        if stderr:
            _LOG.log(Logging.ERRINFO, stderr)

def _deploy_drivers(args, pman):
    """Deploy drivers to the SUT represented by 'pman'."""

    drvsrc = find_app_data("wult", _DRV_SRC_SUBPATH/f"{args.toolname}",
                           descr=f"{args.toolname} drivers sources")
    if not drvsrc.is_dir():
        raise Error(f"path '{drvsrc}' does not exist or it is not a directory")

    kver = None
    if not args.ksrc:
        kver = KernelVersion.get_kver(pman=pman)
        if not args.ksrc:
            args.ksrc = Path(f"/lib/modules/{kver}/build")
    else:
        args.ksrc = FSHelpers.abspath(args.ksrc, pman=pman)

    if not FSHelpers.isdir(args.ksrc, pman=pman):
        raise Error(f"kernel sources directory '{args.ksrc}' does not exist{pman.hostmsg}")

    if not kver:
        kver = KernelVersion.get_kver_ktree(args.ksrc, pman=pman)

    _LOG.info("Kernel sources path: %s", args.ksrc)
    _LOG.info("Kernel version: %s", kver)

    if KernelVersion.kver_lt(kver, args.minkver):
        raise Error(f"version of the kernel{pman.hostmsg} is {kver}, and it is not new enough.\n"
                    f"Please, use kernel version {args.minkver} or newer.")

    _LOG.debug("copying the drivers to %s:\n   '%s' -> '%s'", pman.hostname, drvsrc, args.stmpdir)
    pman.rsync(f"{drvsrc}/", args.stmpdir / "drivers", remotesrc=False, remotedst=True)
    drvsrc = args.stmpdir / "drivers"

    kmodpath = Path(f"/lib/modules/{kver}")
    if not FSHelpers.isdir(kmodpath, pman=pman):
        raise Error(f"kernel modules directory '{kmodpath}' does not exist{pman.hostmsg}")

    # Build the drivers on the SUT.
    _LOG.info("Compiling the drivers%s", pman.hostmsg)
    cmd = f"make -C '{drvsrc}' KSRC='{args.ksrc}'"
    if args.debug:
        cmd += " V=1"

    stdout, stderr, exitcode = pman.run(cmd)
    if exitcode != 0:
        msg = pman.cmd_failed_msg(cmd, stdout, stderr, exitcode)
        if "synth_event_" in stderr:
            msg += "\n\nLooks like synthetic events support is disabled in your kernel, enable " \
                   "the 'CONFIG_SYNTH_EVENTS' kernel configuration option."
        raise Error(msg)

    _log_cmd_output(args, stdout, stderr)

    # Deploy the drivers.
    dstdir = kmodpath / _DRV_SRC_SUBPATH
    FSHelpers.mkdir(dstdir, parents=True, exist_ok=True, pman=pman)

    for name in _get_deployables(drvsrc, pman):
        installed_module = _get_module_path(pman, name)
        srcpath = drvsrc / f"{name}.ko"
        dstpath = dstdir / f"{name}.ko"
        _LOG.info("Deploying driver '%s' to '%s'%s", name, dstpath, pman.hostmsg)
        pman.rsync(srcpath, dstpath, remotesrc=True, remotedst=True)

        if installed_module and installed_module.resolve() != dstpath.resolve():
            _LOG.debug("removing old module '%s'%s", installed_module, pman.hostmsg)
            pman.run_verify(f"rm -f '{installed_module}'")

    stdout, stderr = pman.run_verify(f"depmod -a -- '{kver}'")
    _log_cmd_output(args, stdout, stderr)

    # Potentially the deployed driver may crash the system before it gets to write-back data
    # to the file-system (e.g., what 'depmod' modified). This may lead to subsequent boot
    # problems. So sync the file-system now.
    pman.run_verify("sync")

def _create_standalone_python_script(script, pyhelperdir):
    """
    Create a standalone version of a python script 'script'. The 'pyhelperdir' argument is path to
    the python helper sources directory on the local host. The script hast to be aready installed
    installed on the local host.

    The 'script' depends on wult modules, but this function creates a single file version of it. The
    file will be an executable zip archive containing 'script' and all the wult dependencies it has.

    The resulting standalone script will be saved in 'pyhelperdir' under the 'script'.standalone
    name.
    """

    script_path = FSHelpers.which(script)
    deps = _get_pyhelper_dependencies(script_path)

    # Create an empty '__init__.py' file. We will be adding it to the sub-directories of the
    # depenencies. For example, if one of the dependencies is 'helperlibs/Trivial.py',
    # we'll have to add '__init__.py' to 'wultlibs/' and 'helperlibs'.
    init_path = pyhelperdir / "__init__.py"
    try:
        with init_path.open("w+"):
            pass
    except OSError as err:
        raise Error(f"failed to create file '{init_path}:\n{err}'") from None

    # pylint: disable=consider-using-with
    try:
        fobj = zipobj = None

        # Start creating the stand-alone version of the script: create an empty file and write
        # python shebang there.
        standalone_path = pyhelperdir / f"{script}.standalone"
        try:
            fobj = standalone_path.open("bw+")
            fobj.write("#!/usr/bin/python3\n".encode("utf8"))
        except OSError as err:
            raise Error(f"failed to create and initialize file '{standalone_path}:\n{err}") from err

        # Create a zip archive in the 'standalone_path' file. The idea is that this file will start
        # with python shebang, and then include compressed version the script and its dependencies.
        # Python interpreter is smart and can run such zip archives.
        try:
            zipobj = zipfile.ZipFile(fobj, "w", compression=zipfile.ZIP_DEFLATED)
        except Exception as err:
            raise Error(f"faild to initialize a zip archive from file "
                        f"'{standalone_path}':\n{err}") from err

        # Make 'zipobj' raies exceptions of typ 'Error', so that we do not have to wrap every
        # 'zipobj' operation into 'try/except'.
        zipobj = ClassHelpers.WrapExceptions(zipobj)

        # Put the script to the archive under the '__main__.py' name.
        zipobj.write(script_path, arcname="./__main__.py")

        pkgdirs = set()

        for src in deps:
            # Form the destination path. It is just part of the source path staring from the
            # 'wultlibs' of 'helperlibs' components.
            try:
                idx = src.parts.index("wultlibs")
            except ValueError:
                try:
                    idx = src.parts.index("helperlibs")
                except ValueError:
                    raise Error(f"script '{script}' has bad depenency '{src}' - the path does not "
                                f"have the 'wultlibs' or 'helperlibs' component in it.") from None

            dst = Path(*src.parts[idx:])
            zipobj.write(src, arcname=dst)

            # Collecect all directory paths present in the dependencies. They are all python
            # packages and we'll have to ensure we have the '__init__.py' file in each of the
            # sub-directory.
            pkgdir = dst.parent
            for idx, _ in enumerate(pkgdir.parts):
                pkgdirs.add(Path(*pkgdir.parts[:idx+1]))

        # Ensure the '__init__.py' file is present in all sub-directories.
        zipped_files = {Path(name) for name in zipobj.namelist()}
        for pkgdir in pkgdirs:
            path = pkgdir / "__init__.py"
            if path not in zipped_files:
                zipobj.write(init_path, arcname=pkgdir / "__init__.py")
    finally:
        if zipobj:
            zipobj.close()
        if fobj:
            fobj.close()
    # pylint: enable=consider-using-with

    # Make the standalone file executable.
    try:
        mode = standalone_path.stat().st_mode | 0o777
        standalone_path.chmod(mode)
    except OSError as err:
        raise Error(f"cannot change '{standalone_path}' file mode to {oct(mode)}:\n{err}") from err

def _deploy_helpers(args, pman):
    """Deploy helpers (including python helpers) to the SUT represented by 'pman'."""

    # Python helpers need to be deployd only to a remote host. The local host already has them
    # deployed by 'setup.py'.
    if not pman.is_remote:
        args.pyhelpers = []

    helpers = args.helpers + args.pyhelpers
    if not helpers:
        return

    # We assume all helpers are in the same base directory.
    helper_path = _HELPERS_SRC_SUBPATH/f"{helpers[0]}"
    helpersrc = find_app_data("wult", helper_path, descr=f"{args.toolname} helper sources")
    helpersrc = helpersrc.parent

    if not helpersrc.is_dir():
        raise Error(f"path '{helpersrc}' does not exist or it is not a directory")

    # Make sure all helpers are available.
    for helper in helpers:
        helperdir = helpersrc / helper
        if not helperdir.is_dir():
            raise Error(f"path '{helperdir}' does not exist or it is not a directory")

    # Copy python helpers to the temporary directory on the controller.
    for pyhelper in args.pyhelpers:
        srcdir = helpersrc / pyhelper
        _LOG.debug("copying helper %s:\n  '%s' -> '%s'", pyhelper, srcdir, args.ctmpdir)
        lpman = LocalProcessManager.LocalProcessManager()
        lpman.rsync(f"{srcdir}", args.ctmpdir, remotesrc=False, remotedst=False)

    # Build stand-alone version of every python helper.
    for pyhelper in args.pyhelpers:
        _LOG.info("Building a stand-alone version of '%s'", pyhelper)
        basedir = args.ctmpdir / pyhelper
        deployables = _get_deployables(basedir)
        for name in deployables:
            _create_standalone_python_script(name, basedir)

    # And copy the "standoline-ized" version of python helpers to the SUT.
    if pman.is_remote:
        for pyhelper in args.pyhelpers:
            srcdir = args.ctmpdir / pyhelper
            _LOG.debug("copying helper '%s' to %s:\n  '%s' -> '%s'",
                       pyhelper, pman.hostname, srcdir, args.stmpdir)
            pman.rsync(f"{srcdir}", args.stmpdir, remotesrc=False, remotedst=True)

    # Copy non-python helpers to the temporary directory on the SUT.
    for helper in args.helpers:
        srcdir = helpersrc/ helper
        _LOG.debug("copying helper '%s' to %s:\n  '%s' -> '%s'",
                   helper, pman.hostname, srcdir, args.stmpdir)
        pman.rsync(f"{srcdir}", args.stmpdir, remotesrc=False, remotedst=True)

    deploy_path = get_helpers_deploy_path(pman, args.toolname)

    # Build the non-python helpers on the SUT.
    if args.helpers:
        for helper in args.helpers:
            _LOG.info("Compiling helper '%s'%s", helper, pman.hostmsg)
            helperpath = f"{args.stmpdir}/{helper}"
            stdout, stderr = pman.run_verify(f"make -C '{helperpath}'")
            _log_cmd_output(args, stdout, stderr)

    # Make sure the the destination deployment directory exists.
    FSHelpers.mkdir(deploy_path, parents=True, exist_ok=True, pman=pman)

    # Deploy all helpers.
    _LOG.info("Deploying helpers to '%s'%s", deploy_path, pman.hostmsg)

    helpersdst = args.stmpdir / "helpers_deployed"
    _LOG.debug("deploying helpers to '%s'%s", helpersdst, pman.hostmsg)

    for helper in helpers:
        helperpath = f"{args.stmpdir}/{helper}"

        cmd = f"make -C '{helperpath}' install PREFIX='{helpersdst}'"
        stdout, stderr = pman.run_verify(cmd)
        _log_cmd_output(args, stdout, stderr)

        pman.rsync(str(helpersdst) + "/bin/", deploy_path, remotesrc=True, remotedst=True)

def _remove_deploy_tmpdir(args, pman, success=True):
    """Remove temporary files."""

    ctmpdir = getattr(args, "ctmpdir", None)
    stmpdir = getattr(args, "stmpdir", None)

    if args.debug and not success:
        _LOG.debug("preserved the following temporary directories for debugging purposes:")
        if ctmpdir:
            _LOG.debug(" * On the local host: %s", ctmpdir)
        if stmpdir and stmpdir != ctmpdir:
            _LOG.debug(" * On the SUT: %s", stmpdir)
    else:
        if ctmpdir:
            FSHelpers.rm_minus_rf(args.ctmpdir, pman=pman)
        if stmpdir:
            FSHelpers.rm_minus_rf(args.stmpdir, pman=pman)

def deploy_command(args):
    """Implements the 'deploy' command for the 'wult' and 'ndl' tools."""

    args.stmpdir = None # Temporary directory on the SUT.
    args.ctmpdir = None # Temporary directory on the controller (local host).

    if not FSHelpers.which("rsync", default=None):
        raise Error("please, install the 'rsync' tool")

    if not args.timeout:
        args.timeout = 8
    else:
        args.timeout = Trivial.str_to_num(args.timeout)
    if not args.username:
        args.username = "root"

    if args.privkey and not args.privkey.is_file():
        raise Error(f"path '{args.privkey}' does not exist or it is not a file")

    if args.pyhelpers:
        # Local temporary directory is only needed for creating stand-alone version of python
        # helpers.
        args.ctmpdir = FSHelpers.mktemp(prefix=f"{args.toolname}-")

    with ToolsCommon.get_pman(args) as pman:
        if not FSHelpers.which("make", default=None, pman=pman):
            raise Error(f"please, install the 'make' tool{pman.hostmsg}")

        if pman.is_remote or not args.ctmpdir:
            args.stmpdir = FSHelpers.mktemp(prefix=f"{args.toolname}-", pman=pman)
        else:
            args.stmpdir = args.ctmpdir

        success = True
        try:
            _deploy_drivers(args, pman)
            _deploy_helpers(args, pman)
        except:
            success = False
            raise
        finally:
            _remove_deploy_tmpdir(args, pman, success=success)
