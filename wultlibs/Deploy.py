# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API for deploying the 'wult' and 'ndl' tools.
"""

import os
import sys
import time
import logging
from pathlib import Path
from pepclibs.helperlibs import ProcessManager, LocalProcessManager, Trivial, Logging
from pepclibs.helperlibs import ClassHelpers, ArgParse
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
from wultlibs import ToolsCommon
from wultlibs.helperlibs import RemoteHelpers

_HELPERS_LOCAL_DIR = Path(".local")
_DRV_SRC_SUBPATH = Path("drivers/idle")
_HELPERS_SRC_SUBPATH = Path("helpers")

_LOG = logging.getLogger()

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

def _get_deployables(srcpath, pman=None):
    """
    Returns the list of "deployables" (driver names or helper tool names) provided by tools or
    drivers source code directory 'srcpath' on a host defined by 'pman'.
    """

    with ProcessManager.pman_or_local(pman) as wpman:
        cmd = f"make --silent -C '{srcpath}' list_deployables"
        deployables, _ = wpman.run_verify(cmd)
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
    with LocalProcessManager.LocalProcessManager() as lpman:
        stdout, _ = lpman.run_verify(cmd)
    return [Path(path) for path in stdout.splitlines()]

def _create_standalone_pyhelper(pyhelper, outdir):
    """
    Create a standalone version of a python program. The arguments are as follows.
      * pyhelper - name of the script to create the stand-alone version for. This script is supposed
                   to be already installed on the controller, and should be in 'PATH', This method
                   will execute it on the controller with the '--print-module-paths', which this
                   script is supposed to support. This option will provide the list of modules the
                   script depends on.
      * outdir - path to the output directory. The standalone version of the script will be saved in
                 this directory under the "'pyhelper'.standalone" name.
    """

    import zipfile # pylint: disable=import-outside-toplevel

    with LocalProcessManager.LocalProcessManager() as lpman:
        pyhelper_path = lpman.which(pyhelper)

    deps = _get_pyhelper_dependencies(pyhelper_path)

    # Create an empty '__init__.py' file. We will be adding it to the sub-directories of the
    # dependencies. For example, if one of the dependencies is 'helperlibs/Trivial.py', we'll have
    # to add '__init__.py' to 'wultlibs/' and 'helperlibs'.
    init_path = outdir / "__init__.py"
    try:
        with init_path.open("w+"):
            pass
    except OSError as err:
        raise Error(f"failed to create file '{init_path}:\n{err}'") from None

    try:
        # pylint: disable=consider-using-with
        fobj = zipobj = None

        # Start creating the stand-alone version of the python helper script: create an empty
        # file and write # python shebang there.
        standalone_path = outdir / f"{pyhelper}.standalone"
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

        # Make 'zipobj' raises exceptions of type 'Error', so that we do not have to wrap every
        # 'zipobj' operation into 'try/except'.
        zipobj = ClassHelpers.WrapExceptions(zipobj)

        # Put the python helper script to the archive under the '__main__.py' name.
        zipobj.write(pyhelper_path, arcname="./__main__.py")

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
                    raise Error(f"python helper script '{pyhelper}' has bad dependency '{src}' - "
                                f"the path does not have the 'wultlibs' or 'helperlibs' component "
                                f"in it.") from None

            dst = Path(*src.parts[idx:])
            zipobj.write(src, arcname=dst)

            # Collect all directory paths present in the dependencies. They are all python
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

    # Make the standalone file executable.
    try:
        mode = standalone_path.stat().st_mode | 0o777
        standalone_path.chmod(mode)
    except OSError as err:
        raise Error(f"cannot change '{standalone_path}' file mode to {oct(mode)}:\n{err}") from err


class Deploy(ClassHelpers.SimpleCloseContext):
    """
    This module provides API for deploying the 'wult' and 'ndl' tools. Provides the following
    methods.

     * 'deploy()' - deploy everything (drivers, helper programs) to the SUT.
     * 'is_deploy_needed()' - check if re-deployment is needed.
     * 'add_cmdline_args()' - add deployment-related command line arguments.
    """

    def add_deploy_cmdline_args(self, subparsers, func, argcomplete=None):
        """
        Add the the 'deploy' command to 'argparse' data. The input arguments are as follows.
          * subparsers - the 'argparse' subparsers to add the 'deploy' command to.
          * func - the 'deploy' command handling function.
          * argcomplete - optional 'argcomplete' command-line arguments completer object.
        """

        what = ""
        if (self._shelpers or self._pyhelpers) and self._drivers:
            what = "helpers and drivers"
        elif self._shelpers or self._pyhelpers:
            what = "helpers"
        else:
            what = "drivers"

        envarname = f"{self._toolname.upper()}_DATA_PATH"
        searchdirs = [f"{Path(sys.argv[0]).parent}/%s",
                      f"${envarname}/%s (if '{envarname}' environment variable is defined)",
                      "$HOME/.local/share/wult/%s",
                      "/usr/local/share/wult/%s", "/usr/share/wult/%s"]

        text = f"Compile and deploy {self._toolname} {what}."
        descr = f"""Compile and deploy {self._toolname} {what} to the SUT (System Under Test), which
                    can be either local or a remote host, depending on the '-H' option."""
        if self._drivers:
            drvsearch = ", ".join([name % str(_DRV_SRC_SUBPATH) for name in searchdirs])
            descr += f"""The drivers are searched for in the following directories (and in the
                         following order) on the local host: {drvsearch}."""
        if self._shelpers or self._pyhelpers:
            helpersearch = ", ".join([name % str(_HELPERS_SRC_SUBPATH) for name in searchdirs])
            helpernames = ", ".join(self._shelpers + self._pyhelpers)
            descr += f"""The {self._toolname} tool also depends on the following helpers:
                         {helpernames}. These helpers will be compiled on the SUT and deployed to
                         the SUT. The sources of the helpers are searched for in the following paths
                         (and in the following order) on the local host: {helpersearch}. By default,
                         helpers are deployed to the path defined by the
                         {self._toolname.upper()}_HELPERSPATH environment variable. If the variable
                         is not defined, helpers are deployed to '$HOME/{_HELPERS_LOCAL_DIR}/bin',
                         where '$HOME' is the home directory of user 'USERNAME' on host 'HOST' (see
                         '--host' and '--username' options)."""
        parser = subparsers.add_parser("deploy", help=text, description=descr)

        if self._drivers:
            text = """Path to the Linux kernel sources to build the drivers against. The default is
                      '/lib/modules/$(uname -r)/build' on the SUT. In case of deploying to a remote
                      host, this is the path on the remote host (HOSTNAME)."""
            arg = parser.add_argument("--kernel-src", dest="ksrc", type=Path, help=text)
            if argcomplete:
                arg.completer = argcomplete.completers.DirectoriesCompleter()

        ArgParse.add_ssh_options(parser)

        parser.set_defaults(func=func)

    @staticmethod
    def _get_newest_mtime(paths):
        """Find and return the most recent modification time of files in paths 'paths'."""

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

    def _deployable_not_found(self, what):
        """Raise an exception in case a required driver or helper was not found on the SUT."""

        err = f"{what} was not found on {self._spman.hostmsg}. Please, run:\n" \
              f"{self._toolname} deploy"
        if self._spman.is_remote:
            err += f" -H {self._spman.hostname}"
        raise Error(err)

    def _get_module_path(self, name):
        """Return path to installed module 'name'. Returns 'None', if the module was not found."""

        cmd = f"modinfo -n {name}"
        stdout, _, exitcode = self._spman.run(cmd)
        if exitcode != 0:
            return None

        modpath = Path(stdout.strip())
        if self._spman.is_file(modpath):
            return modpath
        return None

    def get_helpers_deploy_path(self):
        """Return path to the helpers deployment directory on the SUT."""

        helpers_path = os.environ.get(f"{self._toolname.upper()}_HELPERSPATH")
        if not helpers_path:
            helpers_path = self._spman.get_homedir() / _HELPERS_LOCAL_DIR / "bin"
        return Path(helpers_path)

    def is_deploy_needed(self):
        """
        Wult and other tools require additional helper programs and drivers to be installed on the
        SUT. This method tries to analyze the SUT and figure out whether drivers and helper programs
        are installed on the SUT and are up-to-date.

        Returns 'True' if re-deployment is needed, and 'False' otherwise.
        """

        # Build the deploy information dictionary. Start with drivers.
        dinfos = {}
        srcpath = find_app_data("wult", _DRV_SRC_SUBPATH / self._toolname, appname=self._toolname)
        dstpaths = []
        for deployable in _get_deployables(srcpath):
            dstpath = self._get_module_path(deployable)
            if not dstpath:
                self._deployable_not_found(f"the '{deployable}' kernel module")
            dstpaths.append(self._get_module_path(deployable))
        dinfos["drivers"] = {"src" : [srcpath], "dst" : dstpaths}

        # Add non-python helpers' deploy information.
        if self._shelpers or self._pyhelpers:
            helpers_deploy_path = self.get_helpers_deploy_path()

        for shelper in self._shelpers:
            srcpath = find_app_data("wult", _HELPERS_SRC_SUBPATH / shelper,
                                    appname=self._toolname)
            dstpaths = []
            for deployable in _get_deployables(srcpath):
                dstpaths.append(helpers_deploy_path / deployable)
            dinfos[shelper] = {"src" : [srcpath], "dst" : dstpaths}

        # Add python helpers' deploy information. Note, python helpers are deployed only to the
        # remote host. The local copy of python helpers comes via 'setup.py'. Therefore, check them
        # only for the remote case.
        if self._pyhelpers and self._spman.is_remote:
            for pyhelper in self._pyhelpers:
                datapath = find_app_data("wult", _HELPERS_SRC_SUBPATH / pyhelper,
                                         appname=self._toolname)
                srcpaths = []
                dstpaths = []

                for deployable in _get_deployables(datapath, self._cpman):
                    if datapath.joinpath(deployable).exists():
                        # This case is relevant for running wult from sources - python helpers are
                        # in the 'helpers/pyhelper' directory.
                        srcpath = datapath
                    else:
                        # When wult is installed with 'pip', the python helpers go to the "bindir",
                        # and they are not installed to the data directory.
                        srcpath = self._cpman.which(deployable).parent

                    srcpaths += _get_pyhelper_dependencies(srcpath / deployable)
                    dstpaths.append(helpers_deploy_path / deployable)

                    dinfos[pyhelper] = {"src" : srcpaths, "dst" : dstpaths}

        # We are about to get timestamps for local and remote files. Take into account the possible
        # time shift between local and remote systems.
        time_delta = 0
        if self._spman.is_remote:
            time_delta = time.time() - RemoteHelpers.time_time(pman=self._spman)

        # Compare source and destination files' timestamps.
        for what, dinfo in dinfos.items():
            src = dinfo["src"]
            src_mtime = self._get_newest_mtime(src)
            for dst in dinfo["dst"]:
                try:
                    dst_mtime = self._spman.get_mtime(dst)
                except ErrorNotFound:
                    self._deployable_not_found(dst)

                if src_mtime > time_delta + dst_mtime:
                    src_str = ", ".join([str(path) for path in src])
                    _LOG.debug("%s src time %d + %d > dst_mtime %d\nsrc: %s\ndst %s",
                               what, src_mtime, time_delta, dst_mtime, src_str, dst)
                    return True

        return False

    def _log_cmd_output(self, stdout, stderr):
        """Print output of a command in case debugging is enabled."""

        if self._debug:
            if stdout:
                _LOG.log(Logging.ERRINFO, stdout)
            if stderr:
                _LOG.log(Logging.ERRINFO, stderr)

    def _prepare_shelpers(self, helpersrc):
        """
        Build and prepare simple helpers for deployment. The arguments are as follows:
          * helpersrc - path to the helpers base directory on the controller.
        """

        # Copy simple helpers to the temporary directory on the SUT.
        for shelper in self._shelpers:
            srcdir = helpersrc/ shelper
            _LOG.debug("copying simple helper '%s' to %s:\n  '%s' -> '%s'",
                       shelper, self._spman.hostname, srcdir, self._stmpdir)
            self._spman.rsync(f"{srcdir}", self._stmpdir, remotesrc=False,
                              remotedst=self._spman.is_remote)

        # Build non-python helpers on the SUT.
        for shelper in self._shelpers:
            _LOG.info("Compiling simple helper '%s'%s", shelper, self._spman.hostmsg)
            helperpath = f"{self._stmpdir}/{shelper}"
            stdout, stderr = self._spman.run_verify(f"make -C '{helperpath}'")
            self._log_cmd_output(stdout, stderr)

    def _prepare_pyhelpers(self, helpersrc):
        """
        Build and prepare python helpers for deployment. The arguments are as follows:
          * helpersrc - path to the helpers base directory on the controller.
        """

        # Copy python helpers to the temporary directory on the controller.
        for pyhelper in self._pyhelpers:
            srcdir = helpersrc / pyhelper
            _LOG.debug("copying python helper %s:\n  '%s' -> '%s'", pyhelper, srcdir, self._ctmpdir)
            self._cpman.rsync(f"{srcdir}", self._ctmpdir, remotesrc=False, remotedst=False)

        # Build stand-alone version of every python helper.
        for pyhelper in self._pyhelpers:
            _LOG.info("Building a stand-alone version of '%s'", pyhelper)
            basedir = self._ctmpdir / pyhelper
            deployables = _get_deployables(basedir)
            for name in deployables:
                _create_standalone_pyhelper(name, basedir)

        # And copy the "standoline-ized" version of python helpers to the SUT.
        if self._spman.is_remote:
            for pyhelper in self._pyhelpers:
                srcdir = self._ctmpdir / pyhelper
                _LOG.debug("copying python helper '%s' to %s:\n  '%s' -> '%s'",
                           pyhelper, self._spman.hostname, srcdir, self._stmpdir)
                self._spman.rsync(f"{srcdir}", self._stmpdir, remotesrc=False, remotedst=True)

    def _deploy_helpers(self):
        """Deploy helpers (including python helpers) to the SUT."""

        # Python helpers need to be deployed only to a remote host. The local host already has them
        # deployed by 'setup.py'.
        if not self._spman.is_remote:
            self._pyhelpers = []

        all_helpers = self._shelpers + self._pyhelpers
        if not all_helpers:
            return

        # We assume all helpers are in the same base directory.
        helper_path = _HELPERS_SRC_SUBPATH/f"{all_helpers[0]}"
        helpersrc = find_app_data("wult", helper_path, descr=f"{self._toolname} helper sources")
        helpersrc = helpersrc.parent

        if not helpersrc.is_dir():
            raise Error(f"path '{helpersrc}' does not exist or it is not a directory")

        # Make sure all helpers are available.
        for helper in all_helpers:
            helperdir = helpersrc / helper
            if not helperdir.is_dir():
                raise Error(f"path '{helperdir}' does not exist or it is not a directory")

        self._prepare_shelpers(helpersrc)
        self._prepare_pyhelpers(helpersrc)

        deploy_path = self.get_helpers_deploy_path()

        # Make sure the the destination deployment directory exists.
        self._spman.mkdir(deploy_path, parents=True, exist_ok=True)

        # Deploy all helpers.
        _LOG.info("Deploying helpers to '%s'%s", deploy_path, self._spman.hostmsg)

        helpersdst = self._stmpdir / "helpers_deployed"
        _LOG.debug("deploying helpers to '%s'%s", helpersdst, self._spman.hostmsg)

        for helper in all_helpers:
            helperpath = f"{self._stmpdir}/{helper}"

            cmd = f"make -C '{helperpath}' install PREFIX='{helpersdst}'"
            stdout, stderr = self._spman.run_verify(cmd)
            self._log_cmd_output(stdout, stderr)

            self._spman.rsync(str(helpersdst) + "/bin/", deploy_path,
                              remotesrc=self._spman.is_remote,
                              remotedst=self._spman.is_remote)

    def _deploy_drivers(self):
        """Deploy drivers to the SUT."""

        drvsrc = find_app_data("wult", _DRV_SRC_SUBPATH/f"{self._toolname}",
                               descr=f"{self._toolname} drivers sources")
        if not drvsrc.is_dir():
            raise Error(f"path '{drvsrc}' does not exist or it is not a directory")

        _LOG.debug("copying the drivers to %s:\n   '%s' -> '%s'",
                   self._spman.hostname, drvsrc, self._stmpdir)
        self._spman.rsync(f"{drvsrc}/", self._stmpdir / "drivers", remotesrc=False,
                          remotedst=self._spman.is_remote)
        drvsrc = self._stmpdir / "drivers"

        kmodpath = Path(f"/lib/modules/{self._kver}")
        if not self._spman.is_dir(kmodpath):
            raise Error(f"kernel modules directory '{kmodpath}' does not "
                        f"exist{self._spman.hostmsg}")

        # Build the drivers on the SUT.
        _LOG.info("Compiling the drivers%s", self._spman.hostmsg)
        cmd = f"make -C '{drvsrc}' KSRC='{self._ksrc}'"
        if self._debug:
            cmd += " V=1"

        stdout, stderr, exitcode = self._spman.run(cmd)
        if exitcode != 0:
            msg = self._spman.get_cmd_failure_msg(cmd, stdout, stderr, exitcode)
            if "synth_event_" in stderr:
                msg += "\n\nLooks like synthetic events support is disabled in your kernel, " \
                       "enable the 'CONFIG_SYNTH_EVENTS' kernel configuration option."
            raise Error(msg)

        self._log_cmd_output(stdout, stderr)

        # Deploy the drivers.
        dstdir = kmodpath / _DRV_SRC_SUBPATH
        self._spman.mkdir(dstdir, parents=True, exist_ok=True)

        for name in _get_deployables(drvsrc, self._spman):
            installed_module = self._get_module_path(name)
            srcpath = drvsrc / f"{name}.ko"
            dstpath = dstdir / f"{name}.ko"
            _LOG.info("Deploying driver '%s' to '%s'%s", name, dstpath, self._spman.hostmsg)
            self._spman.rsync(srcpath, dstpath, remotesrc=self._spman.is_remote,
                              remotedst=self._spman.is_remote)

            if installed_module and installed_module.resolve() != dstpath.resolve():
                _LOG.debug("removing old module '%s'%s", installed_module, self._spman.hostmsg)
                self._spman.run_verify(f"rm -f '{installed_module}'")

        stdout, stderr = self._spman.run_verify(f"depmod -a -- '{self._kver}'")
        self._log_cmd_output(stdout, stderr)

        # Potentially the deployed driver may crash the system before it gets to write-back data
        # to the file-system (e.g., what 'depmod' modified). This may lead to subsequent boot
        # problems. So sync the file-system now.
        self._spman.run_verify("sync")

    def deploy(self):
        """
        Deploy all the required material to the SUT (drivers, helpers, etc).

        We distinguish between 3 type of helper programs, or just helpers: simple helpers and python
        helpers.

        1. Simple helpers (shelpers) are stand-alone independent programs, which come in form of a
           single executable file.
        2. Python helpers (pyhelpers) are helper programs written in python. Unlike simple helpers,
           they are not totally independent, but they depend on various python modules. Deploying a
           python helpers is trickier because all python modules should also be deployed.
        """

        try:
            # Local temporary directory is required in these cases:
            #   1. We are deploying to the local host.
            #   2. We are deploying python helpers. Regardless of the target host, we need a local
            #      temporary directory for creating stand-alone versions of the helpers.
            if not self._spman.is_remote or self._pyhelpers:
                self._ctmpdir = self._cpman.mkdtemp(prefix=f"{self._toolname}-")

            if self._spman.is_remote:
                self._stmpdir = self._spman.mkdtemp(prefix=f"{self._toolname}-")
            else:
                self._stmpdir = self._ctmpdir
        except Exception as err:
            self._remove_tmpdirs()
            raise Error(f"failed to deploy the '{self._toolname}' tool: {err}") from err

        remove_tmpdirs = True
        try:
            self._deploy_drivers()
            self._deploy_helpers()
        except:
            if self._debug:
                remove_tmpdirs = False
            raise
        finally:
            self._remove_tmpdirs(remove_tmpdirs=remove_tmpdirs)

    def _init_kernel_info(self):
        """
        Discover kernel version and kernel sources path which will be needed for building the out of
        tree drivers. The arguments are as follows.
        """

        from wultlibs.helperlibs import KernelVersion # pylint: disable=import-outside-toplevel

        self._kver = None
        if not self._ksrc:
            self._kver = KernelVersion.get_kver(pman=self._spman)
            if not self._ksrc:
                self._ksrc = Path(f"/lib/modules/{self._kver}/build")
        else:
            self._ksrc = self._spman.abspath(self._ksrc)

        if not self._spman.is_dir(self._ksrc):
            raise Error(f"kernel sources directory '{self._ksrc}' does not "
                        f"exist{self._spman.hostmsg}")

        if not self._kver:
            self._kver = KernelVersion.get_kver_ktree(self._ksrc, pman=self._spman)

        _LOG.debug("Kernel sources path: %s", self._ksrc)
        _LOG.debug("Kernel version: %s", self._kver)

        ToolsCommon.check_kver(self._toolname, self._spman, kver=self._kver)

    def __init__(self, toolname, pman=None, debug=False):
        """
        The class constructor. The arguments are as follows.
          * toolname - name of the tool the command line arguments belong to.
          * pman - the process manager object that defines the SUT to deploy to (local host by
                   default).
          * debug - if 'True', be more verbose and do not remove the temporary directories in case
                    of a failure.
        """

        self._toolname = toolname
        self._spman = pman
        self._debug = debug

        self._close_spman = pman is None

        self._cpman = None   # Process manager associated with the controller (local host).
        self._stmpdir = None # Temporary directory on the SUT.
        self._ctmpdir = None # Temporary directory on the controller (local host).
        self._kver = None    # Version of the kernel to compile the drivers for.
        self._ksrc = None    # Path to the kernel sources to compile the drivers for.

        self._drivers = None
        self._shelpers = []
        self._pyhelpers = []

        self._cpman = LocalProcessManager.LocalProcessManager()
        if not self._spman:
            self._spman = self._cpman

        if self._toolname == "wult":
            self._drivers = True
            self._pyhelpers = ["stats-collect"]
        elif self._toolname == "ndl":
            self._drivers = True
            self._shelpers = ["ndlrunner"]
        else:
            raise Error(f"BUG: unsupported tool '{toolname}'")

        self._init_kernel_info()

    def _remove_tmpdirs(self, remove_tmpdirs=True):
        """
        Remove temporary directories. The arguments are as follows.
          * remove_tmpdirs - remove temporary directories if 'True', preserve them otherwise.
        """

        spman = getattr(self, "_spman", None)
        cpman = getattr(self, "_cpman", None)
        if not cpman or not spman:
            return

        ctmpdir = getattr(self, "_ctmpdir", None)
        stmpdir = getattr(self, "_stmpdir", None)

        if remove_tmpdirs:
            if stmpdir:
                spman.rmtree(self._stmpdir)
            if ctmpdir and ctmpdir is not stmpdir:
                cpman.rmtree(self._ctmpdir)
        else:
            _LOG.info("Preserved the following temporary directories for debugging purposes:")
            if stmpdir:
                _LOG.info(" * On the SUT (%s): %s", spman.hostname, stmpdir)
            if ctmpdir and ctmpdir is not stmpdir:
                _LOG.info(" * On the controller (%s): %s", cpman.hostname, ctmpdir)

    def close(self):
        """Uninitialize the object."""
        ClassHelpers.close(self, close_attrs=("_cpman", "_spman"))
