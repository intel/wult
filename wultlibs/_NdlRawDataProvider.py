# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module implements the "NdlRawDataProvider" class, which provides API for reading raw ndl
data.
"""

import logging
from wultlibs import _RawDataProvider, Devices

_LOG = logging.getLogger()

class NdlRawDataProvider(_RawDataProvider.DrvRawDataProviderBase):
    """
    The raw data provider class implementation the ndl tool.
    """

    def prepare(self):
        """Prepare to start the measurements."""

        # Unload the ndl driver if it is loaded.
        self._unload(everything=True)
        # Load the ndl driver.
        self._load()

    def __init__(self, dev, pman, timeout=None, ldist=None):
        """
        Initialize a class instance. The arguments are as follows.
          * dev - the device object created with 'Devices.GetDevice()'.
          * pman - the process manager object defining host to operate on.
          * timeout - the maximum amount of seconds to wait for a raw datapoint. Default is 10
                      seconds.
          * ldist - a pair of numbers specifying the launch distance range.
        """

        drvinfo = {dev.drvname : {"params" : f"ifname={dev.netif.ifname}"}}
        all_drvnames = Devices.DRVNAMES

        super().__init__(dev, pman, drvinfo, all_drvnames)

        self._timeout = timeout
        self._ldist = ldist

        if not timeout:
            self._timeout = 10
