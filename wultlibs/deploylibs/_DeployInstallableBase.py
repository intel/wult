# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module provides a base class for deploying installables."""

import logging
from pepclibs.helperlibs import Logging

_LOG = logging.getLogger()

class DeployInstallableBase:
    """This base class can be inherited from to provide the API for deploying helpers."""

    def _log_cmd_output(self, stdout, stderr):
        """Print output of a command in case debugging is enabled."""

        if self._debug:
            if stdout:
                _LOG.log(Logging.ERRINFO, stdout)
            if stderr:
                _LOG.log(Logging.ERRINFO, stderr)

    def __init__(self, bpman, spman, btmpdir, debug):
        """
        Class constructor. Arguments are as follows:
         * bpman - process manager associated with the build host.
         * spman - process manager associated with the SUT.
         * btmpdir - a path to a temporary directory on the build host.
         * debug - a boolean variable used to enable extra verbose building of the drivers.
        """

        self._bpman = bpman
        self._spman = spman
        self._btmpdir = btmpdir
        self._debug = debug
