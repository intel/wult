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
from pepclibs.helperlibs import LocalProcessManager
from pepclibs.helperlibs import ClassHelpers, ArgParse, ToolChecker
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound, ErrorNotSupported
from statscollectlibs.deploylibs import _DeployHelpersBase, _DeployPyHelpers
from statscollectlibs.helperlibs import ToolHelpers
from statscollectlibs.deploylibs import Deploy as StatsCollectDeploy
from wultlibs.deploylibs import _DeployBPFHelpers, _DeployDrivers, _DeploySHelpers
from wultlibs.helperlibs import RemoteHelpers, KernelVersion

_LOG = logging.getLogger()

# The supported installable categories.
_CATEGORIES = { "drivers"    : "kernel driver",
                "shelpers"   : "simple helper program",
                "pyhelpers"  : "python helper program",
                "bpfhelpers" : "eBPF helper program"}

def add_deploy_cmdline_args(toolname, deploy_info, subparsers, func, argcomplete=None):
    """
    Add the the 'deploy' command to 'argparse' data. The input arguments are as follows.
      * toolname - name of the tool to add the 'deploy' command for.
      * deploy_info - a dictionary describing the tool to deploy, same as in 'Deploy.__init__()'.
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
        drvsearch = ", ".join([name % str(_DeployDrivers.DRV_SRC_SUBPATH) for name in searchdirs])
        descr += f""" The drivers are searched for in the following directories (and in the
                     following order) on the local host: {drvsearch}."""
    if cats["shelpers"] or cats["pyhelpers"]:
        dirs = [name % str(_DeployHelpersBase.HELPERS_SRC_SUBPATH) for name in searchdirs]
        helpersearch = ", ".join(dirs)
        helpernames = ", ".join(cats["shelpers"] + cats["pyhelpers"] + cats["bpfhelpers"])
        descr += f"""The {toolname} tool also depends on the following helpers: {helpernames}.
                     These helpers will be compiled on the SUT and deployed to the SUT. The sources
                     of the helpers are searched for in the following paths (and in the following
                     order) on the local host: {helpersearch}. By default, helpers are deployed to
                     the path defined by the 'WULT_HELPERSPATH' environment variable. If the
                     variable is not defined, helpers are deployed to
                     '$HOME/{_DeployHelpersBase.HELPERS_LOCAL_DIR}/bin', where '$HOME' is the home
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

class _KernelHelper(ClassHelpers.SimpleCloseContext):
    """
    This class provides helper methods related to kernel versions and kernel module paths for
    'Deploy' and 'DeployCheck'.
    """

    def check_minkver(self, installable, kver):
        """
        Check if the SUT has new enough kernel version for 'installable' to be deployed on it. The
        argument are as follows:
          * installable - name of the installable to check the kernel version for.
          * kver - version of the kernel running on the SUT.
        """

        minkver = self._insts[installable].get("minkver", None)
        if not minkver:
            return

        if KernelVersion.kver_lt(kver, minkver):
            cat_descr = _CATEGORIES[self._insts[installable]["category"]]
            raise ErrorNotSupported(f"version of Linux kernel{self._spman.hostmsg} is {kver}, and "
                                    f"it is not new enough for the '{installable}' {cat_descr}.\n"
                                    f"Please, use kernel version {minkver} or newer.")

    def get_module_path(self, name):
        """Return path to installed module 'name'. Returns 'None', if the module was not found."""

        cmd = f"modinfo -n {name}"
        stdout, _, exitcode = self._spman.run(cmd)
        if exitcode != 0:
            return None

        modpath = Path(stdout.strip())
        if self._spman.is_file(modpath):
            return modpath
        return None

    def __init__(self, insts, pman):
        """
        The class constructor. The arguments are as follows.
          * insts - a dictionary describing installables information.
          * pman - the process manager object that defines the SUT to deploy to.
        """

        self._spman = pman
        self._insts = insts

    def close(self):
        """Uninitialize the object."""
        ClassHelpers.close(self, unref_attrs=("_spman"))

class DeployCheck(ClassHelpers.SimpleCloseContext):
    """
    This class provides the 'check_deployment()' method which can be used for verifying whether all
    the required installables are available on the SUT.
    """

    def _get_kver(self):
        """Returns version of the kernel running on the SUT."""

        if not self._kver:
            self._kver = KernelVersion.get_kver(pman=self._spman)

        return self._kver

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
        """Same as 'StatsCollectDeploy.get_installed_helper_path()'."""
        return StatsCollectDeploy.get_installed_helper_path(self._spman, self._toolname, deployable)

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
        """Same as 'StatsCollectDeploy._deployable_not_found()'."""

        installable = self._get_installable_by_deployable(deployable)
        what = self._get_deployable_print_name(installable, deployable)
        is_helper = self._insts[installable]["category"] != "drivers"

        StatsCollectDeploy.deployable_not_found(self._spman, self._toolname, what, is_helper)

    def _warn_deployable_out_of_date(self, deployable):
        """Print a warning about the 'what' deployable not being up-to-date."""

        installable = self._get_installable_by_deployable(deployable)
        what = self._get_deployable_print_name(installable, deployable)

        _LOG.warning("%s may be out of date%s\nConsider running '%s'",
                     what, self._spman.hostmsg,
                     StatsCollectDeploy.get_deploy_cmd(self._spman, self._toolname))

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
            self._khelper.check_minkver(drvname, self._get_kver())

            try:
                subpath = _DeployDrivers.DRV_SRC_SUBPATH / self._toolname
                srcpath = ToolHelpers.find_project_data("wult", subpath, f"the '{drvname}' driver")
            except ErrorNotFound:
                srcpath = None

            for deployable in self._get_deployables("drivers"):
                dstpath = self._khelper.get_module_path(deployable)
                if not dstpath:
                    self._deployable_not_found(deployable)
                    break

                if srcpath:
                    self._check_deployable_up_to_date(deployable, srcpath, dstpath)

    def _check_helpers_deployment(self):
        """Check if simple and eBPF helpers are deployed and up-to-date."""

        for helpername in list(self._cats["shelpers"]) + list(self._cats["bpfhelpers"]):
            self._khelper.check_minkver(helpername, self._get_kver())

            try:
                descr=f"the '{helpername}' helper program"
                subpath = _DeployHelpersBase.HELPERS_SRC_SUBPATH / helpername
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
                subpath = _DeployHelpersBase.HELPERS_SRC_SUBPATH / pyhelper
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
          * deploy_info - a dictionary describing the tool to deploy. Check 'Deploy.__init__()' for
                          more information.
          * pman - the process manager object that defines the SUT to deploy to (local host by
                   default).

        Please, refer to module docstring for more information.
        """

        self._insts, self._cats = StatsCollectDeploy.get_insts_cats(deploy_info, _CATEGORIES)
        self._toolname = toolname

        if pman:
            self._spman = pman
            self._close_spman = False
        else:
            self._spman = LocalProcessManager.LocalProcessManager()
            self._close_spman = True

        # Version of the kernel running on the SUT of version of the kernel to compile wult
        # components against.
        self._kver = None
        self._khelper = _KernelHelper(self._insts, self._spman)

        self._time_delta = None

    def close(self):
        """Uninitialize the object."""
        ClassHelpers.close(self, close_attrs=("_spman", "_khelper"))


class Deploy(StatsCollectDeploy.Deploy):
    """
    This class provides the 'deploy()' method which can be used for deploying the dependencies of
    the tools of the "wult" project.
    """

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

    def _deploy_helpers(self, toolname, lbuild):
        """
        Deploy helpers (including python helpers) to the SUT. Arguments are as follows:
         * toolname - name of the tool which the helpers are supporting.
         * lbuild - boolean value which represents whether to build locally or not.
        """

        pyhelpers = self._cats.get("pyhelpers")
        if pyhelpers:
            dep_pyhelpers = _DeployPyHelpers.DeployPyHelpers(self._bpman, self._spman, self._cpman,
                                                             self._btmpdir, self._get_ctmpdir(),
                                                             self._get_stmpdir(),
                                                             self._get_deployables("pyhelpers"),
                                                             self._debug)
            dep_pyhelpers.deploy(list(pyhelpers), toolname, lbuild)

        shelpers = self._cats.get("shelpers")
        if shelpers:
            dep_shelpers = _DeploySHelpers.DeploySHelpers(self._bpman, self._spman, self._btmpdir,
                                                          self._get_stmpdir(), self._debug)
            dep_shelpers.deploy(list(shelpers), toolname, lbuild)

        bpfhelpers = self._cats.get("bpfhelpers")
        if bpfhelpers:
            dep_bpfhelpers = _DeployBPFHelpers.DeployBPFHelpers(self._bpman, self._spman,
                                                                self._btmpdir, self._get_stmpdir(),
                                                                self._tchk, self._get_ksrc(),
                                                                lbuild, self._rebuild_bpf,
                                                                self._debug)
            dep_bpfhelpers.deploy(list(bpfhelpers), toolname, lbuild)

    def _deploy_drivers(self):
        """Deploy drivers to the SUT."""

        if not self._cats["drivers"]:
            return

        deps = {}
        for dep in self._get_deployables("drivers"):
            deps[dep] = self._khelper.get_module_path(dep)

        dep_drvr = _DeployDrivers.DeployDrivers(self._bpman, self._spman, self._btmpdir,
                                                self._debug)
        dep_drvr.deploy(self._cats["drivers"], self._get_kver(), self._get_ksrc(), deps)

    def _adjust_installables(self):
        """
        Adjust the list of installables that have to be deployed to the SUT based on various
        conditions, such as kernel version.
        """

        super()._adjust_installables()

        # Exclude installables with unsatisfied minimum kernel version requirements.
        for installable in list(self._insts):
            try:
                self._khelper.check_minkver(installable, self._get_kver())
            except ErrorNotSupported as err:
                cat = self._insts[installable]["category"]
                _LOG.notice(str(err))
                _LOG.warning("the '%s' %s can't be installed", installable, _CATEGORIES[cat])

                del self._insts[installable]
                del self._cats[cat][installable]

    def _deploy(self):
        """Deploy required installables to the SUT."""

        if self._cats["drivers"] or self._cats["shelpers"] or self._cats["bpfhelpers"]:
            # Make sure 'cc' is available on the build host - it'll be executed by 'Makefile', so an
            # explicit check here will generate an nice error message in case 'cc' is not available.
            self._tchk.check_tool("cc")

        self._deploy_drivers()
        self._deploy_helpers(self._toolname, self._lbuild)

    def _init_insts_cats(self):
        """Helper function for the constructor. Initialises '_ints' and '_cats'."""

        self._ints, self._cats = StatsCollectDeploy.get_insts_cats(self._deploy_info, _CATEGORIES)

    def __init__(self, toolname, deploy_info, pman=None, ksrc=None, lbuild=False, rebuild_bpf=False,
                 tmpdir_path=None, keep_tmpdir=False, debug=False):
        """
        The class constructor. The arguments are the same as in
        'statscollectlibs.Deploy.Deploy.__init__()' except for:
          * ksrc - path to the kernel sources to compile drivers against.
          * rebuild_bpf - if 'toolname' comes with an eBPF helper, re-build the the eBPF component
                           of the helper if this argument is 'True'. Do not re-build otherwise.

        The 'deploy_info' dictionary describes the tool to deploy and its dependencies. It should
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

        super().__init__(toolname, deploy_info, pman, lbuild, tmpdir_path, keep_tmpdir, debug)

        self._ksrc = ksrc
        self._rebuild_bpf = rebuild_bpf
        self._tchk = None

        # Version of the kernel running on the SUT of version of the kernel to compile wult
        # components against.
        self._kver = None
        self._khelper = _KernelHelper(self._insts, self._spman)

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

    def close(self):
        """Uninitialize the object."""

        ClassHelpers.close(self, close_attrs=("_tchk", "_khelper"))
        super().close()
