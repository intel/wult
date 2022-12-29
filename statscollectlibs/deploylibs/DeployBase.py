# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

from pepclibs.helperlibs import ClassHelpers, LocalProcessManager

"""This module provides the base class that includes sharable pieces of the 'Deploy' class."""

class DeployBase(ClassHelpers.SimpleCloseContext):
    """This module provides the base class that includes sharable pieces of the 'Deploy' class."""

    def _init_insts_cats(self, categories):
        """Initialize the dictionaries for categories and installables based on 'self._deploy_info'."""

        # Initialize installables and categories dictionaries.
        self._cats = { cat : {} for cat in categories }
        for name, info in self._deploy_info["installables"].items():
            self._insts[name] = info.copy()
            self._cats[info["category"]][name] = info.copy()

    def __init__(self, prjname, toolname, deploy_info, pman=None, lbuild=False, debug=False):
        """
        The class constructor. The arguments are as follows.
          * prjname - name of the project the 'toolname' belong to.
          * toolname - name of the tool to deploy.
          * deploy_info - a dictionary describing the tool to deploy. Check
                          'DeployInstallableBase.__init__()' for more information.
          * pman - the process manager object that defines the SUT to deploy to (local host by
                   default).
          * lbuild - by default, everything is built on the SUT, but if 'lbuild' is 'True', then
                     everything is built on the local host.
          * debug - if 'True', be more verbose and do not remove the temporary directories in case
                    of a failure.
        """

        self._prjname = prjname
        self._toolname = toolname
        self._deploy_info = deploy_info
        self._lbuild = lbuild
        self._debug = debug

        self._spman = None # Process manager associated with the SUT.
        self._bpman = None # Process manager associated with the build host.
        self._cpman = None # Process manager associated with the controller (local host).
        self._insts = {}   # Installables information.
        self._cats = {}    # Lists of installables in every category.

        self._close_spman = None
        self._close_cpman = None

        if pman:
            self._spman = pman
            self._close_spman = False
            self._cpman = LocalProcessManager.LocalProcessManager()
            self._close_cpman = True
        else:
            self._spman = LocalProcessManager.LocalProcessManager()
            self._close_spman = True
            self._cpman = self._spman
            self._close_cpman = False

        if self._lbuild:
            self._bpman = self._cpman
        else:
            self._bpman = self._spman

    def close(self):
        """Uninitialize the object."""

        ClassHelpers.close(self, close_attrs=("_spman", "_cpman"), unref_attrs=("_bpman",))
