
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module provides the API for deploying simple helpers."""

import logging
from wultlibs import _DeployHelpersBase

_LOG = logging.getLogger()

class DeploySHelpers(_DeployHelpersBase.DeployHelpersBase):
    """This class provides the API for deploying simple helpers."""

    def prepare(self, helpersrc, helpers):
        """
        Build and prepare simple helpers for deployment. The arguments are as follows:
          * helpersrc - path to the helpers base directory on the controller.
          * helpers - simple helpers to build and prepare for deployment.
        """

        # Copy simple helpers to the temporary directory on the build host.
        for shelper in helpers:
            srcdir = helpersrc/ shelper
            _LOG.debug("copying simple helper '%s' to %s:\n  '%s' -> '%s'",
                       shelper, self._bpman.hostname, srcdir, self._btmpdir)
            self._bpman.rsync(srcdir, self._btmpdir, remotesrc=False,
                              remotedst=self._bpman.is_remote)

        # Build simple helpers.
        for shelper in helpers:
            _LOG.info("Compiling simple helper '%s'%s", shelper, self._bpman.hostmsg)
            helperpath = f"{self._btmpdir}/{shelper}"
            stdout, stderr = self._bpman.run_verify(f"make -C '{helperpath}'")
            self._log_cmd_outdir(stdout, stderr)

    def __init__(self, bpman, spman, btmpdir, stmpdir, log_cmd_func):
        """
        Class constructor. Arguments are the same as in '_DeployHelpersBase.DeployHelpersBase()'
        except for:
         * log_cmd_func - a function with signature 'log_cmd_func(stdout, stderr)' which will log
                          stdout and stderr accordingly.
        """

        self._log_cmd_outdir = log_cmd_func
        super().__init__(bpman, spman, btmpdir, stmpdir)
