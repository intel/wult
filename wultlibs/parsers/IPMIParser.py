# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2014-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Erik Veijola <erik.veijola@intel.com>
#         Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module implements parsing for the output of the "ipmitool" utility. The input file may contain
multiple snapshots of measurement data which we call "data sets". The data sets are always separated
with the "timestamp | XYZ" lines.
"""

import re
import datetime
from pepclibs.helperlibs import Trivial
from wultlibs.parsers import _ParserBase

class IPMIParser(_ParserBase.ParserBase):
    """This class represents the IPMI parser."""

    def _next_entry(self):
        """Generator which yields entries from IPMI log files."""

        time_regex = re.compile(r"^(timestamp) \| (\d+_\d+_\d+_\d+:\d+:\d+)$")
        entry_regex = re.compile(r"^(.+)\|(.+)\|(.+)$")

        for line in self._lines:
            # Example of the string:
            # timestamp | 2017_01_04_11:02:46
            match = re.match(time_regex, line.strip())
            if match:
                timestamp = datetime.datetime.strptime(match.group(2).strip(), '%Y_%m_%d_%H:%M:%S')
                yield (match.group(1).strip(), timestamp, "")
            else:
                # Example of the string:
                # System Fan 4     | 2491 RPM          | ok
                match = re.match(entry_regex, line.strip())
                if match:
                    val = match.group(2).strip()
                    data = val.split(' ', 1)
                    if val not in ["no reading", "disabled"] and len(data) > 1:
                        yield (match.group(1).strip(), Trivial.str_to_num(data[0]), data[1])
                    else:
                        yield (match.group(1).strip(), None, None)

    def _next(self):
        """
        Generator which yields a dictionary corresponging to one snapshot of ipmitool output at a
        time.
        """

        data_set = {}
        duplicates = {}

        for entry in self._next_entry():
            key = entry[0]
            if key != "timestamp":
                # IPMI records are not necessarily unique.
                if key in duplicates:
                    duplicates[key] += 1
                    key = f"{key}_{duplicates[key]}"
                duplicates[key] = 0
                data_set[key] = entry[1:]
            else:
                if data_set:
                    data_set[key] = entry[1:]
                    yield data_set

                data_set = {}
                duplicates = {}
                data_set[key] = entry[1:]
