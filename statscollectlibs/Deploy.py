# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module provides the API for deploying the 'stats-collect' tool."""

import logging
from pathlib import Path
from pepclibs.helperlibs import ClassHelpers, LocalProcessManager
from pepclibs.helperlibs.Exceptions import ErrorExists

_LOG = logging.getLogger()

# The supported installable categories.
_CATEGORIES = {"pyhelpers"  : "python helper program"}

def get_insts_cats(deploy_info, categories):
    """Build and return dictionaries for categories and installables based on 'deploy_info'."""

    cats = {}
    insts = {}

    # Initialize installables and categories dictionaries.
    cats = { cat : {} for cat in categories }
    for name, info in deploy_info["installables"].items():
        insts[name] = info.copy()
        cats[info["category"]][name] = info.copy()

    return insts, cats

class Deploy(ClassHelpers.SimpleCloseContext):
    """
    This class provides the 'deploy()' method which can be used for deploying the dependencies of
    the "stats-collect" tool.
    """

    def _get_stmpdir(self):
        """Creates a temporary directory on the SUT and returns its path."""

        if not self._stmpdir:
            self._stmpdir_created = True
            if not self._tmpdir_path:
                self._stmpdir = self._spman.mkdtemp(prefix=f"{self._toolname}-")
            else:
                self._stmpdir = self._tmpdir_path
                try:
                    self._spman.mkdir(self._stmpdir, parents=True, exist_ok=False)
                except ErrorExists:
                    self._stmpdir_created = False

        return self._stmpdir

    def _init_insts_cats(self):
        """Helper function for the constructor. Initialises '_ints' and '_cats'."""

        self._ints, self._cats = get_insts_cats(self._deploy_info, _CATEGORIES)

    def __init__(self, toolname, deploy_info, pman=None, lbuild=False, tmpdir_path=None,
                 keep_tmpdir=False, debug=False):
        """
        The class constructor. The arguments are as follows.
          * toolname - name of the tool to create the deployment object for.
          * deploy_info - a dictionary describing the tool to deploy. Check '_DeployBase.__init__()'
                          for more information.
          * pman - the process manager object that defines the SUT to deploy to (local host by
                   default).
          * lbuild - by default, everything is built on the SUT, but if 'lbuild' is 'True', then
                     everything is built on the local host.
          * tmpdir_path - if provided, use this path as a temporary directory (by default, a random
                           temporary directory is created).
          * keep_tmpdir - if 'False', remove the temporary directory when finished. If 'True', do
                          not remove it.
          * debug - if 'True', be more verbose and do not remove the temporary directories in case
                    of a failure.
        """

        self._toolname = toolname
        self._deploy_info = deploy_info
        self._lbuild = lbuild
        self._tmpdir_path = tmpdir_path
        self._keep_tmpdir = keep_tmpdir
        self._debug = debug

        if self._tmpdir_path:
            self._tmpdir_path = Path(self._tmpdir_path)

        self._insts = {}   # Installables information.
        self._cats = {}    # Lists of installables in every category.
        self._init_insts_cats()

        self._spman = None   # Process manager associated with the SUT.
        self._bpman = None   # Process manager associated with the build host.
        self._cpman = None   # Process manager associated with the controller (local host).
        self._stmpdir = None # Temporary directory on the SUT.
        self._ctmpdir = None # Temporary directory on the controller (local host).
        self._btmpdir = None # Temporary directory on the build host.
        self._stmpdir_created = None # Temp. directory on the SUT has been created.
        self._ctmpdir_created = None # Temp. directory on the controller has been created.

        self._cpman = LocalProcessManager.LocalProcessManager()

        if pman:
            self._spman = pman
            self._close_spman = False
        else:
            self._spman = LocalProcessManager.LocalProcessManager()
            self._close_spman = True


        if self._lbuild:
            self._bpman = self._cpman
        else:
            self._bpman = self._spman


    def _remove_tmpdirs(self):
        """Remove temporary directories."""

        spman = getattr(self, "_spman", None)
        cpman = getattr(self, "_cpman", None)
        if not cpman or not spman:
            return

        ctmpdir = getattr(self, "_ctmpdir", None)
        stmpdir = getattr(self, "_stmpdir", None)

        if self._keep_tmpdir:
            _LOG.info("Preserved the following temporary directories:")
            if stmpdir:
                _LOG.info(" * On the SUT (%s): %s", spman.hostname, stmpdir)
            if ctmpdir and ctmpdir is not stmpdir:
                _LOG.info(" * On the controller (%s): %s", cpman.hostname, ctmpdir)
        else:
            if stmpdir and self._stmpdir_created:
                spman.rmtree(self._stmpdir)
            if ctmpdir and cpman is not spman and self._ctmpdir_created:
                cpman.rmtree(self._ctmpdir)

    def close(self):
        """Uninitialize the object."""

        ClassHelpers.close(self, close_attrs=("_cpman", "_spman"), unref_attrs=("_bpman",))
