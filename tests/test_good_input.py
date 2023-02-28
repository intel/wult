#!/usr/bin/env python3
#
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Antti Laakso <antti.laakso@linux.intel.com>

"""
Test module for 'wult' project. Tests following commands for 'wult' and 'ndl':
- filter
- report
- calc
"""

# pylint: disable=redefined-outer-name
# pylint: disable=unused-import

from common import tool

def test_good_input_data(tool):
    """Test 'filter', 'report', and 'calc' commands for good input data."""

    for cmd in ("filter", "report", "calc"):
        for args in tool.good_paths:
            if cmd == "filter":
                args = f"--exclude index!=0 {args}"
            tool.command(cmd, args)
