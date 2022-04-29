# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides the base class for APIs to the definitions (AKA 'defs') files.
"""

from pathlib import Path
from pepclibs.helperlibs import YAML
from wultlibs import Deploy


def get_fsname(metric):
    """Given a metric, returns a file-system and URL safe name."""

    # If 'metric' contains "%", we maintain the meaning by replacing with "Percent".
    metric = metric.replace("%", "Percent")

    # Filter out any remaining non-alphanumeric characters.
    metric = ''.join([c for c in metric if c.isalnum()])
    return metric


class DefsBase:
    """
    This base class can be inherited from to provide an API to the YAML definitions files (AKA
    'defs').

    Optionally child classes can override the '_mangle()' method which mangles the initially loaded
    dictionary to provide more helpful values.
    """

    @staticmethod
    def _mangle(info):
        """This function mangles the initially loaded dictionary and adds useful values there."""

        for key, val in info.items():
            val["metric"] = key
            val["fsname"] = get_fsname(key)

        return info

    def __init__(self, name):
        """
        The class constructor. The arguments are as follows.
          * name - name of the tool to load the definitions for (e.g., 'wult').
        """

        self.name = name
        self.info = None

        self.path = Deploy.find_app_data("wult", Path(f"defs/{name}.yml"),
                                         descr=f"{name} definitions file")
        self.info = self._mangle(YAML.load(self.path))

class CSDefsBase(DefsBase):
    """
    This base class can be inherited from to provide an API to the YAML definitions files (AKA
    'defs'). This class extends 'DefsBase' to add the 'populate_cstates' method which can be used
    to populate the defitions dictionary with the C-state information for a specific platform.
    """

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

    def __init__(self, name):
        """Class constructor. Arguments are the same as in base class 'DefsBase'."""

        # List of info keys to populate with C-states when 'populate_cstates()' is called.
        self._populate_cstate_keys = ["title", "descr", "metric", "fsname"]

        super().__init__(name)
