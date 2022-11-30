# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module provides a base class for deploying helpers."""

from pathlib import Path

HELPERS_LOCAL_DIR = Path(".local")
HELPERS_SRC_SUBPATH = Path("helpers")

class DeployHelpersBase:
    """This base class can be inherited from to provide the API for deploying helpers."""

    def prepare(self, helpersrc, helpers):
        """
        Build and prepare helpers for deployment. The arguments are as follows:
          * helpersrc - path to the helpers base directory on the controller.
          * helpers - helpers to build and prepare for deployment.

        This method should be implemented by a child class.
        """

        raise NotImplementedError()

    def __init__(self):
        """Class constructor."""

        return
