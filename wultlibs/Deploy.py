# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API for deploying the tools coming with the 'wult' project.

Terminology.
  * category - type of an installable. Currently there are 4 categories: drivers, simple helpers
               (shelpers), python helpers (pyhelpers), and eBPF helpers (bpfhelpers).
  * installable - a sub-project to install on the SUT.
  * deployable - each installable provides one or multiple deployables. For example, wult tool has
                 an installable called "wult driver". This is not really a single driver, this is a
                 directory, which includes multiple drivers (kernel modules). Each kernel module is
                 a deployable.

Installable vs deployable.
  * Installables come in the form of source code. Deployables are executable programs (script,
    binary) or kernel drivers.
  * An installable corresponds to a directory with source code. The source code may need to be
    compiled. The compilation results in one or several deployables.
  * Deployables are ultimately copied to the SUT and executed on the SUT.

Note, "wult" is both name of the project and name of the tool in the project.
"""

import os
import sys
import time
import logging
from pathlib import Path
from pepclibs.helperlibs import LocalProcessManager, Logging
from pepclibs.helperlibs import ClassHelpers, ArgParse, ToolChecker
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound, ErrorExists, ErrorNotSupported
from statscollectlibs.helperlibs import ToolHelpers
from wultlibs.helperlibs import RemoteHelpers, KernelVersion
from wultlibs import _DeployPyHelpers, _DeploySHelpers

_DRV_SRC_SUBPATH = Path("drivers/idle")

_LOG = logging.getLogger()

# The supported installable categories.
_CATEGORIES = { "drivers"    : "kernel driver",
                "shelpers"   : "simple helper program",
                "pyhelpers"  : "python helper program",
                "bpfhelpers" : "eBPF helper program"}

def _get_deploy_cmd(pman, toolname):
    """Returns the 'deploy' command suggestion string."""

    cmd = f"{toolname} deploy"
    if pman.is_remote:
        cmd += f" -H {pman.hostname}"
    return cmd

def _deployable_not_found(pman, toolname, what, is_helper=True):
    """Raise an exception in case a required driver or helper was not found."""

    err = f"{what} was not found{pman.hostmsg}"
    if is_helper:
        err += f". Here are the options to try.\n" \
               f" * Run '{_get_deploy_cmd(pman, toolname)}'.\n" \
               f" * Ensure that {what} is in 'PATH'{pman.hostmsg}.\n" \
               f" * Set the 'WULT_HELPERSPATH' environment variable to the path of " \
               f"{what}{pman.hostmsg}"
    else:
        err += f"\nConsider running '{_get_deploy_cmd(pman, toolname)}'"

    raise ErrorNotFound(err)

def get_installed_helper_path(pman, toolname, helper):
    """
    Tries to figure out path to the directory the 'helper' program is installed at. Returns the
    path in case of success (e.g., '/usr/bin') and raises the 'ErrorNotFound' an exception if the
    helper was not found.
    """

    dirpath = os.environ.get("WULT_HELPERSPATH")
    if dirpath:
        helper_path = Path(dirpath) / helper
        if pman.is_exe(helper_path):
            return helper_path

    helper_path = pman.which(helper, must_find=False)
    if helper_path:
        return helper_path

    # Check standard paths.
    homedir = pman.get_homedir()
    stardard_paths = (f"{homedir}/.local/bin", "/usr/bin", "/usr/local/bin", "/bin",
                      f"{homedir}/bin")

    for dirpath in stardard_paths:
        helper_path = Path(dirpath) / helper
        if pman.is_exe(helper_path):
            return helper_path


    return _deployable_not_found(pman, toolname, f"the '{helper}' program", is_helper=True)

def add_deploy_cmdline_args(toolname, deploy_info, subparsers, func, argcomplete=None):
    """
    Add the the 'deploy' command to 'argparse' data. The input arguments are as follows.
      * toolname - name of the tool to add the 'deploy' command for.
      * deploy_info - a dictionary describing the tool to deploy, same as in
                      '_DeployBase.__init__()'.
      * subparsers - the 'argparse' subparsers to add the 'deploy' command to.
      * func - the 'deploy' command handling function.
      * argcomplete - optional 'argcomplete' command-line arguments completer object.
    """

    cats = { cat : [] for cat in _CATEGORIES }
    for name, info in deploy_info["installables"].items():
        cats[info["category"]].append(name)

    what = ""
    if cats["shelpers"] or cats["pyhelpers"] or cats["bpfhelpers"]:
        if cats["drivers"]:
            what = "helpers and drivers"
        else:
            what = "helpers"
    elif cats["drivers"]:
        what = "drivers"
    else:
        raise Error("BUG: no helpers and no drivers")

    searchdirs = [f"{Path(sys.argv[0]).parent}/%s",
                  "$WULT_DATA_PATH/%s (if 'WULT_DATA_PATH' environment variable is defined)",
                  "$HOME/.local/share/wult/%s",
                  "/usr/local/share/wult/%s", "/usr/share/wult/%s"]

    text = f"Compile and deploy {toolname} {what}."
    descr = f"""Compile and deploy {toolname} {what} to the SUT (System Under Test), which can be
                can be either local or a remote host, depending on the '-H' option. By default,
                everything is built on the SUT, but the '--local-build' can be used for building
                on the local system."""

    if cats["drivers"]:
        drvsearch = ", ".join([name % str(_DRV_SRC_SUBPATH) for name in searchdirs])
        descr += f""" The drivers are searched for in the following directories (and in the
                     following order) on the local host: {drvsearch}."""
    if cats["shelpers"] or cats["pyhelpers"]:
        dirs = [name % str(_DeployPyHelpers.HELPERS_SRC_SUBPATH) for name in searchdirs]
        helpersearch = ", ".join(dirs)
        helpernames = ", ".join(cats["shelpers"] + cats["pyhelpers"] + cats["bpfhelpers"])
        descr += f"""The {toolname} tool also depends on the following helpers: {helpernames}.
                     These helpers will be compiled on the SUT and deployed to the SUT. The sources
                     of the helpers are searched for in the following paths (and in the following
                     order) on the local host: {helpersearch}. By default, helpers are deployed to
                     the path defined by the 'WULT_HELPERSPATH' environment variable. If the
                     variable is not defined, helpers are deployed to
                     '$HOME/{_DeployPyHelpers.HELPERS_LOCAL_DIR}/bin', where '$HOME' is the home
                     directory of user 'USERNAME' on host 'HOST' (see '--host' and '--username'
                     options)."""
    parser = subparsers.add_parser("deploy", help=text, description=descr)

    if cats["drivers"] or cats["bpfhelpers"]:
        text = """Path to the Linux kernel sources to build drivers and eBPF helpers against. The
                  default is '/lib/modules/$(uname -r)/build' on the SUT. If '--local-build' was
                  used, then the path is considered to be on the local system, rather than the
                  SUT."""
        arg = parser.add_argument("--kernel-src", dest="ksrc", type=Path, help=text)
        if argcomplete:
            arg.completer = argcomplete.completers.DirectoriesCompleter()

    if cats["bpfhelpers"]:
        text = """eBPF helpers sources consist of 2 components: the user-space component and the
                  eBPF component. The user-space component is distributed as a source code, and must
                  be compiled. The eBPF component is distributed as both source code and in binary
                  (compiled) form. By default, the eBPF component is not re-compiled. This option is
                  meant to be used by wult developers to re-compile the eBPF component if it was
                  modified."""
        parser.add_argument("--rebuild-bpf", action="store_true", help=text)

    text = f"""Build {what} locally, instead of building on HOSTNAME (the SUT)."""
    parser.add_argument("--local-build", dest="lbuild", action="store_true", help=text)

    text = f"""When '{toolname}' is deployed, a random temporary directory is used. Use this option
               provide a custom path instead. It will be used as a temporary directory on both
               local and remote hosts. This option is meant for debugging purposes."""
    arg = parser.add_argument("--tmpdir-path", help=text)
    if argcomplete:
        arg.completer = argcomplete.completers.DirectoriesCompleter()

    text = f"""Do not remove the temporary directories created while deploying '{toolname}'. This
               option is meant for debugging purposes."""
    parser.add_argument("--keep-tmpdir", action="store_true", help=text)

    ArgParse.add_ssh_options(parser)

    parser.set_defaults(func=func)
    return parser

class _DeployBase(ClassHelpers.SimpleCloseContext):
    """
    The base class for 'Deploy' and 'DeployCheck' classes. Contains the common bits and pieces.
    """

    def _get_kver(self):
        """Returns version of the kernel running on the SUT."""

        if not self._kver:
            self._kver = KernelVersion.get_kver(pman=self._spman)

        return self._kver

    def _check_minkver(self, installable):
        """
        Check if the SUT has new enough kernel version for 'installable' to be deployed on it. The
        argument are as follows.
          * installable - name of the installable to check the kernel version for.
        """

        minkver = self._insts[installable].get("minkver", None)
        if not minkver:
            return

        kver = self._get_kver()
        if KernelVersion.kver_lt(kver, minkver):
            cat_descr = _CATEGORIES[self._insts[installable]["category"]]
            raise ErrorNotSupported(f"version of Linux kernel{self._spman.hostmsg} is {kver}, and "
                                    f"it is not new enough for the '{installable}' {cat_descr}.\n"
                                    f"Please, use kernel version {minkver} or newer.")

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

    def __init__(self, toolname, deploy_info, pman=None):
        """
        The class constructor. The arguments are as follows.
          * toolname - name of the tool to create the deployment object for.
          * deploy_info - a dictionary describing the tool to deploy.
          * pman - the process manager object that defines the SUT to deploy to (local host by
                   default).

        The 'deploy_info' dictionary describes the tool to deploy and its dependencies. I should
        have the following structure.

        {
            "installables" : {
                Installable name 1 : {
                    "category" : category name of the installable ("drivers", "shelpers", etc).
                    "minkver"  : minimum SUT kernel version required for the installable.
                    "deployables" : list of deployables this installable provides.
                },
                Installable name 2 : {},
                ... etc for every installable ...
            }
        }

        Please, refer to module docstring for more information.
        """

        self._toolname = toolname
        self._deploy_info = deploy_info
        self._spman = pman

        self._close_spman = pman is None

        self._cpman = None # Process manager associated with the controller (local host).
        self._insts = {}   # Installables information.
        self._cats = {}    # Lists of installables in every category.

        # Version of the kernel running on the SUT of version of the kernel to compile wult
        # components against.
        self._kver = None

        self._cpman = LocalProcessManager.LocalProcessManager()
        if not self._spman:
            self._spman = self._cpman

        # Initialize installables and categories dictionaries.
        self._cats = { cat : {} for cat in _CATEGORIES }
        for name, info in self._deploy_info["installables"].items():
            self._insts[name] = info.copy()
            self._cats[info["category"]][name] = info.copy()

    def close(self):
        """Uninitialize the object."""
        ClassHelpers.close(self, close_attrs=("_spman"))

class DeployCheck(_DeployBase):
    """
    This class provides the 'check_deployment()' method which can be used for verifying whether all
    the required installables are available on the SUT.
    """

    @staticmethod
    def _get_newest_mtime(path):
        """Find and return the most recent modification time of files in paths 'paths'."""

        newest = 0
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
            raise Error(f"no files found in the '{path}'")
        return newest

    def _get_deployables(self, category):
        """Yields all deployable names for category 'category' (e.g., "drivers")."""

        for inst_info in self._cats[category].values():
            for deployable in inst_info["deployables"]:
                yield deployable

    def _get_installed_deployable_path(self, deployable):
        """Same as 'get_installed_helper_path()'."""
        return get_installed_helper_path(self._spman, self._toolname, deployable)

    def _get_installable_by_deployable(self, deployable):
        """Returns installable name and information dictionary for a deployable."""

        for installable, inst_info in self._insts.items():
            if deployable in inst_info["deployables"]:
                break
        else:
            raise Error(f"bad deployable name '{deployable}'")

        return installable # pylint: disable=undefined-loop-variable

    def _get_deployable_print_name(self, installable, deployable):
        """Returns a nice, printable human-readable name of a deployable."""

        cat_descr = _CATEGORIES[self._insts[installable]["category"]]
        if deployable != installable:
            return f"the '{deployable}' component of the '{installable}' {cat_descr}"
        return f"the '{deployable}' {cat_descr}"

    def _deployable_not_found(self, deployable):
        """Same as module-level '_deployable_not_found()'."""

        installable = self._get_installable_by_deployable(deployable)
        what = self._get_deployable_print_name(installable, deployable)
        is_helper = self._insts[installable]["category"] != "drivers"

        _deployable_not_found(self._spman, self._toolname, what, is_helper=is_helper)

    def _warn_deployable_out_of_date(self, deployable):
        """Print a warning about the 'what' deployable not being up-to-date."""

        installable = self._get_installable_by_deployable(deployable)
        what = self._get_deployable_print_name(installable, deployable)

        _LOG.warning("%s may be out of date%s\nConsider running '%s'",
                     what, self._spman.hostmsg, _get_deploy_cmd(self._spman, self._toolname))

    def _check_deployable_up_to_date(self, deployable, srcpath, dstpath):
        """
        Check that a deployable at 'dstpath' on SUT is up-to-date by comparing its 'mtime' to the
        source (code) of the deployable at 'srcpath' on the controller.
        """

        if self._time_delta is None:
            if self._spman.is_remote:
                # Take into account the possible time difference between local and remote
                # systems.
                self._time_delta = time.time() - RemoteHelpers.time_time(pman=self._spman)
            else:
                self._time_delta = 0

        src_mtime = self._get_newest_mtime(srcpath)
        dst_mtime = self._spman.get_mtime(dstpath)

        if src_mtime > self._time_delta + dst_mtime:
            _LOG.debug("src mtime %d > %d + dst mtime %d\nsrc: %s\ndst %s",
                       src_mtime, self._time_delta, dst_mtime, srcpath, dstpath)
            self._warn_deployable_out_of_date(deployable)

    def _check_drivers_deployment(self):
        """Check if drivers are deployed and up-to-date."""

        for drvname in self._cats["drivers"]:
            self._check_minkver(drvname)

            try:
                srcpath = ToolHelpers.find_project_data("wult", _DRV_SRC_SUBPATH / self._toolname,
                                                         descr=f"the '{drvname}' driver")
            except ErrorNotFound:
                srcpath = None

            for deployable in self._get_deployables("drivers"):
                dstpath = self._get_module_path(deployable)
                if not dstpath:
                    self._deployable_not_found(deployable)
                    break

                if srcpath:
                    self._check_deployable_up_to_date(deployable, srcpath, dstpath)

    def _check_helpers_deployment(self):
        """Check if simple and eBPF helpers are deployed and up-to-date."""

        for helpername in list(self._cats["shelpers"]) + list(self._cats["bpfhelpers"]):
            self._check_minkver(helpername)

            try:
                descr=f"the '{helpername}' helper program"
                subpath = _DeployPyHelpers.HELPERS_SRC_SUBPATH / helpername
                srcpath = ToolHelpers.find_project_data("wult", subpath, descr)
            except ErrorNotFound:
                srcpath = None

            for deployable in self._get_deployables("shelpers"):
                deployable_path = self._get_installed_deployable_path(deployable)
                if srcpath:
                    self._check_deployable_up_to_date(deployable, srcpath, deployable_path)

            for deployable in self._get_deployables("bpfhelpers"):
                deployable_path = self._get_installed_deployable_path(deployable)
                if srcpath:
                    self._check_deployable_up_to_date(deployable, srcpath, deployable_path)

    def _check_pyhelpers_deployment(self):
        """Check if python helpers are deployed and up-to-date."""

        for pyhelper in self._cats["pyhelpers"]:
            try:
                descr=f"the '{pyhelper}' python helper program"
                subpath = _DeployPyHelpers.HELPERS_SRC_SUBPATH / pyhelper
                srcpath = ToolHelpers.find_project_data("wult", subpath, descr)
            except ErrorNotFound:
                continue

            for deployable in self._get_deployables("pyhelpers"):
                try:
                    deployable_path = self._get_installed_deployable_path(deployable)
                except ErrorNotFound:
                    self._deployable_not_found(deployable)
                    break

                if srcpath:
                    self._check_deployable_up_to_date(deployable, srcpath, deployable_path)

    def check_deployment(self):
        """
        Wult and other tools require additional helper programs and drivers to be installed on the
        SUT. This method checks whether the required drivers and helper programs are installed on
        the SUT and are up-to-date.
        """

        self._time_delta = None

        if self._cats["drivers"]:
            self._check_drivers_deployment()
        if self._cats["shelpers"] or self._cats["bpfhelpers"]:
            self._check_helpers_deployment()
        if self._cats["pyhelpers"]:
            self._check_pyhelpers_deployment()

    def __init__(self, toolname, deploy_info, pman=None):
        """
        The class constructor. The arguments are as follows.
          * toolname - name of the tool to create the deployment object for.
          * deploy_info - a dictionary describing the tool to deploy. Check '_DeployBase.__init__()'
                          for more information.
          * pman - the process manager object that defines the SUT to deploy to (local host by
                   default).

        Please, refer to module docstring for more information.
        """

        super().__init__(toolname, deploy_info, pman=pman)

        self._time_delta = None


class Deploy(_DeployBase):
    """
    This module provides the 'deploy()' method which can be used for deploying the dependencies of
    the tools of the "wult" project.
    """

    def _get_stmpdir(self):
        """Creates a temporary directory on the SUT and returns its path."""

        if not self._stmpdir:
            self._stmpdir_created = True
            if not self._tmpdir_path:
                self._stmpdir = self._spman.mkdtemp(prefix=f"{self._toolname}-")
            else:
                self._stmpdir = self._tmpdir_path
                try:
                    self._spman.mkdir(self._stmpdir, parents=True, exist_ok=False)
                except ErrorExists:
                    self._stmpdir_created = False

        return self._stmpdir

    def _get_ctmpdir(self):
        """Creates a temporary directory on the controller and returns its path."""

        if not self._ctmpdir:
            self._ctmpdir_created = True
            if not self._tmpdir_path:
                self._ctmpdir = self._cpman.mkdtemp(prefix=f"{self._toolname}-")
            else:
                self._ctmpdir = self._tmpdir_path
                try:
                    self._cpman.mkdir(self._ctmpdir, parents=True, exist_ok=False)
                except ErrorExists:
                    self._ctmpdir_created = False
        return self._ctmpdir

    def _get_deployables(self, category):
        """Yields all deployable names for category 'category' (e.g., "drivers")."""

        for inst_info in self._cats[category].values():
            for deployable in inst_info["deployables"]:
                yield deployable

    def _log_cmd_output(self, stdout, stderr):
        """Print output of a command in case debugging is enabled."""

        if self._debug:
            if stdout:
                _LOG.log(Logging.ERRINFO, stdout)
            if stderr:
                _LOG.log(Logging.ERRINFO, stderr)

    def _get_kver(self):
        """
        Returns version of the kernel running on the SUT or version of the kernel in path to compile
        wult components against.
        """

        if self._kver:
            return self._kver

        if not self._ksrc:
            self._kver = KernelVersion.get_kver(pman=self._spman)
        else:
            self._kver = KernelVersion.get_kver_ktree(self._ksrc, pman=self._bpman)

        _LOG.debug("Kernel version: %s", self._kver)
        return self._kver

    def _get_ksrc(self):
        """Return path to sources of the kernel to build wult components against."""

        if self._ksrc:
            return self._ksrc

        kver = self._get_kver()
        ksrc = Path(f"/lib/modules/{kver}/build")

        try:
            self._ksrc = self._bpman.abspath(ksrc)
        except ErrorNotFound as err:
            raise ErrorNotFound(f"cannot find kernel sources: '{ksrc}' does not "
                                f"exist{self._bpman.hostmsg}") from err

        _LOG.debug("Kernel sources path: %s", self._ksrc)
        return self._ksrc

    def _check_for_shared_library(self, soname):
        """
        Check if a shared library 'soname' is available on the build host. Returns if it is
        available, raises 'ErrorNotFound' otherwise.
        """

        _, stderr, _ = self._bpman.run(f"cc -l{soname}")
        if f"cannot find -l{soname}" in stderr:
            msg = f"The 'lib{soname}' library is not installed{self._bpman.hostmsg}"

            pkgname = self._tchk.tool_to_pkg(f"lib{soname}")
            if pkgname:
                msg += f"\nTry to install OS package '{pkgname}'."
            raise ErrorNotFound(msg)

    def _find_ebpf_include_dirs(self, headers):
        """
        eBPF helpers depend on various C header files from kernel source. The location of some of
        these files varies depending on kernel version and/or how the OS package places them. This
        method finds the locations of header files 'headers' and return the locations list.

        For example, Ubuntu 22.04 puts the 'bpf/bpf_helpers.h' file to '/usr/include', and it comes
        from the 'libbpf-dev' package, not from the kernel sources package. Fedora 36 delivers this
        vile via the kernel sources package.
        """

        search_info = {}

        # The search_info to use when searching in the kernel directory.
        #
        # Note, this list is crafted so that the 'include' subdirectory would go before the
        # 'usr/include' subdirectory. Otherwise the compilation breaks. And this only happens when
        # user ran 'make headers_install', so that 'usr/include' contains the "processed UAPI
        # headers".
        basedir = self._get_ksrc()
        search_info[basedir] = ("libbpf/include", "tools/lib", "tools/lib/bpf", "include",
                                "usr/include", "libbpf/include/bpf",
                                # Fedora-specific UAPI and libbpf include directories (the
                                # 'kernel-devel' module places them there).
                                "include/generated/uapi",
                                "tools/bpf/resolve_btfids/libbpf",
                                "tools/bpf/resolve_btfids/libbpf/include")

        # In case of Ubuntu some bpf headers are in '/usr/include', and they are delivered via the
        # 'libbpf-dev' package.
        basedir = Path("/usr/include")
        if self._bpman.is_dir(basedir):
            search_info[basedir] = ("", )

        incdirs = set()

        for header in headers:
            tried = []

            for basedir, suffixes in search_info.items():
                found = False
                for sfx in suffixes:
                    incdir = basedir / sfx
                    tried.append(incdir)
                    if self._bpman.is_file(incdir / header):
                        incdirs.add(incdir)
                        found = True
                        break
                if found:
                    break
            else:
                tried = "\n * ".join([str(path) for path in tried])
                err = f"failed to find C header file '{header}'.\nTried the following paths" \
                      f"{self._bpman.hostmsg}:\n* {tried}"

                # In Ubuntu, the '/usr/include/asm/types.h' file does not exist unless the
                # 'gcc-multilib' package is installed. Include this information to the error
                # message.
                if header == "asm/types.h" and self._tchk.get_osname() == "Ubuntu":
                    err += "\nTry to install the 'gcc-multilib' Ubuntu package"

                raise ErrorNotFound(err)

        return incdirs

    def _find_or_build_libbpf_a_from_ksrc(self):
        """
        The searches for 'libbpf.a' (static libbpf library) in the kernel sources and returns its
        path. If 'libbpf.a' was not found, this method compiles it in the kernel sources and
        returns the path to 'libbpf.a'.
        """

        ksrc = self._get_ksrc()

        # The location of 'libbpf.a' in kernel sources may vary, check several known paths.
        suffixes = ("tools/lib/bpf", "tools/bpf/resolve_btfids/libbpf", "libbpf")
        tried_paths = []

        for sfx in suffixes:
            path = ksrc / sfx / "libbpf.a"
            tried_paths.append(path)
            if self._bpman.is_file(path):
                return path

        tried = "\n * ".join([str(path) for path in tried_paths])
        msg = f"failed to find 'libbpf.a', tried these paths{self._bpman.hostmsg}:\n * {tried}\n" \
              f"Trying to compile it."

        # Try to compile 'libbpf.a'. It requires 'libelf'.
        self._check_for_shared_library("elf")

        cmd = f"make -C '{ksrc}/tools/lib/bpf'"
        self._bpman.run_verify(cmd)

        path = f"{ksrc}/tools/lib/bpf/libbpf.a"
        if self._bpman.is_file(path):
            return path

        raise ErrorNotFound(f"{msg}\nCompiled 'libbpf.a', but it was still not found in " \
                            f"'{path}'{self._bpman.hostmsg}")

    def _prepare_bpfhelpers(self, helpersrc, bpfhelpers, log_cmd_func, lbuild, rebuild_bpf):
        """
        Build and prepare eBPF helpers for deployment. The arguments are as follows:
          * helpersrc - path to the helpers base directory on the controller.
          * bpfhelpers - bpf helpers to deploy.
          * log_cmd_func - a function with signature 'log_cmd_func(stdout, stderr)' which will log
                           stdout and stderr accordingly.
          * lbuild - boolean value representing whether this method should build locally.
          * rebuild_src - boolean value representing whether this method should rebuild bpf helpers.
        """

        # Copy eBPF helpers to the temporary directory on the build host.
        for bpfhelper in bpfhelpers:
            srcdir = helpersrc / bpfhelper
            _LOG.debug("copying eBPF helper '%s' to %s:\n  '%s' -> '%s'",
                       bpfhelper, self._bpman.hostname, srcdir, self._btmpdir)
            self._bpman.rsync(srcdir, self._btmpdir, remotesrc=False,
                              remotedst=self._bpman.is_remote)

        if rebuild_bpf:
            ksrc = self._get_ksrc()

            # In order to compile the eBPF components of eBPF helpers, the build host must have
            # 'clang' and 'bpftool' available. These tools are used from the 'Makefile'. Let's check
            # for them in order to generate a user-friendly message if one of them is not installed.

            clang_path = self._tchk.check_tool("clang")

            # Check if kernel sources provide 'bpftool' first. The user could have compiled it in
            # the kernel tree. Use it, if so.
            bpftool_path = None
            for path in ("bpftool", "tools/bpf/bpftool/bpftool"):
                if self._bpman.is_file(ksrc / path):
                    bpftool_path = ksrc / path
                    break
            if not bpftool_path:
                bpftool_path = self._tchk.check_tool("bpftool")

            headers = ("bpf/bpf_helpers.h", "bpf_helper_defs.h", "bpf/bpf_tracing.h",
                       "uapi/linux/bpf.h", "linux/version.h", "asm/types.h")
            incdirs = self._find_ebpf_include_dirs(headers)
            bpf_inc = "-I " + " -I ".join([str(incdir) for incdir in incdirs])

            # Build the eBPF components of eBPF helpers.
            for bpfhelper in bpfhelpers:
                _LOG.info("Compiling the eBPF component of '%s'%s", bpfhelper, self._bpman.hostmsg)
                cmd = f"make -C '{self._btmpdir}/{bpfhelper}' KSRC='{ksrc}' CLANG='{clang_path}' " \
                      f"BPFTOOL='{bpftool_path}' BPF_INC='{bpf_inc}' bpf"
                stdout, stderr = self._bpman.run_verify(cmd)
                log_cmd_func(stdout, stderr)

        libbpf_path, u_inc = None, None
        if lbuild:
            # We are building on a local system for a remote host. Everything should come from
            # kernel sources in this case: 'libbpf.a' and 'bpf/bpf.h'.
            libbpf_path = self._find_or_build_libbpf_a_from_ksrc()
            incdirs = self._find_ebpf_include_dirs(("bpf/bpf.h", ))
            u_inc = "-I " + " -I ".join([str(incdir) for incdir in incdirs])
        else:
            # We are building on the SUT for the kernel running on the SUT. In this case we assume
            # that libbpf is installed on the system via an OS kernel package, and we use the shared
            # 'libbpf' library.
            self._check_for_shared_library("bpf")

        # Build eBPF helpers.
        for bpfhelper in bpfhelpers:
            _LOG.info("Compiling eBPF helper '%s'%s", bpfhelper, self._bpman.hostmsg)
            cmd = f"make -C '{self._btmpdir}/{bpfhelper}'"
            if libbpf_path:
                # Note, in case of static libbpf library, we have to specify 'libelf' adn 'libz'
                # linker flags, because 'libbpf.a' requires them.
                cmd += f" LIBBPF='{libbpf_path}' U_INC='{u_inc}' LDFLAGS='-lz -lelf'"
            stdout, stderr = self._bpman.run_verify(cmd)
            log_cmd_func(stdout, stderr)

    def _get_helpers_deploy_path(self):
        """Returns path the directory the helpers should be deployed to."""

        helpers_path = os.environ.get("WULT_HELPERSPATH")
        if not helpers_path:
            helpers_path = self._spman.get_homedir() / _DeployPyHelpers.HELPERS_LOCAL_DIR / "bin"
        return Path(helpers_path)

    def _deploy_helpers(self):
        """Deploy helpers (including python helpers) to the SUT."""

        all_helpers = list(self._cats["shelpers"]) + list(self._cats["pyhelpers"]) + \
                      list(self._cats["bpfhelpers"])
        if not all_helpers:
            return

        # We assume all helpers are in the same base directory.
        helper_path = _DeployPyHelpers.HELPERS_SRC_SUBPATH/f"{all_helpers[0]}"
        helpersrc = ToolHelpers.find_project_data("wult", helper_path,
                                                  descr=f"{self._toolname} helper sources")
        helpersrc = helpersrc.parent

        if not helpersrc.is_dir():
            raise Error(f"path '{helpersrc}' does not exist or it is not a directory")

        # Make sure all helpers are available.
        for helper in all_helpers:
            helperdir = helpersrc / helper
            if not helperdir.is_dir():
                raise Error(f"path '{helperdir}' does not exist or it is not a directory")

        if self._cats["shelpers"]:
            dep_shelper = _DeploySHelpers.DeploySHelpers(self._bpman, self._btmpdir)
            dep_shelper.prepare_shelpers(helpersrc, self._cats["shelpers"], self._log_cmd_output)
        if self._cats["pyhelpers"]:
            dep_pyhelper = _DeployPyHelpers.DeployPyHelpers(self._cpman, self._spman, self._stmpdir)
            dep_pyhelper.prepare_pyhelpers(helpersrc, self._cats["pyhelpers"],
                                           self._get_deployables("pyhelpers"), self._get_ctmpdir())
        if self._cats["bpfhelpers"]:
            self._prepare_bpfhelpers(helpersrc, self._cats["bpfhelpers"], self._log_cmd_output,
                                     self._tchk, self._get_ksrc())

        deploy_path = self._get_helpers_deploy_path()

        # Make sure the the destination deployment directory exists.
        self._spman.mkdir(deploy_path, parents=True, exist_ok=True)

        # Deploy all helpers.
        _LOG.info("Deploying helpers to '%s'%s", deploy_path, self._spman.hostmsg)

        helpersdst = self._stmpdir / "helpers_deployed"
        _LOG.debug("deploying helpers to '%s'%s", helpersdst, self._spman.hostmsg)

        for helper in all_helpers:
            bhelperpath = f"{self._btmpdir}/{helper}"
            shelperpath = f"{self._stmpdir}/{helper}"

            if self._lbuild and self._spman.is_remote:
                # We built the helpers locally, but have to install them on a remote SUT. Copy them
                # to the SUT first.
                self._spman.rsync(str(bhelperpath) + "/", shelperpath,
                                  remotesrc=self._bpman.is_remote, remotedst=self._spman.is_remote)

            cmd = f"make -C '{shelperpath}' install PREFIX='{helpersdst}'"
            stdout, stderr = self._spman.run_verify(cmd)
            self._log_cmd_output(stdout, stderr)

            self._spman.rsync(str(helpersdst) + "/bin/", deploy_path,
                              remotesrc=self._spman.is_remote,
                              remotedst=self._spman.is_remote)

    def _deploy_drivers(self):
        """Deploy drivers to the SUT."""

        if not self._cats["drivers"]:
            return

        kver = self._get_kver()
        ksrc = self._get_ksrc()

        for drvname in self._cats["drivers"]:
            drvsrc = ToolHelpers.find_project_data("wult", _DRV_SRC_SUBPATH / drvname,
                                                   descr=f"{drvname} drivers sources")
            if not drvsrc.is_dir():
                raise Error(f"path '{drvsrc}' does not exist or it is not a directory")

            _LOG.debug("copying driver sources to %s:\n   '%s' -> '%s'",
                       self._bpman.hostname, drvsrc, self._btmpdir)
            self._bpman.rsync(f"{drvsrc}/", self._btmpdir / "drivers", remotesrc=False,
                              remotedst=self._bpman.is_remote)
            drvsrc = self._btmpdir / "drivers"

            kmodpath = Path(f"/lib/modules/{kver}")
            if not self._spman.is_dir(kmodpath):
                raise Error(f"kernel modules directory '{kmodpath}' does not "
                            f"exist{self._spman.hostmsg}")

            # Build the drivers.
            _LOG.info("Compiling the drivers for kernel '%s'%s", kver, self._bpman.hostmsg)
            cmd = f"make -C '{drvsrc}' KSRC='{ksrc}'"
            if self._debug:
                cmd += " V=1"

            stdout, stderr, exitcode = self._bpman.run(cmd)
            if exitcode != 0:
                msg = self._bpman.get_cmd_failure_msg(cmd, stdout, stderr, exitcode)
                if "synth_event_" in stderr:
                    msg += "\n\nLooks like synthetic events support is disabled in your kernel, " \
                           "enable the 'CONFIG_SYNTH_EVENTS' kernel configuration option."
                raise Error(msg)

            self._log_cmd_output(stdout, stderr)

            # Deploy the drivers.
            dstdir = kmodpath / _DRV_SRC_SUBPATH
            self._spman.mkdir(dstdir, parents=True, exist_ok=True)

            for deployable in self._get_deployables("drivers"):
                installed_module = self._get_module_path(deployable)
                modname = f"{deployable}.ko"
                srcpath = drvsrc / modname
                dstpath = dstdir / modname
                _LOG.info("Deploying kernel module '%s'%s", modname, self._spman.hostmsg)
                _LOG.debug("Deploying kernel module '%s' to '%s'%s",
                           modname, dstpath, self._spman.hostmsg)
                self._spman.rsync(srcpath, dstpath, remotesrc=self._bpman.is_remote,
                                  remotedst=self._spman.is_remote)

                if installed_module and installed_module.resolve() != dstpath.resolve():
                    _LOG.debug("removing old module '%s'%s", installed_module, self._spman.hostmsg)
                    self._spman.run_verify(f"rm -f '{installed_module}'")

            stdout, stderr = self._spman.run_verify(f"depmod -a -- '{kver}'")
            self._log_cmd_output(stdout, stderr)

            # Potentially the deployed driver may crash the system before it gets to write-back data
            # to the file-system (e.g., what 'depmod' modified). This may lead to subsequent boot
            # problems. So sync the file-system now.
            self._spman.run_verify("sync")

    def _adjust_installables(self):
        """
        Adjust the list of installables that have to be deployed to the SUT based on various
        conditions, such as kernel version.
        """

        # Python helpers need to be deployed only to a remote host. The local host should already
        # have them:
        #   * either deployed via 'setup.py'.
        #   * or if running from source code, present in the source code.
        if not self._spman.is_remote:
            for installable in self._cats["pyhelpers"]:
                del self._insts[installable]
            self._cats["pyhelpers"] = {}

        # Exclude installables with unsatisfied minimum kernel version requirements.
        for installable in list(self._insts):
            try:
                self._check_minkver(installable)
            except ErrorNotSupported as err:
                cat = self._insts[installable]["category"]
                _LOG.notice(str(err))
                _LOG.warning("the '%s' %s can't be installed", installable, _CATEGORIES[cat])

                del self._insts[installable]
                del self._cats[cat][installable]

    def deploy(self):
        """
        Deploy all the required installables to the SUT (drivers, helpers, etc).

        We distinguish between 3 type of helper programs, or just helpers: simple helpers and python
        helpers.

        1. Simple helpers (shelpers) are stand-alone independent programs, which come in form of a
           single executable file.
        2. Python helpers (pyhelpers) are helper programs written in python. Unlike simple helpers,
           they are not totally independent, but they depend on various python modules. Deploying a
           python helpers is trickier because all python modules should also be deployed.
        """

        self._adjust_installables()

        try:
            if self._spman.is_remote:
                self._stmpdir = self._get_stmpdir()
            else:
                self._stmpdir = self._get_ctmpdir()

            if self._lbuild:
                self._btmpdir = self._get_ctmpdir()
            else:
                self._btmpdir = self._stmpdir
        except Exception as err:
            self._remove_tmpdirs()
            msg = Error(err).indent(2)
            raise Error(f"failed to deploy the '{self._toolname}' tool:\n{msg}") from err

        if self._cats["drivers"] or self._cats["shelpers"] or self._cats["bpfhelpers"]:
            # Make sure 'cc' is available on the build host - it'll be executed by 'Makefile', so an
            # explicit check here will generate an nice error message in case 'cc' is not available.
            self._tchk.check_tool("cc")

        try:
            self._deploy_drivers()
            self._deploy_helpers()
        finally:
            self._remove_tmpdirs()

    def __init__(self, toolname, deploy_info, pman=None, ksrc=None, lbuild=False, rebuild_bpf=False,
                 tmpdir_path=None, keep_tmpdir=False, debug=False):
        """
        The class constructor. The arguments are as follows.
          * toolname - name of the tool to create the deployment object for.
          * deploy_info - a dictionary describing the tool to deploy. Check '_DeployBase.__init__()'
                          for more information.
          * pman - the process manager object that defines the SUT to deploy to (local host by
                   default).
          * ksrc - path to the kernel sources to compile drivers against.
          * lbuild - by default, everything is built on the SUT, but if 'lbuild' is 'True', then
                     everything is built on the local host.
          * rebuild_bpf - if 'toolname' comes with an eBPF helper, re-build the the eBPF component
                           of the helper if this argument is 'True'. Do not re-build otherwise.
          * tmpdir_path - if provided, use this path as a temporary directory (by default, a random
                           temporary directory is created).
          * keep_tmpdir - if 'False', remove the temporary directory when finished. If 'True', do
                          not remove it.
          * debug - if 'True', be more verbose and do not remove the temporary directories in case
                    of a failure.

        Please, refer to module docstring for more information.
        """

        super().__init__(toolname, deploy_info, pman=pman)

        self._ksrc = ksrc
        self._lbuild = lbuild
        self._rebuild_bpf = rebuild_bpf
        self._tmpdir_path = tmpdir_path
        self._keep_tmpdir = keep_tmpdir
        self._debug = debug

        if self._tmpdir_path:
            self._tmpdir_path = Path(self._tmpdir_path)

        self._bpman = None   # Process manager associated with the build host.
        self._stmpdir = None # Temporary directory on the SUT.
        self._ctmpdir = None # Temporary directory on the controller (local host).
        self._btmpdir = None # Temporary directory on the build host.
        self._stmpdir_created = None # Temp. directory on the SUT has been created.
        self._ctmpdir_created = None # Temp. directory on the controller has been created.
        self._tchk = None

        if self._lbuild:
            self._bpman = self._cpman
        else:
            self._bpman = self._spman

        if self._ksrc:
            if not self._bpman.is_dir(self._ksrc):
                raise Error(f"kernel sources directory '{self._ksrc}' does not "
                            f"exist{self._bpman.hostmsg}")
            self._ksrc = self._bpman.abspath(self._ksrc)

        self._tchk = ToolChecker.ToolChecker(pman=self._bpman)

    def _remove_tmpdirs(self):
        """Remove temporary directories."""

        spman = getattr(self, "_spman", None)
        cpman = getattr(self, "_cpman", None)
        if not cpman or not spman:
            return

        ctmpdir = getattr(self, "_ctmpdir", None)
        stmpdir = getattr(self, "_stmpdir", None)

        if self._keep_tmpdir:
            _LOG.info("Preserved the following temporary directories:")
            if stmpdir:
                _LOG.info(" * On the SUT (%s): %s", spman.hostname, stmpdir)
            if ctmpdir and ctmpdir is not stmpdir:
                _LOG.info(" * On the controller (%s): %s", cpman.hostname, ctmpdir)
        else:
            if stmpdir and self._stmpdir_created:
                spman.rmtree(self._stmpdir)
            if ctmpdir and cpman is not spman and self._ctmpdir_created:
                cpman.rmtree(self._ctmpdir)

    def close(self):
        """Uninitialize the object."""

        ClassHelpers.close(self, close_attrs=("_tchk", "_cpman"), unref_attrs=("_bpman",))
        super().close()
