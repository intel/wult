# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module provides the API for deploying the 'stats-collect' tool."""

import os
import time
import logging
from pathlib import Path
from pepclibs.helperlibs import ArgParse, LocalProcessManager, ClassHelpers, ProjectFiles
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
from statscollectlibs.deploylibs import DeployBase, _DeployPyHelpers, DeployHelpersBase

_LOG = logging.getLogger()

def add_deploy_cmdline_args(toolname, subparsers, func, argcomplete=None):
    """
    Add the the 'deploy' command to 'argparse' data. The input arguments are as follows.
      * toolname - name of the tool to add the 'deploy' command for.
      * subparsers - the 'argparse' subparsers to add the 'deploy' command to.
      * func - the 'deploy' command handling function.
      * argcomplete - optional 'argcomplete' command-line arguments completer object.
    """

    text = f"Deploy {toolname} helpers."
    descr = f"""Deploy {toolname} helpers to a remote SUT (System Under Test)."""
    parser = subparsers.add_parser("deploy", help=text, description=descr)

    text = f"""When '{toolname}' is deployed, a random temporary directory is used. Use this option
               provide a custom path instead. It will be used as a temporary directory on both
               local and remote hosts. This option is meant for debugging purposes."""
    arg = parser.add_argument("--tmpdir-path", help=text)
    if argcomplete:
        arg.completer = argcomplete.completers.DirectoriesCompleter()

    text = f"""Do not remove the temporary directories created while deploying '{toolname}'. This
               option is meant for debugging purposes."""
    parser.add_argument("--keep-tmpdir", action="store_true", help=text)

    ArgParse.add_ssh_options(parser)

    parser.set_defaults(func=func)
    return parser

class DeployCheck(ClassHelpers.SimpleCloseContext):
    """
    This class provides the 'check_deployment()' method which can be used for verifying whether all
    the required installables are available on the SUT.
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
        """Yields all deployable names for category 'category' (e.g., "drivers")."""

        for inst_info in self._cats[category].values():
            for deployable in inst_info["deployables"]:
                yield deployable

    def _get_installed_deployable_path(self, deployable):
        """Same as 'DeployBase.get_installed_helper_path()'."""
        return DeployBase.get_installed_helper_path("wult", self._toolname, deployable,
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

        err = DeployBase.get_deploy_suggestion(self._spman, "wult", self._toolname, what, is_helper)
        raise ErrorNotFound(err) from None

    def _warn_deployable_out_of_date(self, deployable):
        """Print a warning about the 'what' deployable not being up-to-date."""

        installable = self._get_installable_by_deployable(deployable)
        what = self._get_deployable_print_name(installable, deployable)

        _LOG.warning("%s may be out of date%s\nConsider running '%s'",
                     what, self._spman.hostmsg,
                     DeployBase.get_deploy_cmd(self._spman, self._toolname))

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

    def _check_pyhelpers_deployment(self):
        """Check if python helpers are deployed and up-to-date."""

        for pyhelper in self._cats["pyhelpers"]:
            try:
                subpath = DeployHelpersBase.HELPERS_SRC_SUBDIR / pyhelper
                what = f"the '{pyhelper}' python helper program"
                srcpath = ProjectFiles.find_project_data("wult", subpath, what=what)
            except ErrorNotFound:
                continue

            for deployable in self._get_deployables("pyhelpers"):
                try:
                    deployable_path = self._get_installed_deployable_path(deployable)
                except ErrorNotFound:
                    self._deployable_not_found(deployable)
                    break

                if srcpath:
                    self._check_deployable_up_to_date(deployable, srcpath, deployable_path)

    def check_deployment(self):
        """
        Wult and other tools require additional helper programs and drivers to be installed on the
        SUT. This method checks whether the required drivers and helper programs are installed on
        the SUT and are up-to-date.
        """

        self._time_delta = None
        self._check_pyhelpers_deployment()

    def __init__(self, toolname, deploy_info, pman=None):
        """
        The class constructor. The arguments are as follows.
          * toolname - name of the tool to create the deployment object for.
          * deploy_info - a dictionary describing the tool to deploy. Check 'DeployBase.__init__()'
                          for more information.
          * pman - the process manager object that defines the SUT to deploy to (local host by
                   default).

        Please, refer to module docstring for more information.
        """

        self._insts, self._cats = DeployBase.get_insts_cats(deploy_info)
        self._toolname = toolname

        if pman:
            self._spman = pman
            self._close_spman = False
        else:
            self._spman = LocalProcessManager.LocalProcessManager()
            self._close_spman = True

        # Version of the kernel running on the SUT of version of the kernel to compile wult
        # components against.
        self._time_delta = None

    def close(self):
        """Uninitialize the object."""
        ClassHelpers.close(self, close_attrs=("_spman",))

class Deploy(DeployBase.DeployBase):
    """
    This class provides the 'deploy()' method which can be used for deploying the dependencies of
    the "stats-collect" tool.
    """

    def _deploy(self):
        """Deploy python helpers to the SUT."""

        deployables = self._get_deployables("pyhelpers")
        stmpdir = self._get_stmpdir()
        btmpdir = self._get_btmpdir()
        ctmpdir = self._get_ctmpdir()

        with _DeployPyHelpers.DeployPyHelpers("wult", self._toolname, deployables, self._spman,
                                              self._bpman, self._cpman, stmpdir, btmpdir, ctmpdir,
                                              debug=self._debug) as depl:
            pyhelpers = list(self._cats.get("pyhelpers"))
            depl.deploy(pyhelpers)

    def deploy(self):
        """Deploy all the installables to the SUT."""

        if not self._cats.get("pyhelpers"):
            _LOG.info("Nothing to deploy to the local host.")
            return

        try:
            self._deploy()
        finally:
            self._remove_tmpdirs()

    def __init__(self, toolname, deploy_info, pman=None, tmpdir_path=None,
                 keep_tmpdir=False, debug=False):
        """
        The class constructor. The arguments are the same as in 'DeployBase.__init()'.
        """

        super().__init__("wult", toolname, deploy_info, pman=pman, tmpdir_path=tmpdir_path,
                         keep_tmpdir=keep_tmpdir, debug=debug)

        # Python helpers need to be deployed only to a remote host. The local host should already
        # have them:
        #   * either deployed via 'setup.py'.
        #   * or if running from source code, present in the source code.
        if not self._spman.is_remote:
            for installable in self._cats["pyhelpers"]:
                del self._insts[installable]
            self._cats["pyhelpers"] = {}
