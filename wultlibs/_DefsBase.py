# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides the base class for metrics definitoins (AKA 'defs').
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
    """The base class for metrics definitoins (AKA 'defs')."""

    def _mangle_placeholders(self, placeholders_info):
        """
        Mangle the definitions by substituting placeholders with real values. The arguments are as
        follows.
          * placeholders_info - a list or tuple of dictionaries describing how to mangle the
                                definitions by substituting placeholders with real values.

        The 'placeholders_info' list has the following format.
          [
           { "values"     : list_of_values,
             "placeholder" : placeholder },
           ... etc ...
          ]

        Every dictionary in the list provides the following components to the mangler:
          values - list of values to substitute the placeholder with.
          placeholder - the placeholder string that has to be substituted with elements from the
                        'values' list.

        Example.

        The definitions YAML file includes the 'CCx%' metric:

           CCx%
              title: "CCx residence"
              description: "Time in percent the CPU spent in the CCx core C-state"
              unit: "%"

        This metric describes core C-states. Core C-states are platform-dependent, so the real names
        are not known in advance. Therefore, the definitions YAML file uses the 'CCx' placeholder
        instead.

        Suppose the platform has CC1 and CC6 C-states. The 'placeholders_info' list could be the
        following in this case:
          [ { "values" : [ "CC1", "CC6" ],
              "placeholder" : "CCx" } ]

        The mangler would replace the 'CCx%' placeholder metric definition with the following.

           CC1%
              title: "CC1 residence"
              description: "Time in percent the CPU spent in the CC1 core C-state"
              unit: "%"
           CC6%
              title: "CC6 residence"
              description: "Time in percent the CPU spent in the CC6 core C-state"
              unit: "%"
        """

        # The sub-keys to look and substitute the placeholders in.
        mangle_subkeys = { "title", "descr", "fsname", "metric" }

        for pinfo in placeholders_info:
            values = pinfo["values"]
            phld = pinfo["placeholder"]

            for placeholder_metric in list(self.info):
                if phld not in placeholder_metric:
                    continue

                # We found the placeholder metric (e.g., 'CCx%'). Build the 'replacement' dictionary
                # which will replace the 'CCx' sub-dictionary with metric names (e.g., 'CC1' and
                # 'CC6').
                replacement = {}
                for value in values:
                    metric = placeholder_metric.replace(phld, value)
                    replacement[metric] = self.info[placeholder_metric].copy()
                    for subkey, val in replacement[metric].items():
                        if subkey in mangle_subkeys:
                            replacement[metric][subkey] = val.replace(phld, value)

                # Construct new 'self.info' by replacing the placeholder metric with the replacement
                # metrics.
                new_info = {}
                for metric, minfo in self.info.items():
                    if metric != placeholder_metric:
                        new_info[metric] = minfo
                    else:
                        for new_metric, new_minfo in replacement.items():
                            new_info[new_metric] = new_minfo

                self.info = new_info

    def _mangle_basic(self):
        """Mangle the initially loaded 'self.info' dictionary."""

        for key, val in self.info.items():
            val["metric"] = key
            val["fsname"] = get_fsname(key)

    def __init__(self, name):
        """
        The class constructor. The arguments are as follows.
          * name - name of the tool to load the definitions for (e.g., 'wult').
        """

        self.name = name
        self.info = None

        self._populate_cstate_keys = ["title", "descr", "metric", "fsname"]

        self.path = Deploy.find_app_data("wult", Path(f"defs/{name}.yml"),
                                         descr=f"{name} definitions file")
        self.info = YAML.load(self.path)
        self._mangle_basic()
