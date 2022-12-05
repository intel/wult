# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module provides a base class for deploying installables."""


class DeployInstallableBase:
    """This base class can be inherited from to provide the API for deploying helpers."""

    def __init__(self, bpman, spman, btmpdir):
        """
        Class constructor. Arguments are as follows:
         * bpman - process manager associated with the build host.
         * spman - process manager associated with the SUT.
         * btmpdir - a path to a temporary directory on the build host.
        """

        self._bpman = bpman
        self._spman = spman
        self._btmpdir = btmpdir
