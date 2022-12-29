# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module provides the API for deploying the 'stats-collect' tool."""

import os
import logging
from pathlib import Path
from pepclibs.helperlibs import ArgParse, ProjectFiles
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
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

def get_deploy_cmd(pman, toolname):
    """Returns the 'deploy' command suggestion string."""

    cmd = f"{toolname} deploy"
    if pman.is_remote:
        cmd += f" -H {pman.hostname}"
    return cmd

def deployable_not_found(pman, toolname, what, is_helper=True):
    """Raise an exception in case a required driver or helper was not found."""

    err = f"{what} was not found{pman.hostmsg}"
    if is_helper:
        envvar = ProjectFiles.get_project_helpers_envvar(toolname)
        err += f". Here are the options to try.\n" \
               f" * Run '{get_deploy_cmd(pman, toolname)}'.\n" \
               f" * Ensure that {what} is in 'PATH'{pman.hostmsg}.\n" \
               f" * Set the '{envvar}' environment variable to the path of {what}{pman.hostmsg}."
    else:
        err += f"\nConsider running '{get_deploy_cmd(pman, toolname)}'"

    raise ErrorNotFound(err)

def get_installed_helper_path(pman, toolname, helper):
    """
    Tries to figure out path to the directory the 'helper' program is installed at. Returns the
    path in case of success (e.g., '/usr/bin') and raises the 'ErrorNotFound' an exception if the
    helper was not found.
    """

    envvar = ProjectFiles.get_project_helpers_envvar(toolname)
    dirpath = os.environ.get(envvar)
    if dirpath:
        helper_path = Path(dirpath) / helper
        if pman.is_exe(helper_path):
            return helper_path

    helper_path = pman.which(helper, must_find=False)
    if helper_path:
        return helper_path

    # Check standard paths.
    homedir = pman.get_homedir()
    stardard_paths = (f"{homedir}/.local/bin", "/usr/bin", "/usr/local/bin", "/bin",
                      f"{homedir}/bin")

    for dirpath in stardard_paths:
        helper_path = Path(dirpath) / helper
        if pman.is_exe(helper_path):
            return helper_path

    return deployable_not_found(pman, toolname, f"the '{helper}' program", is_helper=True)

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
        """Deploy helpers (including python helpers) to the SUT."""

        pyhelpers = self._cats.get("pyhelpers")
        if not pyhelpers:
            return

        dep_pyhelpers = DeployPyHelpers.DeployPyHelpers("wult", self._toolname,
                            self._get_deployables("pyhelpers"), self._spman, self._bpman,
                            self._cpman, self._get_stmpdir(), self._btmpdir, self._get_ctmpdir(),
                            debug=self._debug)
        dep_pyhelpers.deploy(self._toolname, list(pyhelpers))

    def _adjust_installables(self):
        """
        Adjust the list of installables that have to be deployed to the SUT based on various
        conditions, such as kernel version.
        """

        # Python helpers need to be deployed only to a remote host. The local host should already
        # have them:
        #   * either deployed via 'setup.py'.
        #   * or if running from source code, present in the source code.
        if not self._spman.is_remote:
            for installable in self._cats["pyhelpers"]:
                del self._insts[installable]
            self._cats["pyhelpers"] = {}

    def deploy(self):
        """
        Deploy all the required installables to the SUT (drivers, helpers, etc).

        We distinguish between 3 type of helper programs, or just helpers: simple helpers and python
        helpers.

        1. Simple helpers (shelpers) are stand-alone independent programs, which come in form of a
           single executable file.
        2. Python helpers (pyhelpers) are helper programs written in python. Unlike simple helpers,
           they are not totally independent, but they depend on various python modules. Deploying a
           python helpers is trickier because all python modules should also be deployed.
        """

        self._adjust_installables()

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

        super().__init__("wult", toolname, deploy_info, pman=pman, lbuild=lbuild, tmpdir_path=tmpdir_path,
                         keep_tmpdir=keep_tmpdir, debug=debug)

        self._init_insts_cats(_CATEGORIES)
