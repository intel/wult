# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""Provide the wult metrics definition class."""

from pepclibs.helperlibs.Exceptions import Error
from wultlibs import _WultMDCBase

def is_cscyc_metric(metric):
    """Returns 'True' if 'metric' is a C-state cycles count metric."""

    return len(metric) > 5 and (metric[0:2] in {"CC", "MC", "PC"}) and metric.endswith("Cyc")

def is_csres_metric(metric):
    """Returns 'True' if 'metric' is a C-state residency metric."""

    return len(metric) > 3 and (metric[0:2] in {"CC", "MC", "PC"}) and metric.endswith("%")

def is_cs_metric(metric):
    """Returns 'True' if 'metric' is a C-state residency or cycles counter metric."""

    return is_csres_metric(metric) or is_cscyc_metric(metric)

def get_csname(metric, must_get=True):
    """
    If 'metric' is a metric related to a C-state, then returns the C-state name string. Otherwise
    raises an exception, unless the 'must_get' argument is 'False', in which case it returns 'None'
    instead of raising an exception.
    """

    csname = None
    if metric.endswith("Cyc"):
        csname = metric[:-3]
        if csname.endswith("Derived"):
            csname = csname[:-len("Derived")]
    elif metric.endswith("%"):
        csname = metric[:-1]

    if not csname or not (metric[0:2] in {"CC", "MC", "PC"}):
        if must_get:
            raise Error(f"cannot get C-state name for metric '{metric}'")
        return None

    return csname

def get_cscyc_metric(csname):
    """
    Given 'csname' is a C-state name, this method returns the corresponding C-state cycles count
    metric.
    """

    return f"{csname}Cyc"

def get_csres_metric(csname):
    """
    Given 'csname' is a C-state name, this method returns the corresponding C-state residency
    metric.
    """

    return f"{csname}%"

class WultMDC(_WultMDCBase.WultMDCBase):
    """
    The wult metrics definition class provides API to wult metrics definitions, which describe the
    metrics provided by the wult tool.
    """

    def mangle(self, hdr=None): # pylint: disable=arguments-renamed
        """
        Mangle the definitions dictionary and replace C-state residency patterns. The arguments are
        as follows.
          * hdr - a collection of wult datapoints CSV file header fields.
        """

        metrics = list(hdr)

        # Add the C-state residency metric names.
        for field in hdr:
            csname = get_csname(field, must_get=False)
            if not csname:
                continue
            metrics.append(get_csres_metric(csname))

        super().mangle(metrics=metrics)

    def __init__(self, hdr):
        """
        The class constructor. The arguments are as follows.
          * hdr - a collection of wult datapoints CSV file header fields.
        """

        super().__init__("wult")
        self.mangle(hdr=hdr)
