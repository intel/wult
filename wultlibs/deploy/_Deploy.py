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
from pepclibs.helperlibs import Logging, ClassHelpers, ToolChecker
from pepclibs.helperlibs import KernelVersion
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound, ErrorNotSupported
from statscollectlibs.deploy import DeployBase, _DeployPyHelpers
from wultlibs.deploy import _DeployDrivers, _DeploySHelpers

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

HELPERS_DEPLOY_SUBDIR = Path(".local")
HELPERS_SRC_SUBDIR = Path("helpers")

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

    def __init__(self, toolname, deploy_info, pman=None, ksrc=None, lbuild=False,
                 drv_make_opts=None, tmpdir_path=None, keep_tmpdir=False, debug=False):
        """
        The class constructor. The arguments are the same as in 'DeployBase.__init__()' except for:
          * ksrc - path to the kernel sources to compile drivers against.
          * drv_make_opts - options to add to the 'make' command when building the drivers.
        """

        self._ksrc = ksrc
        self._drv_make_opts = drv_make_opts
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
