# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides the base class for metrics definitions (AKA 'defs').
"""

import re
from pathlib import Path
from pepclibs.helperlibs import YAML, ProjectFiles

def get_fsname(metric):
    """Given a metric, returns a file-system and URL safe name."""

    # If 'metric' contains "%", we maintain the meaning by replacing with "Percent".
    metric = metric.replace("%", "Percent")

    # Filter out any remaining non-alphanumeric characters.
    metric = ''.join([c for c in metric if c.isalnum()])
    return metric

class DefsBase:
    """The base class for metrics definitions (AKA 'defs')."""

    def _mangle_placeholders(self, placeholders_info):
        """
        Mangle the definitions by substituting placeholders with real values. The arguments are as
        follows.
          * placeholders_info - a list or tuple of dictionaries describing how to mangle the
                                definitions by substituting placeholders with real values.

        The 'placeholders_info' list has the following format.
          [
           { "placeholder"   : placeholder,
             "values"        : list_of_values,
             "casesensitive" : boolean_value},
           ... etc ...
          ]

        Every dictionary in the list provides the following components to the mangler:
          placeholder - the placeholder string that has to be substituted with elements from the
                        'values' list.
          values - list of values to substitute the placeholder with.
          casesensitive - whether to use case-sensitive or case-insensitive matching and
                          substitution. 'True' by default.

        Example.

        The definitions YAML file includes the 'CCx%' metric:

           CCx%
              title: "CCx residence"
              description: "Time in percent spent in Cx core C-state. Matches turbostat CPU%cx."
              unit: "%"

        This metric describes core C-states. Core C-states are platform-dependent, so the real names
        are not known in advance. Therefore, the definitions YAML file uses the 'CCx' placeholder
        instead.

        Suppose the platform has CC1 and CC6 C-states. The 'placeholders_info' list could be the
        following in this case:
          [ { "placeholder" : "Cx",
              "values" : [ "C1", "C6" ],
              "casesensitive" : False, } ]

        The mangler would replace the 'CCx%' placeholder metric definition with the following.

           CC1%
              title: "CC1 residence"
              description: "Time in percent spent in C1 core C-state. Matches turbostat CPU%c1."
              unit: "%"
           CC6%
              title: "CC6 residence"
              description: "Time in percent spent in C6 core C-state. Matches turbostat CPU%c6."
              unit: "%"
        """

        # The sub-keys to look and substitute the placeholders in.
        mangle_subkeys = { "title", "descr", "fsname", "name" }

        for pinfo in placeholders_info:
            values = pinfo["values"]
            phld = pinfo["placeholder"]

            # Whether matching and replacement should be case-sensitive or not.
            # 1. Case-sensitive.
            #   * Match metrics that include the placeholder in the name.
            #   * Replace all placeholders with values in 'values'.
            # 2. Case-insensitive.
            #   * Match metrics that include the placeholder in the name, but accept both lower
            #     and upper cases.
            #   * Replace all placeholders with values in 'values'. But when replacing, if the
            #     original value was in upper case, use upper case, otherwise use lower case
            #     (preserve the case when replacing).
            case_sensitive = pinfo.get("casesensitive", True)

            if case_sensitive:
                regex = re.compile(phld)
            else:
                regex = re.compile(phld, re.IGNORECASE)

            for placeholder_metric in list(self.info):
                if not regex.search(placeholder_metric):
                    continue

                # We found the placeholder metric (e.g., 'CCx%'). Build the 'replacement' dictionary
                # which will replace the 'CCx' sub-dictionary with metric names (e.g., 'CC1' and
                # 'CC6').
                replacement = {}
                for value in values:
                    # pylint: disable=cell-var-from-loop
                    if case_sensitive:
                        func = lambda mo: value
                    else:
                        # The replacement function. Will replace with upper-cased or lower-cased
                        # 'value' depending on whether the replaced sub-string starts with a capital
                        # letter.
                        func = lambda mo: value.upper() if mo.group(0).istitle() else value.lower()

                    metric = regex.sub(func, placeholder_metric)
                    replacement[metric] = self.info[placeholder_metric].copy()

                    for subkey, text in replacement[metric].items():
                        if subkey in mangle_subkeys:
                            replacement[metric][subkey] = regex.sub(func, text)

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
            val["name"] = key
            val["fsname"] = get_fsname(key)

    def __init__(self, name, defsdir=None):
        """
        The class constructor. The arguments are as follows.
          * name - name of the tool to load the definitions for (e.g., 'wult').
          * defsdir - path of directory containing definition files, defaults to "defs".
        """

        if defsdir is None:
            defsdir = "defs"

        self.name = name

        self._populate_cstate_keys = ["title", "descr", "name", "fsname"]

        self.path = ProjectFiles.find_project_data("wult", Path(defsdir) / f"{name}.yml",
                                                   what=f"{name} definitions file")
        self.info = YAML.load(self.path)
        self._mangle_basic()
