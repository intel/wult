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

class DeployBase:
    """This base class can be inherited from to provide the API for deploying installables."""

    def _log_cmd_output(self, stdout, stderr):
        """Print output of a command in case debugging is enabled."""

        if self._debug:
            if stdout:
                _LOG.log(Logging.ERRINFO, stdout)
            if stderr:
                _LOG.log(Logging.ERRINFO, stderr)

    def __init__(self, prjname, toolname, spman, bpman, stmpdir, btmpdir, cpman=None, ctmpdir=None,
                 debug=False):
        """
        Class constructor. Arguments are as follows:
         * prjname - name of the project the installables and 'toolname' belong to.
         * toolname - name of the tool the installables belong to.
         * spman - a process manager object associated with the SUT (System Under Test, the system
                   where the installables will be deployed).
         * bpman - a process manager object associated with the build host (the host where the
                   installable should be built). Same as 'spman' by default.
         * stmpdir - a temporary directory on the SUT.
         * btmpdir - path to temporary directory on the build host (same as 'stmpdir' by default).
         * cpman - a process manager object associated with the controller (local host). Same as
                  'spman' by default.
         * ctmpdir - path to temporary directory on the controller (same as 'stmpdir' by default).
         * debug - a boolean variable for enabling additional debugging messages.
        """

        if not cpman:
            cpman = spman
        if not ctmpdir:
            ctmpdir = stmpdir

        self._prjname = prjname
        self._toolname = toolname
        self._spman = spman
        self._stmpdir = stmpdir
        self._debug = debug
        self._cpman = cpman
        self._bpman = bpman
        self._ctmpdir = ctmpdir
        self._btmpdir = btmpdir
