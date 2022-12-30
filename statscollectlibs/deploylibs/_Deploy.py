# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module provides the API for deploying the 'stats-collect' tool."""

import logging
from pepclibs.helperlibs import ArgParse
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.deploylibs import DeployBase, DeployPyHelpers

_LOG = logging.getLogger()

# The supported installable categories.
_CATEGORIES = {"pyhelpers"  : "python helper program"}

def add_deploy_cmdline_args(toolname, deploy_info, subparsers, func, argcomplete=None):
    """
    Add the the 'deploy' command to 'argparse' data. The input arguments are as follows.
      * toolname - name of the tool to add the 'deploy' command for.
      * deploy_info - a dictionary describing the tool to deploy, same as in
                      'DeployInstallableBase.__init__()'.
      * subparsers - the 'argparse' subparsers to add the 'deploy' command to.
      * func - the 'deploy' command handling function.
      * argcomplete - optional 'argcomplete' command-line arguments completer object.
    """

    cats = { cat : [] for cat in _CATEGORIES }
    for name, info in deploy_info["installables"].items():
        cats[info["category"]].append(name)

    what = "helpers"

    text = f"Compile and deploy {toolname} {what}."
    descr = f"""Compile and deploy {toolname} {what} to the SUT (System Under Test), which can be
                can be either local or a remote host, depending on the '-H' option. By default,
                everything is built on the SUT, but the '--local-build' can be used for building
                on the local system."""

    parser = subparsers.add_parser("deploy", help=text, description=descr)

    text = f"""Build {what} locally, instead of building on HOSTNAME (the SUT)."""
    parser.add_argument("--local-build", dest="lbuild", action="store_true", help=text)

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

class Deploy(DeployBase.DeployBase):
    """
    This class provides the 'deploy()' method which can be used for deploying the dependencies of
    the "stats-collect" tool.
    """

    def _get_deployables(self, category):
        """Yields all deployable names for category 'category' (e.g., "drivers")."""

        for inst_info in self._cats[category].values():
            for deployable in inst_info["deployables"]:
                yield deployable

    def _deploy(self):
        """Deploy python helpers to the SUT."""

        pyhelpers = self._cats.get("pyhelpers")
        dep_pyhelpers = DeployPyHelpers.DeployPyHelpers("wult", self._toolname,
                            self._get_deployables("pyhelpers"), self._spman, self._bpman,
                            self._cpman, self._get_stmpdir(), self._btmpdir, self._get_ctmpdir(),
                            debug=self._debug)
        dep_pyhelpers.deploy(self._toolname, list(pyhelpers))

    def deploy(self):
        """Deploy all the installables to the SUT."""

        if not self._cats.get("pyhelpers"):
            return

        try:
            if self._spman.is_remote:
                self._stmpdir = self._get_stmpdir()
            else:
                self._stmpdir = self._get_ctmpdir()

            if self._lbuild:
                self._btmpdir = self._get_ctmpdir()
            else:
                self._btmpdir = self._stmpdir
        except Exception as err:
            self._remove_tmpdirs()
            msg = Error(err).indent(2)
            raise Error(f"failed to deploy the '{self._toolname}' tool:\n{msg}") from err

        try:
            self._deploy()
        finally:
            self._remove_tmpdirs()

    def __init__(self, toolname, deploy_info, pman=None, lbuild=False, tmpdir_path=None,
                 keep_tmpdir=False, debug=False):
        """
        The class constructor. The arguments are the same as in 'DeployBase.__init()'.
        """

        super().__init__("wult", toolname, deploy_info, pman=pman, lbuild=lbuild,
                         tmpdir_path=tmpdir_path, keep_tmpdir=keep_tmpdir, debug=debug)

        self._init_insts_cats(_CATEGORIES)

        # Python helpers need to be deployed only to a remote host. The local host should already
        # have them:
        #   * either deployed via 'setup.py'.
        #   * or if running from source code, present in the source code.
        if not self._spman.is_remote:
            for installable in self._cats["pyhelpers"]:
                del self._insts[installable]
            self._cats["pyhelpers"] = {}
