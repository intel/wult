#!/usr/bin/env python3
#
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
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
# pylint: disable=unused-import

import pytest
from common import tool
from pepclibs.helperlibs import Exceptions

def test_bad_input_data(tool):
    """Test 'report', 'calc', and 'start' commands for bad input data."""

    for cmd in ("filter", "report", "start", "calc"):
        for args in tool.bad_paths:
            if cmd == "filter":
                args = f"--rfilt index!=0 {args}"
            with pytest.raises(Exceptions.Error):
                tool.command(cmd, args)

def test_bad_filter_names(tool):
    """Test 'filter' and 'calc' commands for bad filter names."""

    for cmd in ("filter", "calc", "report"):
        for argname in ("rfilt", "rsel", "cfilt", "csel"):
            # 'report' command don't have 'cfilt' and 'csel' arguments.
            if cmd == "report" and argname.startswith("c"):
                continue
            # Need only one good testdata path.
            args = f"--{argname} 'bad_filter' {tool.good_paths[0]}"
            with pytest.raises(Exceptions.Error):
                tool.command(cmd, args)

def test_calc(tool):
    """Test 'calc' command for bad arguments."""

    with pytest.raises(Exceptions.Error):
        tool.command("calc", f"-f 'bad_function' {tool.good_paths[0]}")
