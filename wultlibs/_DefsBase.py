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
    """

    @staticmethod
    def _mangle(info):
        """This function mangles the initially loaded dictionary and adds useful values there."""

        metric_key = "metric"
        fsname_key = "fsname"

        for key, val in info.items():
            val[metric_key] = key
            val[fsname_key] = get_fsname(key)

        return info

    def __init__(self, name):
        """
        The class constructor. The arguments are as follows.
          * name - name of the tool to load the definitions for (e.g., 'wult').
        """

        self.name = name
        self.info = None
        self.vanilla_info = None

        self.path = Deploy.find_app_data("wult", Path(f"defs/{name}.yml"),
                                         descr=f"{name} definitions file")
        self.info = self.vanilla_info = self._mangle(YAML.load(self.path))

class CSDefsBase(DefsBase):
    """
    This base class can be inherited from to provide an API to the YAML definitions files (AKA
    'defs'). This class extends 'DefsBase' to add the 'populate_cstates' method which can be used
    to populate the defitions dictionary with the C-state information for a specific platform.

    This base class requires child classes to implement the following methods:
    1. Return 'True' if a given 'metric' is a C-state residency metric.
       * 'is_cs_metric()'
    2. Return the C-state name string for the C-state represented in a given metric name 'metric'.
       * 'get_csname()'
    3. Return a new version of a given metric name 'metric' for a C-state 'csname'.
       * 'get_new_metric()'

    Optionally child classes can override the '_mangle()' method which mangles the initially loaded
    dictionary to provide more helpful values.
    """

    def is_csmetric(self, metric):
        """Returns 'True' if 'metric' is a C-state residency metric."""

        raise NotImplementedError()

    def get_csname(self, metric):
        """Returns the name of the C-state represented in 'metric'."""

        raise NotImplementedError()

    def get_csmetric(self, metric, csname):
        """Returns a version of 'metric' populated with the C-state name 'csname'."""

        raise NotImplementedError()

    def populate_cstates(self, hdr):
        """
        The definitions YAML file does not contain information about C-states supported by various
        platforms. It only defines general core and package C-states ('CCx' and 'PCx'). Depending on
        the platform, there may be different amount of C-states with different names.

        This method should should be invoked to populate the definitions dictionary with the C-state
        information for a specific platform. The 'hdr' argument is a list of metrics for which the
        definitions dictionary should be populated.
        """

        if self.info is not self.vanilla_info:
            # Already populated.
            return

        # Filter hdr to only C-state metrics.
        hdr = [hdrname for hdrname in hdr if self.is_csmetric(hdrname)]

        # Copy all keys one-by-one to preserve the order.
        info = {}
        for metric, minfo in self.vanilla_info.items():
            if not self.is_csmetric(metric) or "Cx" not in metric:
                info[metric] = minfo
                continue

            mcsname = self.get_csname(metric)

            for hdrname in hdr:
                csname = self.get_csname(hdrname)
                new_metric = self.get_csmetric(metric, csname)

                info[new_metric] = minfo.copy()

                # Correct all info dicts which need populating to refer to real C-state names.
                for key in self._populate_cstate_keys:
                    if key in info[new_metric]:
                        info[new_metric][key] = info[new_metric][key].replace(mcsname, csname)

        self.info = info

    def __init__(self, name):
        """Class constructor. Arguments are the same as in base class 'DefsBase'."""

        # List of info keys to populate with C-states when 'populate_cstates()' is called.
        self._populate_cstate_keys = ["title", "descr", "metric", "fsname"]

        super().__init__(name)
