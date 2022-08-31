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
import contextlib
from pathlib import Path
from pepclibs.helperlibs import LocalProcessManager, Logging
from pepclibs.helperlibs import ClassHelpers, ArgParse, ToolChecker
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound, ErrorExists
from statscollectlibs.helperlibs import ToolHelpers
from wultlibs.helperlibs import RemoteHelpers, KernelVersion

_HELPERS_LOCAL_DIR = Path(".local")
_DRV_SRC_SUBPATH = Path("drivers/idle")
_HELPERS_SRC_SUBPATH = Path("helpers")

_LOG = logging.getLogger()

# The supported installable categories.
_CATEGORIES = { "drivers"    : "kernel driver",
                "shelpers"   : "simple helper program",
                "pyhelpers"  : "python helper program",
                "bpfhelpers" : "eBPF helper program"}

class _ErrorKVer(Error):
    """An exception class indicating that SUT kernel version is not new enough."""

def _get_deploy_cmd(pman, toolname):
    """Returns the 'deploy' command suggestion string."""

    cmd = f"{toolname} deploy"
    if pman.is_remote:
        cmd += f" -H {pman.hostname}"
    return cmd

def _deployable_not_found(pman, toolname, what, optional=False, is_helper=True):
    """Raise an exception in case a required driver or helper was not found."""

    if is_helper:
        what = f"the '{what}' program"

    err = f"{what} was not found{pman.hostmsg}"
    if is_helper and not optional:
        err += f".\nHere are the options to try.\n" \
               f"* Run '{_get_deploy_cmd(pman, toolname)}'.\n" \
               f"* Ensure that {what} is in 'PATH'{pman.hostmsg}.\n" \
               f"* Set the 'WULT_HELPERSPATH' environment variable to the path of " \
               f"{what}{pman.hostmsg}"

    if optional:
        _LOG.warning(err)
    else:
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

    return _deployable_not_found(pman, toolname, helper)

def _find_pyhelper_path(pyhelper, deployable=None):
    """
    Find and return path to python helper 'pyhelper' on the local system.
      * pyhelper - the python helper name.
      * deployable - name of the program to find.

    Note about 'pyhelper' vs 'deployable'. Python helpers may come with additional "deployables".
    For example, "stc-agent" comes with the 'ipmi-helper' tool that it uses. Here is a usage
    example.
      * To find path to the "stc-agent" python helper program, use:
        _find_pyhelper_path("stc-agent")
      * To find path to the "ipmi-helper" program which belongs to the "stc-agent" python helper,
        use:
        _find_pyhelper_path("stc-agent", deployable="ipmi-helper")
    """

    if not deployable:
        deployable = pyhelper

    with LocalProcessManager.LocalProcessManager() as lpman:
        try:
            pyhelper_path = lpman.which(deployable)
        except ErrorNotFound as err1:
            _LOG.debug(err1)

            try:
                subpath = _HELPERS_SRC_SUBPATH / pyhelper / deployable
                descr=f"the '{deployable}' python helper"
                pyhelper_path = ToolHelpers.find_project_data("wult", subpath, descr=descr)
            except ErrorNotFound as err2:
                errmsg = str(err1).capitalize() + "\n" + str(err2).capitalize()
                raise Error(f"failed to find '{pyhelper}' on the local system.\n{errmsg}") from err2

        pyhelper_path = lpman.abspath(pyhelper_path)

    return pyhelper_path

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
        descr += f"""The drivers are searched for in the following directories (and in the
                     following order) on the local host: {drvsearch}."""
    if cats["shelpers"] or cats["pyhelpers"]:
        helpersearch = ", ".join([name % str(_HELPERS_SRC_SUBPATH) for name in searchdirs])
        helpernames = ", ".join(cats["shelpers"] + cats["pyhelpers"] + cats["bpfhelpers"])
        descr += f"""The {toolname} tool also depends on the following helpers: {helpernames}.
                     These helpers will be compiled on the SUT and deployed to the SUT. The sources
                     of the helpers are searched for in the following paths (and in the following
                     order) on the local host: {helpersearch}. By default, helpers are deployed to
                     the path defined by the 'WULT_HELPERSPATH' environment variable. If the
                     variable is not defined, helpers are deployed to
                     '$HOME/{_HELPERS_LOCAL_DIR}/bin', where '$HOME' is the home directory of user
                     'USERNAME' on host 'HOST' (see '--host' and '--username' options)."""
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
                    "category" : category name of the installable ("driver", "shelper", etc).
                    "minkver"  : minimum SUT kernel version required for the installable.
                    "deployables" : list of deployables this installable provides.
                },
                Installable name 2 : {},
                ... etc for every installable ...
            }
        }

        Please, refer to module doctring for more information.
        """

        self._toolname = toolname
        self._deploy_info = deploy_info
        self._spman = pman

        self._close_spman = pman is None

        self._cpman = None # Process manager associated with the controller (local host).

        self._cpman = LocalProcessManager.LocalProcessManager()
        if not self._spman:
            self._spman = self._cpman

    def close(self):
        """Uninitialize the object."""
        ClassHelpers.close(self, close_attrs=("_spman"))

class DeployCheck(_DeployBase):
    """
    This module provides the 'check_deployment()' method which can be used for verifying whether all
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

    def _check_minkver(self, installable):
        """
        Check if the SUT has new enough kernel version for 'installable' to be deployed on it. The
        argument are as follows.
          * installable - name of the installable to check the kernel version for.
        """

        minkver = self._insts[installable].get("minkver", None)
        if not minkver:
            return

        if KernelVersion.kver_lt(self._kver, minkver):
            cat_descr = _CATEGORIES[self._insts[installable]["category"]]
            raise _ErrorKVer(f"version of Linux kernel{self._bpman.hostmsg} is {self._kver}, and "
                             f"it is not new enough for the '{installable}' {cat_descr}.\n"
                             f"Please, use kernel version {minkver} or newer.")

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
            except _ErrorKVer as err:
                cat = self._insts[installable]["category"]
                _LOG.notice(str(err))
                _LOG.warning("the '%s' %s can't be installed", installable, _CATEGORIES[cat])

                del self._insts[installable]
                del self._cats[cat][installable]

        # Either drivers or eBPF helpers are required.
        if not self._cats["drivers"] and not self._cats["bpfhelpers"]:
            # We have already printed the details, so we can have a short error message here.
            raise Error("please, use newer kernel")

    def _init_kernel_info(self, ksrc_required=False):
        """
        Discover kernel version and kernel sources path which will be needed for building the out of
        tree drivers. The arguments are as follows.
          * ksrc_required - if 'True', raises an exception if kernel sources were not found on the
                            build host (the SUT in all cases, except for the 'self._lbuild=True'
                            case).
        """

        self._kver = None
        if not self._ksrc:
            self._kver = KernelVersion.get_kver(pman=self._bpman)
            with contextlib.suppress(ErrorNotFound):
                ksrc_path = Path(f"/lib/modules/{self._kver}/build")
                self._ksrc = self._bpman.abspath(ksrc_path)
            if not self._ksrc and ksrc_required:
                raise Error(f"cannot find kernel sources: '{ksrc_path}' does not "
                            f"exist{self._bpman.hostmsg}")
        else:
            if not self._bpman.is_dir(self._ksrc):
                raise Error(f"kernel sources directory '{self._ksrc}' does not "
                            f"exist{self._bpman.hostmsg}")
            self._ksrc = self._bpman.abspath(self._ksrc)
            self._kver = KernelVersion.get_kver_ktree(self._ksrc, pman=self._bpman)

        if self._ksrc:
            _LOG.debug("Kernel sources path: %s", self._ksrc)
        else:
            _LOG.debug("Kernel sources path: not found%s", self._bpman.hostmsg)
        _LOG.debug("Kernel version: %s", self._kver)

    def _get_deployables(self, category):
        """Yields all deployable names for catergory 'category' (e.g., "drivers")."""

        for inst_info in self._cats[category].values():
            for deployable in inst_info["deployables"]:
                yield deployable

    def _get_installed_deployable_path(self, deployable):
        """Same as 'get_installed_helper_path()'."""
        return get_installed_helper_path(self._spman, self._toolname, deployable)

    def _deployable_not_found(self, deployable, optional=False, is_helper=True):
        """Same as module-level '_deployable_not_found()'."""
        _deployable_not_found(self._spman, self._toolname, deployable, optional=optional,
                              is_helper=is_helper)

    def _warn_deployable_out_of_date(self, what, is_helper=True):
        """Print a warning about the 'what' deployable not being up-to-date."""

        if is_helper:
            what = f"the '{what}' program"

        _LOG.warning("%s may be out of date%s, consider running '%s'",
                     what, self._spman.hostmsg, _get_deploy_cmd(self._spman, self._toolname))

    def _check_deployable_up_to_date(self, what, srcpath, dstpath, is_helper=True):
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
            self._warn_deployable_out_of_date(what, is_helper=is_helper)

    def _check_drivers_deployment(self, dev):
        """Check if drivers are deployed and up-to-date."""

        if not self._cats["drivers"]:
            # This must be because SUT kernel version is not new enough.
            raise Error(f"the '{dev.info['devid']}' device can't be used{self._spman.hostmsg}\n"
                        f"Reason: drivers cannot be installed.\n"
                        f"Please use newer kernel{self._spman.hostmsg}")

        try:
            srcpath = ToolHelpers.find_project_data("wult", _DRV_SRC_SUBPATH / self._toolname,
                                                     descr=f"the '{dev.drvname}' driver")
        except ErrorNotFound:
            srcpath = None

        for deployable in self._get_deployables("drivers"):
            dstpath = self._get_module_path(deployable)
            if not dstpath:
                self._deployable_not_found(f"the '{deployable}' kernel module", is_helper=False)

            if srcpath:
                what = f"the '{deployable}' kernel driver"
                self._check_deployable_up_to_date(what, srcpath, dstpath, is_helper=False)

    def _check_helpers_deployment(self, dev):
        """Check if simple and eBPF helpers are deployed and up-to-date."""

        if dev.helpername not in self._insts:
            # This must be because SUT kernel version is not new enough.
            cat = self._deploy_info["installables"][dev.helpername]["category"]
            cat_descr = _CATEGORIES[cat]
            raise Error(f"the '{dev.info['devid']}' device can't be used{self._spman.hostmsg}\n"
                        f"Reason: the '{dev.helpername}' {cat_descr} cannot be installed.\n"
                        f"Please use newer kernel{self._spman.hostmsg}")

        for helper in list(self._cats["shelpers"]) + list(self._cats["bpfhelpers"]):
            if helper != dev.helpername:
                continue

            try:
                descr=f"the '{dev.helpername}' helper program"
                srcpath = ToolHelpers.find_project_data("wult", _HELPERS_SRC_SUBPATH / helper,
                                                        descr=descr)
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
                datapath = ToolHelpers.find_project_data("wult", _HELPERS_SRC_SUBPATH / pyhelper,
                                                         descr)
            except ErrorNotFound:
                continue

            for deployable in self._get_deployables("pyhelpers"):
                try:
                    deployable_path = self._get_installed_deployable_path(deployable)
                except ErrorNotFound:
                    self._deployable_not_found(deployable, optional=True)
                    continue

                if not datapath:
                    continue

                if datapath.joinpath(deployable).exists():
                    # This case is relevant for running the tool from sources - python helpers
                    # are in the 'helpers/pyhelper' directory.
                    srcpath = datapath
                else:
                    # When the tool is installed with 'pip', python helpers get installed, and their
                    # sources are not avaliable in the data directory ('datapath').
                    try:
                        srcpath = get_installed_helper_path(self._cpman, self._toolname, deployable)
                        srcpath = srcpath.parent
                    except ErrorNotFound:
                        continue

                self._check_deployable_up_to_date(deployable, srcpath, deployable_path)

    def check_deployment(self, dev):
        """
        Wult and other tools require additional helper programs and drivers to be installed on the
        SUT. This method checks whether the required drivers and helper programs are installed on
        the SUT and are up-to-date. The arguments are as follows.
          * dev - the delayed event device object created by 'Devices.GetDevice()'.
        """

        self._init_kernel_info(ksrc_required=False)
        self._adjust_installables()

        self._time_delta = None

        if dev.drvname:
            self._check_drivers_deployment(dev)

        if dev.helpername:
            self._check_helpers_deployment(dev)

        if self._cats["pyhelpers"]:
            self._check_pyhelpers_deployment()

    def __init__(self, toolname, deploy_info, pman=None, ksrc=None, lbuild=False):
        """
        The class constructor. The arguments are as follows.
          * toolname - name of the tool to create the deployment object for.
          * deploy_info - a dictionary describing the tool to deploy.
          * pman - the process manager object that defines the SUT to deploy to (local host by
                   default).
          * ksrc - path to the kernel sources to compile drivers against.
          * lbuild - by default, everything is built on the SUT, but if 'lbuild' is 'True', then
                     everything is built on the local host.

        The 'deploy_info' dictionary describes the tool to deploy and its dependencies. I should
        have the following structure.

        {
            "installables" : {
                Installable name 1 : {
                    "category" : category name of the installable ("driver", "shelper", etc).
                    "minkver"  : minimum SUT kernel version required for the installable.
                    "deployables" : list of deployables this installable provides.
                },
                Installable name 2 : {},
                ... etc for every installable ...
            }
        }

        Please, refer to module doctring for more information.
        """

        super().__init__(toolname, deploy_info, pman=pman)

        self._ksrc = ksrc
        self._lbuild = lbuild

        self._bpman = None   # Process manager associated with the build host.
        self._kver = None # Version of the kernel to compile the drivers for (version of 'ksrc').

        self._time_delta = None

        # Installables information.
        self._insts = {}
        # Lists of installables in every category.
        self._cats = { cat : {} for cat in _CATEGORIES }

        for name, info in self._deploy_info["installables"].items():
            self._insts[name] = info.copy()
            self._cats[info["category"]] = { name : info.copy()}

        if self._lbuild:
            self._bpman = self._cpman
        else:
            self._bpman = self._spman

    def close(self):
        """Uninitialize the object."""

        ClassHelpers.close(self, close_attrs=("_cpman",), unref_attrs=("_bpman",))
        super().close()


class Deploy(_DeployBase):
    """
    This module provides the 'deploy()' method which can be used for deploying the depenencies of
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

    def _check_minkver(self, installable):
        """
        Check if the SUT has new enough kernel version for 'installable' to be deployed on it. The
        argument are as follows.
          * installable - name of the installable to check the kernel version for.
        """

        minkver = self._insts[installable].get("minkver", None)
        if not minkver:
            return

        if KernelVersion.kver_lt(self._kver, minkver):
            cat_descr = _CATEGORIES[self._insts[installable]["category"]]
            raise _ErrorKVer(f"version of Linux kernel{self._bpman.hostmsg} is {self._kver}, and "
                             f"it is not new enough for the '{installable}' {cat_descr}.\n"
                             f"Please, use kernel version {minkver} or newer.")

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
            except _ErrorKVer as err:
                cat = self._insts[installable]["category"]
                _LOG.notice(str(err))
                _LOG.warning("the '%s' %s can't be installed", installable, _CATEGORIES[cat])

                del self._insts[installable]
                del self._cats[cat][installable]

        # Either drivers or eBPF helpers are required.
        if not self._cats["drivers"] and not self._cats["bpfhelpers"]:
            # We have already printed the details, so we can have a short error message here.
            raise Error("please, use newer kernel")

    def _init_kernel_info(self, ksrc_required=False):
        """
        Discover kernel version and kernel sources path which will be needed for building the out of
        tree drivers. The arguments are as follows.
          * ksrc_required - if 'True', raises an exception if kernel sources were not found on the
                            build host (the SUT in all cases, except for the 'self._lbuild=True'
                            case).
        """

        self._kver = None
        if not self._ksrc:
            self._kver = KernelVersion.get_kver(pman=self._bpman)
            with contextlib.suppress(ErrorNotFound):
                ksrc_path = Path(f"/lib/modules/{self._kver}/build")
                self._ksrc = self._bpman.abspath(ksrc_path)
            if not self._ksrc and ksrc_required:
                raise Error(f"cannot find kernel sources: '{ksrc_path}' does not "
                            f"exist{self._bpman.hostmsg}")
        else:
            if not self._bpman.is_dir(self._ksrc):
                raise Error(f"kernel sources directory '{self._ksrc}' does not "
                            f"exist{self._bpman.hostmsg}")
            self._ksrc = self._bpman.abspath(self._ksrc)
            self._kver = KernelVersion.get_kver_ktree(self._ksrc, pman=self._bpman)

        if self._ksrc:
            _LOG.debug("Kernel sources path: %s", self._ksrc)
        else:
            _LOG.debug("Kernel sources path: not found%s", self._bpman.hostmsg)
        _LOG.debug("Kernel version: %s", self._kver)

    def _get_deployables(self, category):
        """Yields all deployable names for catergory 'category' (e.g., "drivers")."""

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

    def _prepare_shelpers(self, helpersrc):
        """
        Build and prepare simple helpers for deployment. The arguments are as follows:
          * helpersrc - path to the helpers base directory on the controller.
        """

        # Copy simple helpers to the temporary directory on the build host.
        for shelper in self._cats["shelpers"]:
            srcdir = helpersrc/ shelper
            _LOG.debug("copying simple helper '%s' to %s:\n  '%s' -> '%s'",
                       shelper, self._bpman.hostname, srcdir, self._btmpdir)
            self._bpman.rsync(srcdir, self._btmpdir, remotesrc=False,
                              remotedst=self._bpman.is_remote)

        # Build simple helpers.
        for shelper in self._cats["shelpers"]:
            _LOG.info("Compiling simple helper '%s'%s", shelper, self._bpman.hostmsg)
            helperpath = f"{self._btmpdir}/{shelper}"
            stdout, stderr = self._bpman.run_verify(f"make -C '{helperpath}'")
            self._log_cmd_output(stdout, stderr)

    @staticmethod
    def _get_pyhelper_dependencies(script_path):
        """
        Find and return a python helper script (pyhelper) dependencies. An example of such a
        dependency would be:
            /usr/lib/python3.9/site-packages/helperlibs/Trivial.py
        """

        # All pyhelpers implement the '--print-module-paths' option, which prints the dependencies.
        cmd = f"{script_path} --print-module-paths"
        with LocalProcessManager.LocalProcessManager() as lpman:
            stdout, _ = lpman.run_verify(cmd)
        return [Path(path) for path in stdout.splitlines()]

    def _create_standalone_pyhelper(self, pyhelper_path, outdir):
        """
        Create a standalone version of a python program. The arguments are as follows.
          * pyhelper_path - path to the python helper program on the local system. This method will
                            execute it on with the '--print-module-paths' option, which this it is
                            supposed to support. This option will provide the list of modules the
                            python helper program depends on.
          * outdir - path to the output directory. The standalone version of the script will be
                     saved in this directory under the "'pyhelper'.standalone" name.
        """

        import zipfile # pylint: disable=import-outside-toplevel

        pyhelper = pyhelper_path.name

        deps = self._get_pyhelper_dependencies(pyhelper_path)

        # Create an empty '__init__.py' file. We will be adding it to the sub-directories of the
        # dependencies. For example, if one of the dependencies is 'helperlibs/Trivial.py', we'll
        # have to add '__init__.py' to 'wultlibs/' and 'helperlibs'.
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
                raise Error(f"failed to create and initialize file '{standalone_path}:\n"
                            f"{err}") from err

            # Create a zip archive in the 'standalone_path' file. The idea is that this file will
            # start with python shebang, and then include compressed version the script and its
            # dependencies. Python interpreter is smart and can run such zip archives.
            try:
                zipobj = zipfile.ZipFile(fobj, "w", compression=zipfile.ZIP_DEFLATED)
            except Exception as err:
                raise Error(f"failed to initialize a zip archive from file "
                            f"'{standalone_path}':\n{err}") from err

            # Make 'zipobj' raises exceptions of type 'Error', so that we do not have to wrap every
            # 'zipobj' operation into 'try/except'.
            zipobj = ClassHelpers.WrapExceptions(zipobj)

            # Put the python helper script to the archive under the '__main__.py' name.
            zipobj.write(pyhelper_path, arcname="./__main__.py")

            pkgdirs = set()

            for src in deps:
                # Form the destination path. It is just part of the source path staring from the
                # 'statscollectlibs' of 'helperlibs' components.
                try:
                    idx = src.parts.index("statscollectlibs")
                except ValueError:
                    try:
                        idx = src.parts.index("helperlibs")
                    except ValueError:
                        raise Error(f"python helper script '{pyhelper}' has bad dependency '{src}' "
                                    f"- the path does not have the 'statscollectlibs' or "
                                    f"'helperlibs' component in it.") from None

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
            raise Error(f"cannot change '{standalone_path}' file mode to {oct(mode)}:\n"
                        f"{err}") from err

    def _prepare_pyhelpers(self, helpersrc):
        """
        Build and prepare python helpers for deployment. The arguments are as follows:
          * helpersrc - path to the helpers base directory on the controller.
        """

        ctmpdir = self._get_ctmpdir()

        # Copy python helpers to the temporary directory on the controller.
        for pyhelper in self._cats["pyhelpers"]:
            srcdir = helpersrc / pyhelper
            _LOG.debug("copying python helper %s:\n  '%s' -> '%s'", pyhelper, srcdir, ctmpdir)
            self._cpman.rsync(srcdir, ctmpdir, remotesrc=False, remotedst=False)

        # Build stand-alone version of every python helper.
        for pyhelper in self._cats["pyhelpers"]:
            _LOG.info("Building a stand-alone version of '%s'", pyhelper)
            basedir = ctmpdir / pyhelper
            for deployable in self._get_deployables("pyhelpers"):
                local_path = _find_pyhelper_path(pyhelper, deployable=deployable)
                self._create_standalone_pyhelper(local_path, basedir)

        # And copy the "standalone-ized" version of python helpers to the SUT.
        if self._spman.is_remote:
            for pyhelper in self._cats["pyhelpers"]:
                srcdir = ctmpdir / pyhelper
                _LOG.debug("copying python helper '%s' to %s:\n  '%s' -> '%s'",
                           pyhelper, self._spman.hostname, srcdir, self._stmpdir)
                self._spman.rsync(srcdir, self._stmpdir, remotesrc=False, remotedst=True)

    def _get_libbpf_path(self):
        """Search for 'libbpf.a' library in the kernel sources and return its path."""

        # The location of 'libbpf.a' may vary, check several known paths.
        path_suffixes = ("tools/lib/bpf", "tools/bpf/resolve_btfids/libbpf", "libbpf")
        tried_paths = []
        for path_sfx in path_suffixes:
            path = self._ksrc / path_sfx / "libbpf.a"
            tried_paths.append(str(path))
            if self._bpman.is_file(path):
                return path

        tried = "\n * ".join(tried_paths)
        raise ErrorNotFound(f"failed to find 'libbpf.a', tried the following paths"
                            f"{self._bpman.hostmsg}:\n * {tried}")

    def _build_libbpf(self):
        """Build 'libbpf.a' in the kernel sources."""

        cmd = f"make -C '{self._ksrc}/tools/lib/bpf'"
        self._bpman.run_verify(cmd)

    def _prepare_bpfhelpers(self, helpersrc):
        """
        Build and prepare eBPF helpers for deployment. The arguments are as follows:
          * helpersrc - path to the helpers base directory on the controller.
        """

        # Copy eBPF helpers to the temporary directory on the build host.
        for bpfhelper in self._cats["bpfhelpers"]:
            srcdir = helpersrc/ bpfhelper
            _LOG.debug("copying eBPF helper '%s' to %s:\n  '%s' -> '%s'",
                       bpfhelper, self._bpman.hostname, srcdir, self._btmpdir)
            self._bpman.rsync(srcdir, self._btmpdir, remotesrc=False,
                              remotedst=self._bpman.is_remote)

        if self._rebuild_bpf:
            # In order to compile the eBPF components of eBPF helpers, the build host must have
            # 'bpftool' and 'clang' available.

            # Check for the tools called from 'Makefile' here, in order to generate a user-friendly
            # message if one of them is not installed.
            bpftool_path = self._tchk.check_tool("bpftool")
            clang_path = self._tchk.check_tool("clang")

            # Build the eBPF components of eBPF helpers.
            for bpfhelper in self._cats["bpfhelpers"]:
                _LOG.info("Compiling the eBPF component of '%s'%s",
                          bpfhelper, self._bpman.hostmsg)
                cmd = f"make -C '{self._btmpdir}/{bpfhelper}' KSRC='{self._ksrc}' " \
                      f"CLANG='{clang_path}' BPFTOOL='{bpftool_path}' bpf"
                stdout, stderr = self._bpman.run_verify(cmd)
                self._log_cmd_output(stdout, stderr)

        # Check for 'libbpf.a', which should come from the kernel source.
        try:
            libbpf_path = self._get_libbpf_path()
        except ErrorNotFound as find_err:
            try:
                self._build_libbpf()
            except Error as build_err:
                raise Error(f"{build_err}\n{find_err}") from build_err
            libbpf_path = self._get_libbpf_path()

        # Build eBPF helpers.
        for bpfhelper in self._cats["bpfhelpers"]:
            _LOG.info("Compiling eBPF helper '%s'%s", bpfhelper, self._bpman.hostmsg)
            cmd = f"make -C '{self._btmpdir}/{bpfhelper}' KSRC='{self._ksrc}' LIBBPF={libbpf_path}"
            stdout, stderr = self._bpman.run_verify(cmd)
            self._log_cmd_output(stdout, stderr)

    def _get_helpers_deploy_path(self):
        """Returns path the directory the helpers should be deployed to."""

        helpers_path = os.environ.get("WULT_HELPERSPATH")
        if not helpers_path:
            helpers_path = self._spman.get_homedir() / _HELPERS_LOCAL_DIR / "bin"
        return Path(helpers_path)

    def _deploy_helpers(self):
        """Deploy helpers (including python helpers) to the SUT."""

        all_helpers = list(self._cats["shelpers"]) + list(self._cats["pyhelpers"]) + \
                      list(self._cats["bpfhelpers"])
        if not all_helpers:
            return

        # We assume all helpers are in the same base directory.
        helper_path = _HELPERS_SRC_SUBPATH/f"{all_helpers[0]}"
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
            self._prepare_shelpers(helpersrc)
        if self._cats["pyhelpers"]:
            self._prepare_pyhelpers(helpersrc)
        if self._cats["bpfhelpers"]:
            self._prepare_bpfhelpers(helpersrc)

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

            kmodpath = Path(f"/lib/modules/{self._kver}")
            if not self._spman.is_dir(kmodpath):
                raise Error(f"kernel modules directory '{kmodpath}' does not "
                            f"exist{self._spman.hostmsg}")

            # Build the drivers.
            _LOG.info("Compiling the drivers for kernel '%s'%s", self._kver, self._bpman.hostmsg)
            cmd = f"make -C '{drvsrc}' KSRC='{self._ksrc}'"
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

            stdout, stderr = self._spman.run_verify(f"depmod -a -- '{self._kver}'")
            self._log_cmd_output(stdout, stderr)

            # Potentially the deployed driver may crash the system before it gets to write-back data
            # to the file-system (e.g., what 'depmod' modified). This may lead to subsequent boot
            # problems. So sync the file-system now.
            self._spman.run_verify("sync")

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

        ksrc_required = False
        if self._cats["drivers"] or self._cats["bpfhelpers"]:
            ksrc_required = True

        self._init_kernel_info(ksrc_required=ksrc_required)
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
            raise Error(f"failed to deploy the '{self._toolname}' tool: {err}") from err

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
        self._kver = None # Version of the kernel to compile the drivers for (version of 'ksrc').
        self._tchk = None

        # Installables information.
        self._insts = {}
        # Lists of installables in every category.
        self._cats = { cat : {} for cat in _CATEGORIES }

        for name, info in self._deploy_info["installables"].items():
            self._insts[name] = info.copy()
            self._cats[info["category"]] = { name : info.copy()}

        if self._lbuild:
            self._bpman = self._cpman
        else:
            self._bpman = self._spman

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
