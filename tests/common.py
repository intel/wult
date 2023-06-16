#!/usr/bin/env python3
#
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Antti Laakso <antti.laakso@linux.intel.com>

"""Common code for test modules."""

import os
from pathlib import Path
import pytest
from pepclibs.helperlibs import TestRunner
from wulttools.wult import _Wult, ToolInfo as WultToolInfo
from wulttools.ndl import _Ndl, ToolInfo as NdlToolInfo


def run_wult(arguments, exp_exc=None):
    """
    Run wult command and verify the outcome. The arguments are as follows:
     * arguments - the arguments to run the command with, e.g. 'report -o tmpdir'.
     * exp_exc - the expected exception, by default, any exception is considered to be a failure.
                 But when set if the command did not raise the expected exception then the test is
                 considered to be a failure.
    """

    TestRunner.run_tool(_Wult, WultToolInfo.TOOLNAME, arguments, exp_exc=exp_exc)

def run_ndl(arguments, exp_exc=None):
    """Same as 'run_wult()', but runs the 'ndl' command."""

    TestRunner.run_tool(_Ndl, NdlToolInfo.TOOLNAME, arguments, exp_exc=exp_exc)

class CmdLineRunner():
    """Class for running commandline commands."""

    def _has_outdir(self, cmd):
        """Check if 'cmd' command has 'outdir' -option."""

        return "report" in cmd

    def command(self, cmd, arg=None, exp_exc=None):
        """Run commandline tool with arguments."""

        if self._has_outdir(cmd) and self._tmpdir:
            arg += f" -o {self._tmpdir}"

        if not arg:
            arg = ""

        return self._tool_runner(f"{cmd} {arg}", exp_exc=exp_exc)

    def __init__(self, toolname, tool_runner, devid, tmpdir=None):
        """The constructor."""

        self._tmpdir = str(tmpdir)
        self._tool_runner = tool_runner
        self._devid = devid

        tooldir = Path(__file__).parents[1].resolve() # pylint: disable=no-member
        testdataroot = tooldir / "tests" / "testdata"
        self._tool_path = tooldir / toolname
        assert self._tool_path.exists()

        self.good_paths = []
        self.bad_paths = []
        for dirpath, dirnames, _ in os.walk(testdataroot / toolname):
            if dirnames:
                continue
            if "good" in Path(dirpath).parts:
                self.good_paths.append(dirpath)
            else:
                self.bad_paths.append(dirpath)

        assert self.good_paths
        assert self.bad_paths

class WultTest(CmdLineRunner):
    """Class for running tests for 'wult'."""

    def __init__(self, devid, tmpdir=None):
        """The constructor."""

        super().__init__("wult", run_wult, devid, tmpdir)

class NdlTest(CmdLineRunner):
    """Class for running tests for 'ndl'."""

    def __init__(self, devid, tmpdir=None):
        """The constructor."""

        super().__init__("ndl", run_ndl, devid, tmpdir)

@pytest.fixture(params=[WultTest, NdlTest], ids=["wult", "ndl"])
def tool(request, devid, tmp_path_factory):
    """Common fixture to return test object for 'wult' and 'ndl'."""

    tmpdir = tmp_path_factory.mktemp(request.fixturename)
    return request.param(devid, tmpdir=tmpdir)
