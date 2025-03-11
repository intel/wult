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

from pathlib import Path
from pepclibs.helperlibs import Logging, ClassHelpers, ArgParse, ProjectFiles, ToolChecker
from pepclibs.helperlibs import KernelVersion
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound, ErrorNotSupported
from statscollectlibs.deploylibs import DeployBase, _DeployPyHelpers
from wultlibs.deploylibs import _DeployBPFHelpers, _DeployDrivers, _DeploySHelpers

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

HELPERS_DEPLOY_SUBDIR = Path(".local")
HELPERS_SRC_SUBDIR = Path("helpers")

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

    cats = {cat: [] for cat in DeployBase.CATEGORIES}
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
        searchdirs = ProjectFiles.get_project_data_search_descr("wult", HELPERS_SRC_SUBDIR)
        helpernames = ", ".join(cats["shelpers"] + cats["pyhelpers"] + cats["bpfhelpers"])
        descr += f""" The {toolname} tool also depends on the following helpers: {helpernames}.
                     These helpers will be compiled on the SUT and deployed to the SUT. The sources
                     of the helpers are searched for in the following paths (and in the following
                     order) on the local host: {searchdirs}. By default, helpers are deployed to
                     the path defined by the 'WULT_HELPERSPATH' environment variable. If the
                     variable is not defined, helpers are deployed to
                     '$HOME/{HELPERS_DEPLOY_SUBDIR}/bin', where '$HOME' is the home directory of
                     user 'USERNAME' on host 'HOST' (see '--host' and '--username' options)."""
    parser = subparsers.add_parser("deploy", help=text, description=descr)

    if cats["drivers"] or cats["bpfhelpers"]:
        text = """Path to the Linux kernel sources to build drivers and eBPF helpers against. The
                  default is '/lib/modules/$(uname -r)/build' on the SUT. If '--local-build' was
                  used, then the path is considered to be on the local system, rather than the
                  SUT."""
        arg = parser.add_argument("--kernel-src", dest="ksrc", type=Path, help=text)
        if argcomplete:
            arg.completer = argcomplete.completers.DirectoriesCompleter()

    if cats["drivers"]:
        text = """Options and variables to pass to 'make' when the drivers are built. For example,
                  pass 'CC=clang LLVM=1' to use clang and LLVM tools for building the drivers."""
        parser.add_argument("--drivers-make-opts", dest="drv_make_opts", help=text)

    if cats["drivers"] and cats["bpfhelpers"]:
        text = """Do not deploy the drivers. This is a debug and development option, do not use it
                  for other purposes."""
        parser.add_argument("--skip-drivers", action="store_true", help=text)

        text = """Do not deploy eBPF helpers. This is a debug and development option, do not use it
                  for other purposes."""
        parser.add_argument("--skip-bpf", action="store_true", help=text)

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

def _check_minkver(pman, instinfo, kver):
    """
    Check if the SUT has new enough kernel version for 'installable' to be deployed on it. The
    argument are as follows:
        * pman - a process manager object for the SUT.
        * instinfo - the installable description dictionary.
        * kver - version of the kernel running on the SUT.
    """

    minkver = instinfo.get("minkver", None)
    if not minkver:
        return

    if KernelVersion.kver_lt(kver, minkver):
        name = instinfo["name"]
        cat_descr = instinfo["category_descr"]
        raise ErrorNotSupported(f"version of Linux kernel{pman.hostmsg} is {kver}, and "
                                f"it is not new enough for the '{name}' {cat_descr}.\n"
                                f"Please, use kernel version {minkver} or newer.")

def _get_module_path(pman, name):
    """Return path to installed module 'name'. Returns 'None', if the module was not found."""

    cmd = f"modinfo -n {name}"
    stdout, _, exitcode = pman.run(cmd)
    if exitcode != 0:
        return None

    modpath = Path(stdout.strip())
    if pman.is_file(modpath):
        return modpath
    return None

class DeployCheck(DeployBase.DeployCheckBase):
    """
    This class provides the 'check_deployment()' method which can be used for verifying whether all
    the required installables are available on the SUT.
    """

    def _get_kver(self):
        """Returns version of the kernel running on the SUT."""

        if not self._kver:
            self._kver = KernelVersion.get_kver(pman=self._spman)

        return self._kver

    def _check_drivers_deployment(self):
        """Check if drivers are deployed and up-to-date."""

        for drvname, instinfo in self._cats["drivers"].items():
            _check_minkver(self._spman, instinfo, self._get_kver())

            try:
                subpath = _DeployDrivers.DRIVERS_SRC_SUBDIR / self._toolname
                what = f"the '{drvname}' driver"
                srcpath = ProjectFiles.find_project_data("wult", subpath, what=what)
            except ErrorNotFound:
                srcpath = None

            for deployable in self._get_deployables("drivers"):
                dstpath = _get_module_path(self._spman, deployable)
                if not dstpath:
                    self._deployable_not_found(deployable)
                    break

                if srcpath:
                    self._check_deployable_up_to_date(deployable, srcpath, dstpath)

    def _check_helpers_deployment(self):
        """Check if simple and eBPF helpers are deployed and up-to-date."""

        for helpername in list(self._cats["shelpers"]) + list(self._cats["bpfhelpers"]):
            _check_minkver(self._spman, self._insts[helpername], self._get_kver())

            try:
                subpath = HELPERS_SRC_SUBDIR / helpername
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

    def _check_deployment(self):
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

    def __init__(self, prjname, toolname, deploy_info, pman=None):
        """
        The class constructor. The arguments are the same as in 'DeployCheckBase.__init__()'.
        """

        super().__init__(prjname, toolname, deploy_info, pman=pman)

        # Version of the kernel running on the SUT, or version of the kernel to compile against.
        self._kver = None
        self._time_delta = None

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

        _LOG.debug("kernel version: %s", self._kver)
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

        _LOG.debug("kernel sources path: %s", self._ksrc)
        return self._ksrc

    def _deploy_bpf_helpers(self):
        """Deploy eBPF helpers to the SUT."""

        bpfhelpers = self._cats["bpfhelpers"]
        if not bpfhelpers:
            return

        with _DeployBPFHelpers.DeployBPFHelpers("wult", self._toolname, self._get_ksrc(),
                                                self._rebuild_bpf, self._spman, self._bpman,
                                                self._get_stmpdir(), self._get_btmpdir(),
                                                btchk=self._btchk, debug=self._debug) as depl:
            depl.deploy(list(bpfhelpers))

    def _deploy_shelpers(self):
        """Deploy simple helpers to the SUT."""

        shelpers = self._cats["shelpers"]
        if not shelpers:
            return

        with _DeploySHelpers.DeploySHelpers("wult", self._toolname, self._spman, self._bpman,
                                            self._get_stmpdir(), self._get_btmpdir(),
                                            btchk=self._btchk, debug=self._debug) as depl:
            depl.deploy(list(shelpers))

    def _deploy_pyhelpers(self):
        """Deploy python helpers to the SUT."""

        if not self._cats["pyhelpers"]:
            return

        with _DeployPyHelpers.DeployPyHelpers("wult", self._toolname, self._spman,
                                              self._bpman, self._get_stmpdir(), self._get_btmpdir(),
                                              cpman=self._cpman, ctmpdir=self._get_ctmpdir(),
                                              debug=self._debug) as depl:
            depl.deploy(self._cats["pyhelpers"])

    def _deploy_drivers(self):
        """Deploy drivers to the SUT."""

        drivers = self._cats["drivers"]
        if not drivers:
            return

        with _DeployDrivers.DeployDrivers("wult", self._toolname, self._spman, self._bpman,
                                          self._get_stmpdir(), self._get_btmpdir(),
                                          btchk=self._btchk, debug=self._debug) as depl:
            deps = {}
            for dep in self._get_deployables("drivers"):
                deps[dep] = _get_module_path(self._spman, dep)

            depl.deploy(drivers, self._get_kver(), self._get_ksrc(), deps,
                        make_opts=self._drv_make_opts)

    def _deploy(self):
        """Deploy required installables to the SUT."""

        self._deploy_drivers()
        self._deploy_shelpers()
        self._deploy_pyhelpers()
        self._deploy_bpf_helpers()

    def deploy(self):
        """Deploy all the required installables to the SUT (drivers, helpers, etc)."""

        try:
            self._deploy()
        finally:
            self._remove_tmpdirs()

    def _drop_installables(self):
        """
        Drop the some installables, for example those that do not satisfy the minimum kernel version
        requirements.
        """

        if self._skip_bpf:
            for installable in list(self._cats["bpfhelpers"]):
                self._drop_installable(installable)

        if self._skip_drivers:
            for installable in list(self._cats["drivers"]):
                self._drop_installable(installable)

        # Python helpers need to be deployed only to a remote host. The local host should already
        # have them:
        #   * either deployed via 'setup.py'.
        #   * or if running from source code, present in the source code.
        if not self._spman.is_remote:
            for installable in list(self._cats["pyhelpers"]):
                self._drop_installable(installable)

        # Exclude installables with unsatisfied minimum kernel version requirements.
        for installable in list(self._insts):
            instinfo = self._insts[installable]
            try:
                _check_minkver(self._spman, instinfo, self._get_kver())
            except ErrorNotSupported as err:
                cat_descr = instinfo["category_descr"]
                _LOG.notice(str(err))
                _LOG.warning("the '%s' %s can't be installed", installable, cat_descr)

                self._drop_installable(installable)

    def __init__(self, toolname, deploy_info, pman=None, ksrc=None, lbuild=False, skip_bpf=None,
                 skip_drivers=None, drv_make_opts=None, rebuild_bpf=False, tmpdir_path=None,
                 keep_tmpdir=False, debug=False):
        """
        The class constructor. The arguments are the same as in 'DeployBase.__init__()' except for:
          * ksrc - path to the kernel sources to compile drivers against.
          * skip_bpf - do not build / deploy eBPF helpers (drop the installables of the "bpfhelpers"
                       category).
          * skip_drivers - do not build / deploy the drivers (drop the installables of the "drivers"
                           category).
          * drv_make_opts - options to add to the 'make' command when building the drivers.
          * rebuild_bpf - if 'toolname' comes with an eBPF helper, re-build the the eBPF component
                          of the helper if this argument is 'True'. Do not re-build otherwise.
        """

        self._ksrc = ksrc
        self._skip_bpf = skip_bpf
        self._skip_drivers = skip_drivers
        self._drv_make_opts = drv_make_opts
        self._rebuild_bpf = rebuild_bpf
        self._btchk = None

        # Version of the kernel running on the SUT of version of the kernel to compile wult
        # components against.
        self._kver = None

        super().__init__("wult", toolname, deploy_info, pman=pman, lbuild=lbuild,
                         tmpdir_path=tmpdir_path, keep_tmpdir=keep_tmpdir, debug=debug)

        if self._ksrc:
            if not self._bpman.is_dir(self._ksrc):
                raise Error(f"kernel sources directory '{self._ksrc}' does not "
                            f"exist{self._bpman.hostmsg}")
            self._ksrc = self._bpman.abspath(self._ksrc)

        self._btchk = ToolChecker.ToolChecker(self._bpman)

        self._drop_installables()

    def close(self):
        """Uninitialize the object."""

        ClassHelpers.close(self, close_attrs=("_btchk",))
        super().close()
