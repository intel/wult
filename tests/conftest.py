#!/usr/bin/env python
#
# Copyright (C) 2020 Intel Corporation
# SPDX-License-Identifier: GPL-2.0-only
#
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Author: Antti Laakso <antti.laakso@linux.intel.com>

"""
This configuration file adds the '--devid' option, to allow user to specify device ID to run the
tests on.
"""

def pytest_addoption(parser):
    """Add custom pytest options."""

    text = "The device ID to run the tests for."
    parser.addoption("--devid", action="append", default=["None"], help=text)

def pytest_generate_tests(metafunc):
    """Run tests for the custom options."""

    if 'devid' in metafunc.fixturenames:
        # Remove default option if option provided in commandline.
        devid_option = metafunc.config.getoption('devid')
        if len(devid_option) > 1:
            devid_option = devid_option[1:]
        metafunc.parametrize("devid", devid_option)
