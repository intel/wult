# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides the API for deploying drivers. Refer to the 'DeployBase' module
docstring for more information.
"""

import logging
from pathlib import Path
from pepclibs.helperlibs.Exceptions import Error
from pepclibs.helperlibs import ProjectFiles
from statscollectlibs.deploylibs import DeployInstallableBase

DRIVERS_SRC_SUBDIR = Path("drivers/idle")

_LOG = logging.getLogger()

class DeployDrivers(DeployInstallableBase.DeployInstallableBase):
    """This class provides the API for deploying drivers."""

    def deploy(self, drivers, kver, ksrc, deployables, make_opts=None):
        """
        Deploy drivers to the SUT. Arguments are as follows:
         * drivers - names of the drivers to deploy to the SUT.
         * kver - kernel version running on the SUT.
         * ksrc - path to the kernel sources to compile drivers against.
         * deployables - a dictionary in the format '{deployable:installed_module}'.
         * make_opts - additional drivers compilation 'make' options (e.g., 'CC=clang').
        """

        if not drivers:
            return

        # Make sure 'cc' is available on the build host - it'll be executed by 'Makefile', so an
        # explicit check here will generate an nice error message in case 'cc' is not available.
        self._btchk.check_tool("cc")

        for drvname in drivers:
            subpath = DRIVERS_SRC_SUBDIR / drvname
            what = f"{drvname} drivers sources"
            drvsrc = ProjectFiles.find_project_data(self._prjname, subpath, what=what)
            if not drvsrc.is_dir():
                raise Error(f"path '{drvsrc}' does not exist or it is not a directory")

            _LOG.debug("copying driver sources to %s:\n   '%s' -> '%s'",
                       self._bpman.hostname, drvsrc, self._btmpdir)
            self._bpman.rsync(f"{drvsrc}/", self._btmpdir / "drivers", remotesrc=False,
                              remotedst=self._bpman.is_remote)
            drvsrc = self._btmpdir / "drivers"

            kmodpath = Path(f"/lib/modules/{kver}")
            if not self._spman.is_dir(kmodpath):
                msg = f"kernel modules directory '{kmodpath}' does not exist{self._spman.hostmsg}"
                if not self._bpman.is_remote and self._spman.is_remote:
                    msg += f"\nEven though you are building on local host, the result will have " \
                           f"to be installed to '{self._spman.hostname}'.\nFor this reason " \
                           f"you should have same kernel version ({kver}) installed on " \
                           f"'{self._spman.hostname}'."
                raise Error(msg)

            # Build the drivers.
            _LOG.info("Compiling the drivers for kernel '%s'%s", kver, self._bpman.hostmsg)
            cmd = f"make -C '{drvsrc}' KSRC='{ksrc}'"
            if self._debug:
                cmd += " V=1"
            if make_opts:
                cmd += " " + make_opts

            stdout, stderr, exitcode = self._bpman.run(cmd)
            if exitcode != 0:
                msg = self._bpman.get_cmd_failure_msg(cmd, stdout, stderr, exitcode)
                if "synth_event_" in stderr:
                    msg += "\n\nLooks like synthetic events support is disabled in your kernel, " \
                           "enable the 'CONFIG_SYNTH_EVENTS' kernel configuration option."
                elif "objtool: No such file or directory" in stderr:
                    msg += "\n\nLooks like 'objtool' is missing, maybe your kernel needs to be " \
                           "prepared to build external modules. Try running 'make modules_prepare'."
                elif "compiler differs" in stderr:
                    msg += "\n\nConsider using driver compilation 'make' options such as 'CC='."
                raise Error(msg)

            self._log_cmd_output(stdout, stderr)

            # Deploy the drivers.
            dstdir = kmodpath / DRIVERS_SRC_SUBDIR
            self._spman.mkdir(dstdir, parents=True, exist_ok=True)

            denylist = []

            for deployable, installed_module in deployables.items():
                modname = f"{deployable}.ko"
                denylist.append(f"blacklist {deployable}")
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

            # Deny automatic probing of all of our modules.
            with self._spman.open(f"/etc/modprobe.d/{self._toolname}-blacklist.conf", "w") as fobj:
                fobj.write(f"# '{self._toolname}' is a system tracing tool, and its helper kernel modules should not be\n"
                           "# automatically loaded by system. Instead, they shall be manually probed by the\n" \
                           "# tool itself when used.\n\n");
                fobj.write("\n".join(denylist))
                fobj.write("\n")

            # Potentially the deployed driver may crash the system before it gets to write-back data
            # to the file-system (e.g., what 'depmod' modified). This may lead to subsequent boot
            # problems. So sync the file-system now.
            self._spman.run_verify("sync")
