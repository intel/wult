
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module provides the API for deploying Python helpers."""

import logging
from pathlib import Path
from pepclibs.helperlibs import LocalProcessManager
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
from statscollectlibs.helperlibs import ToolHelpers

_LOG = logging.getLogger()

HELPERS_LOCAL_DIR = Path(".local")
HELPERS_SRC_SUBPATH = Path("helpers")

def find_pyhelper_path(pyhelper, deployable=None):
    """
    Find and return path to python helper 'pyhelper' on the local system.
      * pyhelper - the python helper name.
      * deployable - name of the program to find.

    Note about 'pyhelper' vs 'deployable'. Python helpers may come with additional "deployables".
    For example, "stc-agent" comes with the 'ipmi-helper' tool that it uses. Here is a usage
    example.
      * To find path to the "stc-agent" python helper program, use:
        _find_pyhelper_path("stc-agent")
      * To find path to the "ipmi-helper" program which belongs to the "stc-agent" python helper,
        use:
        _find_pyhelper_path("stc-agent", deployable="ipmi-helper")
    """

    if not deployable:
        deployable = pyhelper

    with LocalProcessManager.LocalProcessManager() as lpman:
        try:
            pyhelper_path = lpman.which(deployable)
        except ErrorNotFound as err1:
            _LOG.debug(err1)

            try:
                subpath = HELPERS_SRC_SUBPATH / pyhelper / deployable
                descr=f"the '{deployable}' python helper"
                pyhelper_path = ToolHelpers.find_project_data("wult", subpath, descr=descr)
            except ErrorNotFound as err2:
                errmsg = str(err1).capitalize() + "\n" + str(err2).capitalize()
                raise Error(f"failed to find '{pyhelper}' on the local system.\n{errmsg}") from err2

        pyhelper_path = lpman.abspath(pyhelper_path)

    return pyhelper_path
