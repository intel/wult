# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module implements several misc. helpers for tools using 'STCAgent'.
"""

# pylint: disable=protected-access

import logging
from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.stcagentlibs import STCAgent

_LOG = logging.getLogger()

def parse_stnames(stnames):
    """
    This is a helper function for tools using this module and receiving the list of statistics in
    form of a string with statistics names separated by a comma. The "!" symbol at the beginning of
    the statistics name means that this statistics should not be collected. The "all" name means
    that all the discovered statistics should be included.

    This function returns a dictionary with the following keys.
      * include: statistics names that should be collected (a 'set()').
      * exclude: statistics names that should not be collected (a 'set()').
      * discover: if 'True', then include all the discovered statistics except for those in
                  'exclude'.
    """

    stconf = {}
    stconf["include"] = set()
    stconf["exclude"] = set()
    stconf["discover"] = False
    stconf["intervals"] = {}

    for stname in Trivial.split_csv_line(stnames):
        if stname == "all":
            stconf["discover"] = True
        elif stname.startswith("!"):
            # The "!" prefix indicates that the statistics must not be collected.
            stconf["exclude"].add(stname[1:])
        else:
            stconf["include"].add(stname)

    STCAgent._check_stnames(stconf["include"])
    STCAgent._check_stnames(stconf["exclude"])
    stconf["include"] -= stconf["exclude"]

    return stconf

def parse_intervals(intervals, stconf):
    """
    This is another helper function for tools using this module, complementary to the
    'parse_stnames()' helper. The 'intervals' argument is a comma-separated list of
    "stname:interval" entries, where 'stname' is the statistics name, and 'interval' is the
    collection interval for this statistics.

    This function requires the 'stconf' dictionary produced by the 'parse_stnames()' helper, and it
    adds intervals information to this dictionary. Namely, it adds the "intervals" key with value
    being an "stname -> interval" dictionary. Intervals are floating point numbers.
    """

    for entry in Trivial.split_csv_line(intervals):
        split = Trivial.split_csv_line(entry, sep=":")
        if len(split) != 2:
            raise Error(f"bad intervals entry '{entry}', should be 'stname:interval', where "
                        f"'stname' is the statistics name and 'interval' is a floating point "
                        f"interval for collecting the 'stname' statistics.")
        stname, interval = split
        STCAgent._check_stname(stname)

        if not Trivial.is_float(interval):
            raise Error(f"bad interval value '{interval}' for the '{stname}' statistics: should "
                        f"be a positive floating point or integer number")

        stconf["intervals"][stname] = float(interval)

def apply_stconf(stcagent, stconf):
    """
    Apply statistics configuration in 'stconf' dictionary that was created by 'parse_stnames()' to
    the 'STCAgent' instance 'stcagent'.

    In other words, the assumed usage scenario is as follows.
    1. A tool gets list of statistics to collect from the user, feeds the list to 'parse_stname()',
       which parses the list and returns 'stconf'.
    2. The tool may also get custom intervals from the user, feed them to 'parse_intervals()', which
       will parse them and add to 'stconf'.
    3. Before the tool calls stcagent.configure()', it runs 'apply_stconf()' to apply the parsed
       user input information. This will run statistics discovery too, if necessary.
    """

    stcagent.set_disabled_stats(stconf["exclude"])
    stcagent.set_intervals(stconf["intervals"])

    stcagent.configure(discover=stconf["discover"], must_have=stconf["include"])

    stconf["include"] = stcagent.get_enabled_stats()
