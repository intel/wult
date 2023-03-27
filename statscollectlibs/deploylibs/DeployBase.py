# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides the base class that includes sharable pieces of the 'Deploy' class.

Terminology.
  * category - type of an installable. Currently there are 4 categories: drivers, simple helpers
               (shelpers), python helpers (pyhelpers), and eBPF helpers (bpfhelpers).
  * installable - a sub-project to install on the SUT.
  * deployable - each installable provides one or multiple deployables. For example, one or multiple
                 drivers.

Installable vs deployable.
  * Installables come in the form of source code. Deployables are executable programs (script,
    binary) or kernel drivers.
  * An installable corresponds to a directory with source code. The source code may need to be
    compiled. The compilation results in one or several deployables.
  * Deployables are ultimately copied to the SUT and executed on the SUT.

Helpers types.
    1. Simple helpers (shelpers) are stand-alone independent programs, which come in form of a
       single executable file.
    2. eBPF helpers (bpfhelpers) consist of 2 components: the user-space component and the eBPF
       component. The user-space component is distributed as a source code, and must be compiled.
       The eBPF component is distributed as both source code and in binary
    3. Python helpers (pyhelpers) are helper programs written in python. Unlike simple helpers,
       they are not totally independent, but they depend on various python modules. Deploying a
       python helpers is trickier because all python modules should also be deployed.
"""

import os
import time
import copy
import logging
from pathlib import Path
from pepclibs.helperlibs.Exceptions import Error, ErrorExists, ErrorNotFound
from pepclibs.helperlibs import ClassHelpers, ProcessManager, LocalProcessManager, ProjectFiles

_LOG = logging.getLogger()

# The supported installable categories.
CATEGORIES = {"drivers"    : "kernel driver",
              "shelpers"   : "simple helper program",
              "pyhelpers"  : "python helper program",
              "bpfhelpers" : "eBPF helper program"}

def get_deploy_cmd(pman, toolname):
    """Returns the command that should be run to deploy the 'toolname' tool."""

    cmd = f"{toolname} deploy"
    if pman.is_remote:
        cmd += f" -H {pman.hostname}"
    return cmd

def get_deploy_suggestion(pman, prjname, toolname, what, is_helper):
    """
    Return a string suitable for using for an error message in a situation when an deployable was
    not found. The arguments are as follows.
      * pman - the process manager object for the host the deployable was supposed to be found on.
      * prjname - name of the project the deployable belongs to.
      * toolname - name of the tool the deployable belongs to.
      * what - a human-readable name of the deployable.
      * is_helper - the deployable is a helper program if 'True', otherwise 'False'.
    """

    if not is_helper:
        return f"Please run '{get_deploy_cmd(pman, toolname)}'"

    envvar = ProjectFiles.get_project_helpers_envvar(prjname)
    msg = f"Here are the options to try.\n" \
          f" * Run '{get_deploy_cmd(pman, toolname)}'.\n" \
          f" * Ensure that {what} is in 'PATH'{pman.hostmsg}.\n" \
          f" * Set the '{envvar}' environment variable to the path of {what}{pman.hostmsg}."
    return msg

def get_installed_helper_path(prjname, toolname, helper, pman=None):
    """
    Search for helper program 'helper' belonging to the 'prjname' project. The arguments are as
    follows:
      * prjname - name of the project the helper program belongs to.
      * toolname - name of the tool the helper program belongs to.
      * helper - the helper program to find.
      * pman - the process manager object for the host to find the helper on (local host by
               default).

    Return helper path in case of success, raises the 'ErrorNotFound' otherwise.
    """

    with ProcessManager.pman_or_local(pman) as wpman:
        try:
            return ProjectFiles.find_project_helper(prjname, helper, pman=wpman)
        except ErrorNotFound as err:
            what = f"the '{helper}' helper program"
            err = f"{err}\n"
            err += get_deploy_suggestion(wpman, prjname, toolname, what, is_helper=True)
            raise ErrorNotFound(err) from None

def get_insts_cats(deploy_info):
    """
    Build and return dictionaries for categories and installables based on 'deploy_info'. Returns a
    tuple of '(insts, cats)', where:
      * 'insts' is the same as 'deploy_info["installables"]' (except for some added sub-keys).
      * 'cats' is includes installables information arranged by the category.
    """

    insts = {}
    cats = {cat : {} for cat in CATEGORIES}

    for name, info in deploy_info["installables"].items():
        info = copy.deepcopy(info)
        info["name"] = name

        # Add category description to the installable information dictionary.
        catname = info["category"]
        info["category_descr"] = CATEGORIES[catname]

        insts[name] = info
        cats[catname][name] = info

    return insts, cats

class DeployCheckBase(ClassHelpers.SimpleCloseContext):
    """
    This is a base class for verifying whether all the required installables have been deployed and
    up-to-date.
    """

    @staticmethod
    def _get_newest_mtime(path):
        """Find and return the most recent modification time of files in paths 'paths'."""

        newest = 0
        if not path.is_dir():
            mtime = path.stat().st_mtime
            if mtime > newest:
                newest = mtime
        else:
            for root, _, files in os.walk(path):
                for file in files:
                    mtime = Path(root, file).stat().st_mtime
                    if mtime > newest:
                        newest = mtime

        if not newest:
            raise Error(f"no files found in the '{path}'")
        return newest

    def _get_deployables(self, category):
        """Yield all deployable names for category 'category' (e.g., "drivers")."""

        for inst_info in self._cats[category].values():
            for deployable in inst_info["deployables"]:
                yield deployable

    def _get_installed_deployable_path(self, deployable):
        """Same as 'DeployBase.get_installed_helper_path()'."""
        return get_installed_helper_path(self._prjname, self._toolname, deployable,
                                         pman=self._spman)

    def _get_installable_by_deployable(self, deployable):
        """Returns installable name and information dictionary for a deployable."""

        for installable, inst_info in self._insts.items():
            if deployable in inst_info["deployables"]:
                break
        else:
            raise Error(f"bad deployable name '{deployable}'")

        return installable # pylint: disable=undefined-loop-variable

    def _get_deployable_print_name(self, installable, deployable):
        """Returns a nice, printable human-readable name of a deployable."""

        cat_descr = self._insts[installable]["category_descr"]
        if deployable != installable:
            return f"the '{deployable}' component of the '{installable}' {cat_descr}"
        return f"the '{deployable}' {cat_descr}"

    def _deployable_not_found(self, deployable):
        """
        Called in a situation when 'deployable' was not found. Formats an error message and
        raises 'ErrorNotFound'.
        """

        installable = self._get_installable_by_deployable(deployable)
        what = self._get_deployable_print_name(installable, deployable)
        is_helper = self._insts[installable]["category"] != "drivers"

        err = get_deploy_suggestion(self._spman, self._prjname, self._toolname, what, is_helper)
        raise ErrorNotFound(err) from None

    def _warn_deployable_out_of_date(self, deployable):
        """Print a warning about the 'what' deployable not being up-to-date."""

        installable = self._get_installable_by_deployable(deployable)
        what = self._get_deployable_print_name(installable, deployable)

        _LOG.warning("%s may be out of date%s\nConsider running '%s'",
                     what, self._spman.hostmsg, get_deploy_cmd(self._spman, self._toolname))

    def _check_deployable_up_to_date(self, deployable, srcpath, dstpath):
        """
        Check that a deployable at 'dstpath' on SUT is up-to-date by comparing its 'mtime' to the
        source (code) of the deployable at 'srcpath' on the controller.
        """

        if self._time_delta is None:
            if self._spman.is_remote:
                # Take into account the possible time difference between local and remote
                # systems.
                self._time_delta = time.time() - self._spman.time_time()
            else:
                self._time_delta = 0

        src_mtime = self._get_newest_mtime(srcpath)
        dst_mtime = self._spman.get_mtime(dstpath)

        if src_mtime > self._time_delta + dst_mtime:
            _LOG.debug("src mtime %d > %d + dst mtime %d\nsrc: %s\ndst %s",
                       src_mtime, self._time_delta, dst_mtime, srcpath, dstpath)
            self._warn_deployable_out_of_date(deployable)

    def _check_deployment(self):
        """
        Check if all the required installables have been deployed and up-to-date. Has to be
        implemented by the sub-class.
        """

        raise NotImplementedError()

    def check_deployment(self):
        """Check if all the required installables have been deployed and up-to-date."""

        self._time_delta = None
        self._check_deployment()

    def __init__(self, prjname, toolname, deploy_info, pman=None):
        """
        The class constructor. The arguments are as follows.
          * prjname - name of the project 'toolname' belongs to.
          * toolname - name of the tool to check the deployment for.
          * deploy_info - a dictionary describing the tool to deploy. Check 'DeployBase.__init__()'
                          for more information.
          * pman - the process manager object that defines the SUT to check the deployment at (local
            host by default).
        """

        self._prjname = prjname
        self._toolname = toolname

        self._insts = None # Installables information.
        self._cats = None  # Lists of installables in every category.
        self._time_delta = None

        if pman:
            self._spman = pman
            self._close_spman = False
        else:
            self._spman = LocalProcessManager.LocalProcessManager()
            self._close_spman = True

        self._insts, self._cats = get_insts_cats(deploy_info)

    def close(self):
        """Uninitialize the object."""
        ClassHelpers.close(self, close_attrs=("_spman",))


class DeployBase(ClassHelpers.SimpleCloseContext):
    """This module provides the base class that includes sharable pieces of the 'Deploy' class."""

    def _get_deployables(self, category):
        """Yield all deployables for category 'category'."""

        for inst_info in self._cats[category].values():
            for deployable in inst_info["deployables"]:
                yield deployable

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

    def _get_btmpdir(self):
        """Create a temporary directory on the build host and return its path."""

        if self._lbuild:
            self._btmpdir = self._get_ctmpdir()
        else:
            self._btmpdir = self._get_stmpdir()

        return self._btmpdir

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
            _LOG.info("Preserved the following temporary directories:\n * %s",
                      "\n * ".join(preserved))

    def __init__(self, prjname, toolname, deploy_info, pman=None, lbuild=False, tmpdir_path=None,
                 keep_tmpdir=False, debug=False):
        """
        The class constructor. The arguments are as follows.
          * prjname - name of the project 'toolname' belongs to.
          * toolname - name of the tool to deploy.
          * deploy_info - a dictionary describing what should be deployed.
          * pman - the process manager object that defines the SUT to deploy to (local host by
                   default).
          * lbuild - by default, everything is built on the SUT, but if 'lbuild' is 'True', then
                     everything is built on the local host.
          * tmpdir_path - if provided, use this path as a temporary directory (by default, a random
                           temporary directory is created).
          * keep_tmpdir - if 'False', remove the temporary directory when finished. If 'True', do
                          not remove it.
          * debug - if 'True', be more verbose.

        The 'deploy_info' dictionary describes the tool to deploy and its dependencies. It should
        have the following structure.

        {
            "installables" : {
                Installable name 1 : {
                    "category" : category name of the installable ("drivers", "shelpers", etc).
                    "minkver"  : minimum SUT kernel version required for the installable.
                    "deployables" : list of deployables this installable provides.
                },
                Installable name 2 : {},
                ... etc for every installable ...
            }
        }

        Please, refer to module docstring for more information.
        """

        self._prjname = prjname
        self._toolname = toolname
        self._lbuild = lbuild
        self._tmpdir_path = tmpdir_path
        self._keep_tmpdir = keep_tmpdir
        self._debug = debug

        self._spman = None # Process manager associated with the SUT.
        self._bpman = None # Process manager associated with the build host.
        self._cpman = None # Process manager associated with the controller (local host).

        self._close_spman = None
        self._close_cpman = None

        self._insts = None   # Installables information.
        self._cats = None    # Lists of installables in every category.
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

        self._insts, self._cats = get_insts_cats(deploy_info)

    def close(self):
        """Uninitialize the object."""

        ClassHelpers.close(self, close_attrs=("_spman", "_cpman"), unref_attrs=("_bpman",))
