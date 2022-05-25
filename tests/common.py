#!/usr/bin/env python3
#
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Antti Laakso <antti.laakso@linux.intel.com>

"""Common code for test modules."""

import os
import logging
import subprocess
from pathlib import Path
import pytest
from pepclibs.helperlibs.Exceptions import Error

logging.basicConfig(level=logging.DEBUG)
_LOG = logging.getLogger()

class CmdLineRunner():
    """Class for running commandline commands."""

    @staticmethod
    def _command(cmd):
        """Run 'cmd' command and return output, if any."""

        _LOG.debug("running: %s", " ".join([str(elt) for elt in cmd]))

        try:
            result = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            raise Error(str(err)) from err

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
