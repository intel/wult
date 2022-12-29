# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

import logging
from pathlib import Path
from pepclibs.helperlibs.Exceptions import ErrorExists
from pepclibs.helperlibs import ClassHelpers, LocalProcessManager

"""This module provides the base class that includes sharable pieces of the 'Deploy' class."""

_LOG = logging.getLogger()

class DeployBase(ClassHelpers.SimpleCloseContext):
    """This module provides the base class that includes sharable pieces of the 'Deploy' class."""

    def _get_stmpdir(self):
        """Create a temporary directory on the SUT and return its path."""

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

    def _get_ctmpdir(self):
        """Create a temporary directory on the controller and return its path."""

        if not self._ctmpdir:
            self._ctmpdir_created = True
            if not self._tmpdir_path:
                self._ctmpdir = self._cpman.mkdtemp(prefix=f"{self._toolname}-")
            else:
                self._ctmpdir = self._tmpdir_path
                try:
                    self._cpman.mkdir(self._ctmpdir, parents=True, exist_ok=False)
                except ErrorExists:
                    self._ctmpdir_created = False

        return self._ctmpdir

    def _remove_tmpdirs(self):
        """Remove temporary directories."""

        spman = getattr(self, "_spman", None)
        cpman = getattr(self, "_cpman", None)
        if not cpman or not spman:
            return

        ctmpdir = getattr(self, "_ctmpdir", None)
        stmpdir = getattr(self, "_stmpdir", None)
        keep_tmpdir = getattr(self, "_keep_tmpdir", None)

        preserved = []
        if stmpdir and self._stmpdir_created:
            if not keep_tmpdir:
                spman.rmtree(self._stmpdir)
            else:
                preserved.append(f"On the SUT ({spman.hostname}): {stmpdir}")
        if ctmpdir and cpman is not spman and self._ctmpdir_created:
            if not keep_tmpdir:
                cpman.rmtree(self._ctmpdir)
            else:
                preserved.append(f"On the controller ({cpman.hostname}): {ctmpdir}")

        if preserved:
            _LOG.info("Preserved the following temporary directories:\n * %s", "\n * ".join(preserved))

    def _init_insts_cats(self, categories):
        """Initialize the dictionaries for categories and installables based on 'self._deploy_info'."""

        # Initialize installables and categories dictionaries.
        self._cats = { cat : {} for cat in categories }
        for name, info in self._deploy_info["installables"].items():
            self._insts[name] = info.copy()
            self._cats[info["category"]][name] = info.copy()

    def __init__(self, prjname, toolname, deploy_info, pman=None, lbuild=False, tmpdir_path=None,
                 keep_tmpdir=False, debug=False):
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
          * tmpdir_path - if provided, use this path as a temporary directory (by default, a random
                           temporary directory is created).
          * keep_tmpdir - if 'False', remove the temporary directory when finished. If 'True', do
                          not remove it.
          * debug - if 'True', be more verbose.
        """

        self._prjname = prjname
        self._toolname = toolname
        self._deploy_info = deploy_info
        self._lbuild = lbuild
        self._tmpdir_path = tmpdir_path
        self._keep_tmpdir = keep_tmpdir
        self._debug = debug

        self._spman = None # Process manager associated with the SUT.
        self._bpman = None # Process manager associated with the build host.
        self._cpman = None # Process manager associated with the controller (local host).

        self._close_spman = None
        self._close_cpman = None

        self._insts = {}     # Installables information.
        self._cats = {}      # Lists of installables in every category.
        self._stmpdir = None # Temporary directory on the SUT.
        self._ctmpdir = None # Temporary directory on the controller (local host).
        self._btmpdir = None # Temporary directory on the build host.

        self._stmpdir_created = None # Temp. directory on the SUT has been created.
        self._ctmpdir_created = None # Temp. directory on the controller has been created.

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

        if self._tmpdir_path:
            self._tmpdir_path = Path(self._tmpdir_path)

    def close(self):
        """Uninitialize the object."""

        ClassHelpers.close(self, close_attrs=("_spman", "_cpman"), unref_attrs=("_bpman",))
