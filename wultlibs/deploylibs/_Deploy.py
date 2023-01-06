# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API for deploying the tools coming with the 'wult' project.
Note, "wult" is both name of the project and name of the tool in the project.
"""

import os
import time
import logging
from pathlib import Path
from pepclibs.helperlibs import LocalProcessManager
from pepclibs.helperlibs import ClassHelpers, ArgParse, ToolChecker, ProjectFiles
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound, ErrorNotSupported
from statscollectlibs.deploylibs import DeployBase, DeployHelpersBase
from wultlibs.deploylibs import _DeployBPFHelpers, _DeployDrivers, _DeploySHelpers
from wultlibs.helperlibs import KernelVersion

_LOG = logging.getLogger()

def add_deploy_cmdline_args(toolname, deploy_info, subparsers, func, argcomplete=None):
    """
    Add the the 'deploy' command to 'argparse' data. The input arguments are as follows.
      * toolname - name of the tool to add the 'deploy' command for.
      * deploy_info - a dictionary describing the tool to deploy, same as in
                      'DeployBase.__init__()'.
      * subparsers - the 'argparse' subparsers to add the 'deploy' command to.
      * func - the 'deploy' command handling function.
      * argcomplete - optional 'argcomplete' command-line arguments completer object.
    """

    cats = {cat : [] for cat in DeployBase.CATEGORIES}
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

    text = f"Compile and deploy {toolname} {what}."
    descr = f"""Compile and deploy {toolname} {what} to the SUT (System Under Test), which can be
                can be either local or a remote host, depending on the '-H' option. By default,
                everything is built on the SUT, but the '--local-build' can be used for building
                on the local system."""

    if cats["drivers"]:
        searchdirs = ProjectFiles.get_project_data_search_descr("wult",
                                                                _DeployDrivers.DRIVERS_SRC_SUBDIR)
        descr += f""" The drivers are searched for in the following directories (and in the
                     following order) on the local host: {searchdirs}."""
    if cats["shelpers"] or cats["pyhelpers"]:
        searchdirs = ProjectFiles.get_project_data_search_descr("wult",
                                                            DeployHelpersBase.HELPERS_SRC_SUBDIR)
        helpernames = ", ".join(cats["shelpers"] + cats["pyhelpers"] + cats["bpfhelpers"])
        descr += f""" The {toolname} tool also depends on the following helpers: {helpernames}.
                     These helpers will be compiled on the SUT and deployed to the SUT. The sources
                     of the helpers are searched for in the following paths (and in the following
                     order) on the local host: {searchdirs}. By default, helpers are deployed to
                     the path defined by the 'WULT_HELPERSPATH' environment variable. If the
                     variable is not defined, helpers are deployed to
                     '$HOME/{DeployHelpersBase.HELPERS_DEPLOY_SUBDIR}/bin', where '$HOME' is the
                     home directory of user 'USERNAME' on host 'HOST' (see '--host' and '--username'
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
            cat_descr = self._insts[installable]["category_descr"]
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
        """Same as 'DeployBase.get_installed_helper_path()'."""
        return DeployBase.get_installed_helper_path("wult", self._toolname, deployable,
                                                    pman=self._spman)

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

        cat_descr = self._insts[installable]["category_descr"]
        if deployable != installable:
            return f"the '{deployable}' component of the '{installable}' {cat_descr}"
        return f"the '{deployable}' {cat_descr}"

    def _deployable_not_found(self, deployable):
        """
        Called in a situation when 'deployable' was not found. Formats an error message and
        raises 'ErrorNotFound'.
        """

        installable = self._get_installable_by_deployable(deployable)
        what = self._get_deployable_print_name(installable, deployable)
        is_helper = self._insts[installable]["category"] != "drivers"

        err = DeployBase.get_deploy_suggestion(self._spman, "wult", self._toolname, what, is_helper)
        raise ErrorNotFound(err) from None

    def _warn_deployable_out_of_date(self, deployable):
        """Print a warning about the 'what' deployable not being up-to-date."""

        installable = self._get_installable_by_deployable(deployable)
        what = self._get_deployable_print_name(installable, deployable)

        _LOG.warning("%s may be out of date%s\nConsider running '%s'",
                     what, self._spman.hostmsg,
                     DeployBase.get_deploy_cmd(self._spman, self._toolname))

    def _check_deployable_up_to_date(self, deployable, srcpath, dstpath):
        """
        Check that a deployable at 'dstpath' on SUT is up-to-date by comparing its 'mtime' to the
        source (code) of the deployable at 'srcpath' on the controller.
        """

        if self._time_delta is None:
            if self._spman.is_remote:
                # Take into account the possible time difference between local and remote
                # systems.
                self._time_delta = time.time() - self._spman.time_time()
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
                subpath = _DeployDrivers.DRIVERS_SRC_SUBDIR / self._toolname
                what = f"the '{drvname}' driver"
                srcpath = ProjectFiles.find_project_data("wult", subpath, what=what)
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
                subpath = DeployHelpersBase.HELPERS_SRC_SUBDIR / helpername
                what = f"the '{helpername}' helper program"
                srcpath = ProjectFiles.find_project_data("wult", subpath, what=what)
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
                subpath = DeployHelpersBase.HELPERS_SRC_SUBDIR / pyhelper
                what = f"the '{pyhelper}' python helper program"
                srcpath = ProjectFiles.find_project_data("wult", subpath, what=what)
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
          * deploy_info - a dictionary describing the tool to deploy. Check 'DeployBase.__init__()'
                          for more information.
          * pman - the process manager object that defines the SUT to deploy to (local host by
                   default).

        Please, refer to module docstring for more information.
        """

        self._insts, self._cats = DeployBase.get_insts_cats(deploy_info)
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


class Deploy(DeployBase.DeployBase):
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

    def _deploy_bpf_helpers(self):
        """Deploy eBPF helpers to the SUT."""

        bpfhelpers = self._cats.get("bpfhelpers")
        if not bpfhelpers:
            return

        with _DeployBPFHelpers.DeployBPFHelpers("wult", self._toolname, self._tchk,
                                                self._get_ksrc(), self._rebuild_bpf, self._spman,
                                                self._bpman, self._get_stmpdir(),
                                                self._get_btmpdir(), debug=self._debug) as depl:
            depl.deploy(list(bpfhelpers))

    def _deploy_shelpers(self):
        """Deploy simple helpers to the SUT."""

        shelpers = self._cats.get("shelpers")
        if not shelpers:
            return

        with _DeploySHelpers.DeploySHelpers("wult", self._toolname, self._spman, self._bpman,
                                            self._get_stmpdir(), self._get_btmpdir(),
                                            debug=self._debug) as depl:
            depl.deploy(list(shelpers))

    def _deploy_drivers(self):
        """Deploy drivers to the SUT."""

        drivers = self._cats["drivers"]
        if not drivers:
            return

        with _DeployDrivers.DeployDrivers("wult", self._toolname, self._spman, self._bpman,
                                          self._get_stmpdir(), self._get_btmpdir(),
                                          debug=self._debug) as depl:
            deps = {}
            for dep in self._get_deployables("drivers"):
                deps[dep] = self._khelper.get_module_path(dep)

            depl.deploy(drivers, self._get_kver(), self._get_ksrc(), deps)

    def _adjust_installables(self):
        """
        Adjust the list of installables that have to be deployed to the SUT based on various
        conditions, such as kernel version.
        """

        # Exclude installables with unsatisfied minimum kernel version requirements.
        for installable in list(self._insts):
            try:
                self._khelper.check_minkver(installable, self._get_kver())
            except ErrorNotSupported as err:
                cat_descr = self._insts[installable]["category_descr"]
                _LOG.notice(str(err))
                _LOG.warning("the '%s' %s can't be installed", installable, cat_descr)

                cat = self._insts[installable]["category"]
                del self._insts[installable]
                del self._cats[cat][installable]

    def _deploy(self):
        """Deploy required installables to the SUT."""

        if self._cats["drivers"] or self._cats["shelpers"] or self._cats["bpfhelpers"]:
            # Make sure 'cc' is available on the build host - it'll be executed by 'Makefile', so an
            # explicit check here will generate an nice error message in case 'cc' is not available.
            self._tchk.check_tool("cc")

        self._deploy_drivers()
        self._deploy_shelpers()
        self._deploy_bpf_helpers()

    def deploy(self):
        """Deploy all the required installables to the SUT (drivers, helpers, etc)."""

        try:
            self._deploy()
        finally:
            self._remove_tmpdirs()

    def __init__(self, toolname, deploy_info, pman=None, ksrc=None, lbuild=False, rebuild_bpf=False,
                 tmpdir_path=None, keep_tmpdir=False, debug=False):
        """
        The class constructor. The arguments are the same as in 'DeployBase.__init__()' except for:
          * ksrc - path to the kernel sources to compile drivers against.
          * rebuild_bpf - if 'toolname' comes with an eBPF helper, re-build the the eBPF component
                           of the helper if this argument is 'True'. Do not re-build otherwise.
        """

        self._ksrc = ksrc
        self._rebuild_bpf = rebuild_bpf
        self._tchk = None

        # Version of the kernel running on the SUT of version of the kernel to compile wult
        # components against.
        self._kver = None
        self._khelper = None

        super().__init__("wult", toolname, deploy_info, pman=pman, lbuild=lbuild,
                         tmpdir_path=tmpdir_path, keep_tmpdir=keep_tmpdir, debug=debug)

        self._khelper = _KernelHelper(self._insts, self._spman)

        if self._ksrc:
            if not self._bpman.is_dir(self._ksrc):
                raise Error(f"kernel sources directory '{self._ksrc}' does not "
                            f"exist{self._bpman.hostmsg}")
            self._ksrc = self._bpman.abspath(self._ksrc)

        self._tchk = ToolChecker.ToolChecker(self._bpman)

        self._adjust_installables()

    def close(self):
        """Uninitialize the object."""

        ClassHelpers.close(self, close_attrs=("_tchk", "_khelper"))
        super().close()
