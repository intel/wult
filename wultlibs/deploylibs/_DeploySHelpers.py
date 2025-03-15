
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides the API for deploying simple helpers. Refer to the 'DeployBase' module
docstring for more information.
"""

# TODO: finish adding type hints to this module.
from __future__ import annotations # Remove when switching to Python 3.10+.

from pathlib import Path
from pepclibs.helperlibs import Logging
from statscollectlibs.deploylibs import DeployHelpersBase
from statscollectlibs.deploylibs.DeployBase import InstallableInfoTypedDict

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

class DeploySHelpers(DeployHelpersBase.DeployHelpersBase):
    """This class provides the API for deploying simple helpers."""

    def _prepare(self, insts_info: dict[str, InstallableInfoTypedDict], installables_basedir: Path):
        """
        Build and prepare installables for deployment.

        Args:
            insts_info: The installables information dictionary.
            installables_basedir: Path to the base directory that contains the installables on the
                                  controller.
        """

        # Make sure 'cc' is available on the build host - it'll be executed by 'Makefile', so an
        # explicit check here will generate a nice error message in case 'cc' is not available.
        self._get_btchk().check_tool("cc")

        # Copy simple helpers to the temporary directory on the build host.
        for shelper in insts_info:
            srcdir = installables_basedir/ shelper
            _LOG.debug("copying simple helper '%s' to %s:\n  '%s' -> '%s'",
                       shelper, self._bpman.hostname, srcdir, self._btmpdir)
            self._bpman.rsync(srcdir, self._btmpdir, remotesrc=False,
                              remotedst=self._bpman.is_remote)

        # Build simple helpers.
        for shelper in insts_info:
            _LOG.info("Compiling simple helper '%s'%s", shelper, self._bpman.hostmsg)
            helperpath = f"{self._btmpdir}/{shelper}"
            stdout, stderr = self._bpman.run_verify(f"make -C '{helperpath}'")
            self._log_cmd_output(stdout, stderr)

    def __init__(self, prjname, toolname, spman, bpman, stmpdir, btmpdir, btchk=None,
                 debug=False):
        """
        Class constructor. Arguments are the same as in 'DeployHelpersBase.DeployHelpersBase()'.
        """

        what = f"{toolname} helpers"
        super().__init__(prjname, toolname, what, spman, bpman, stmpdir, btmpdir=btmpdir,
                         btchk=btchk,debug=debug)
