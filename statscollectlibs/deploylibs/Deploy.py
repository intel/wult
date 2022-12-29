# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module provides the API for deploying the 'stats-collect' tool."""

import logging
import os
from pathlib import Path
from pepclibs.helperlibs import ArgParse, ClassHelpers, LocalProcessManager, ProjectFiles
from pepclibs.helperlibs.Exceptions import Error, ErrorExists, ErrorNotFound
from statscollectlibs.deploylibs import DeployPyHelpers

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

    def _get_ctmpdir(self):
        """Creates a temporary directory on the controller and returns its path."""

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

    def _init_insts_cats(self):
        """Helper function for the constructor. Initialises '_ints' and '_cats'."""

        self._insts, self._cats = get_insts_cats(self._deploy_info, _CATEGORIES)

    def __init__(self, toolname, deploy_info, pman=None, lbuild=False, tmpdir_path=None,
                 keep_tmpdir=False, debug=False):
        """
        The class constructor. The arguments are as follows.
          * toolname - name of the tool to create the deployment object for.
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
