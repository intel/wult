# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API to turbostat metrics definitions (AKA 'defs').
"""

from wultlibs import _DefsBase

class TurbostatDefs(_DefsBase.DefsBase):
    """This module provides API to turbostat metrics definitions (AKA 'defs')."""

    def populate_cstates(self, csnames):
        """
        Definitions YAML files do not contain information about C-states supported by various
        platforms, they only use a generic C-state "Cx".  Depending on the platform, there may be a
        different amount of C-states with different names.

        This method should be invoked to populate the definitions dictionary with the C-state
        information for a specific platform. The 'csnames' argument is the list of C-state names to
        replace the "Cx" metric with.
        """

        pattern = "Cx"

        # Copy all keys one-by-one to preserve the order.
        info = {}
        for metric, minfo in self.info.items():
            if pattern not in metric:
                info[metric] = minfo
                continue

            for csname in csnames:
                new_metric = metric.replace(pattern, csname)

                if new_metric in info:
                    continue

                info[new_metric] = minfo.copy()

                # Correct all info dicts which need populating to refer to real C-state names.
                for key in self._populate_cstate_keys:
                    if key in info[new_metric]:
                        info[new_metric][key] = info[new_metric][key].replace(pattern, csname)

        self.info = info

    def __init__(self, cstates):
        """
        The class constructor. Arguments are as follows:
         * cstates - a list of C-states parsed from raw turbostat statistic files.
        """

        super().__init__("turbostat")

        placeholders_info = [{"values": cstates, "placeholder": "Cx"}]
        self._mangle_placeholders(placeholders_info)
