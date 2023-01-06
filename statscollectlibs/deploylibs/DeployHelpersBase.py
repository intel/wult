# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module provides a base class for deploying helpers."""

import logging
import os
from pathlib import Path
from pepclibs.helperlibs.Exceptions import Error
from pepclibs.helperlibs import ProjectFiles
from statscollectlibs.deploylibs import DeployInstallableBase

HELPERS_DEPLOY_SUBDIR = Path(".local")
HELPERS_SRC_SUBDIR = Path("helpers")

_LOG = logging.getLogger()

class DeployHelpersBase(DeployInstallableBase.DeployInstallableBase):
    """This base class can be inherited from to provide the API for deploying helpers."""

    def _prepare(self, helpersrc, helpers):
        """
        Build and prepare helpers for deployment. The arguments are as follows:
          * helpersrc - path to the helpers base directory on the controller.
          * helpers - same as in the 'deploy()' method.

        This method should be implemented by a child class.
        """

        raise NotImplementedError()

    def _get_helpers_deploy_path(self):
        """Returns path the directory the helpers should be deployed to."""

        helpers_path = os.environ.get("WULT_HELPERSPATH")
        if not helpers_path:
            helpers_path = self._spman.get_homedir() / HELPERS_DEPLOY_SUBDIR / "bin"
        return Path(helpers_path)

    def deploy(self, helpers):
        """
        Deploy helpers to the SUT. The arguments are as follows.
          * helpers - the helpers to deploy. Should be a collection of helper names (e.g., a list).
                      These are not deployable names, these are helper directory names in the
                      'HELPERS_DEPLOY_SUBDIR' sub-directory.

        This is the default implementation which deploys the helpers by running 'make' and 'make
        install'.
        """

        if not helpers:
            return

        # We assume all helpers are in the same base directory.
        helper_path = HELPERS_SRC_SUBDIR/f"{helpers[0]}"
        what = f"sources of {self._what}"
        helpersrc = ProjectFiles.find_project_data("wult", helper_path, what=what)
        helpersrc = helpersrc.parent

        # Make sure all helpers are available.
        for helper in helpers:
            helperdir = helpersrc / helper
            if not helperdir.is_dir():
                raise Error(f"path '{helperdir}' does not exist or it is not a directory")

        self._prepare(helpersrc, helpers)

        deploy_path = self._get_helpers_deploy_path()

        # Make sure the the destination deployment directory exists.
        self._spman.mkdir(deploy_path, parents=True, exist_ok=True)

        # Deploy all helpers.
        _LOG.info("Deploying %s to '%s'%s", self._what, deploy_path, self._spman.hostmsg)

        helpersdst = self._stmpdir / "helpers_deployed"
        _LOG.debug("deploying helpers to '%s'%s", helpersdst, self._spman.hostmsg)

        for helper in helpers:
            bhelperpath = f"{self._btmpdir}/{helper}"
            shelperpath = f"{self._stmpdir}/{helper}"

            if not self._bpman.is_remote and self._spman.is_remote:
                # We built the helpers locally, but have to install them on a remote SUT. Copy them
                # to the SUT first.
                self._spman.rsync(str(bhelperpath) + "/", shelperpath,
                                  remotesrc=self._bpman.is_remote, remotedst=self._spman.is_remote)

            cmd = f"make -C '{shelperpath}' install PREFIX='{helpersdst}'"
            stdout, stderr = self._spman.run_verify(cmd)
            self._log_cmd_output(stdout, stderr)

            self._spman.rsync(str(helpersdst) + "/bin/", deploy_path,
                              remotesrc=self._spman.is_remote,
                              remotedst=self._spman.is_remote)

    def __init__(self, prjname, toolname, what, spman, bpman, stmpdir, btmpdir, cpman=None,
                 ctmpdir=None, debug=False):
        """
        Class constructor. Arguments are the same as in
        'DeployInstallableBase.DeployInstallableBase()' except for the following:
         * what - a human-readable string describing the helpers that are being deployed.
        """

        self._what = what
        super().__init__(prjname, toolname, spman, bpman, stmpdir, btmpdir, cpman=cpman,
                         ctmpdir=ctmpdir, debug=False)
