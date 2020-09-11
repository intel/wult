#!/usr/bin/env python3
#
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Antti Laakso <antti.laakso@linux.intel.com>

"""
Test module for 'wult' project. Includes following bad input tests for both, 'wult', and 'ndl':
- Non-existing device ID.
- Bad filter name.
- Bad function name.
- Empty CSV -file.
- Random data in CSV -file.
- Too short line.
- Too long line.
- Directory as input file.
- "/dev/null" as input file.
- "/dev/urandom" as input file.
"""

# pylint: disable=redefined-outer-name

import os
import subprocess
from pathlib import Path
import pytest
from wultlibs.helperlibs import Exceptions

class CmdLineRunner():
    """Class for running commandline commands."""

    @staticmethod
    def _command(cmd):
        """Run 'cmd' command and return output, if any."""

        try:
            result = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            raise Exceptions.Error(str(err))
            #raise Exception(str(err))

        if not result:
            return None

        return result.decode("utf-8").strip()

    def _has_outdir(self, cmd):
        """Check if 'cmd' command has 'outdir' -option."""

        cmd = [self._tool_path, cmd, "-h"]
        helptext = self._command(cmd)

        return "outdir" in helptext

    def command(self, cmd, arg=None):
        """Run commandline tool with arguments."""

        if self._has_outdir(cmd) and self._tmpdir:
            arg += f" -o {self._tmpdir}"

        cmd = [self._tool_path, cmd]
        if arg:
            cmd += arg.split()

        return self._command(cmd)

    def __init__(self, toolname, devid, tmpdir=None):
        """The constructor."""

        self._tmpdir = str(tmpdir)
        self._devid = devid

        tooldir = Path(__file__).parents[1].resolve()
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

        super().__init__("wult", devid, tmpdir)

class NdlTest(CmdLineRunner):
    """Class for running tests for 'ndl'."""

    def __init__(self, devid, tmpdir=None):
        """The constructor."""

        super().__init__("ndl", devid, tmpdir)

@pytest.fixture(params=[WultTest, NdlTest], ids=["wult", "ndl"])
def tool(request, devid, tmp_path_factory):
    """Common fixture to return test object for 'wult' and 'ndl'."""

    tmpdir = tmp_path_factory.mktemp(request.fixturename)
    return request.param(devid, tmpdir=tmpdir)

def test_bad_input_data(tool):
    """Test 'report', 'stats', and 'start' commands for bad input data."""

    for cmd in ("filter", "report", "start", "stats"):
        for args in tool.bad_paths:
            if cmd == "filter":
                args = f"--rfilt 'index!=0' {args}"
            with pytest.raises(Exceptions.Error):
                tool.command(cmd, args)

def test_bad_filter_names(tool):
    """Test 'filter' and 'stats' commands for bad filter names."""

    for cmd in ("filter", "stats", "report"):
        for argname in ("rfilt", "rsel", "cfilt", "csel"):
            # 'report' command don't have 'cfilt' and 'csel' arguments.
            if cmd == "report" and argname.startswith("c"):
                continue
            # Need only one good testdata path.
            args = f"--{argname} 'bad_filter' {tool.good_paths[0]}"
            with pytest.raises(Exceptions.Error):
                tool.command(cmd, args)

def test_stats(tool):
    """Test 'stats' command for bad arguments."""

    with pytest.raises(Exceptions.Error):
        tool.command("stats", f"-f 'bad_function' {tool.good_paths[0]}")
