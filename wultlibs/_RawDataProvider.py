# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module implements the base class for raw data provider classes.
"""

import logging
import contextlib
from pepclibs.helperlibs.Exceptions import Error
from pepclibs.helperlibs import ClassHelpers, KernelModule
from wultlibs.helperlibs import FSHelpers

_LOG = logging.getLogger()

class RawDataProviderBase(ClassHelpers.SimpleCloseContext):
    """
    The base class for raw data provider classes.
    """

    def __init__(self, dev, pman):
        """
        Initialize a class instance for device 'dev'. The arguments are as follows.
          * dev - the device object created with 'Devices.GetDevice()'.
          * pman - the process manager object defining host to operate on.
        """

        self.dev = dev
        self._pman = pman

        msg = f"Using device '{self.dev.info['name']}'{pman.hostmsg}:\n" \
              f" * Device ID: {self.dev.info['devid']}\n" \
              f"   - {self.dev.info['descr']}"
        _LOG.info(msg)

    def close(self):
        """Uninitialize everything."""
        ClassHelpers.close(self, unref_attrs=("dev", "_pman"))

class DrvRawDataProviderBase(RawDataProviderBase):
    """
    The base class for raw data providers in case Linux kernel drivers are used. In other words,
    this class is 'RawDataProviderBase' + drivers loading/unloading support.
    """

    def _load(self):
        """Load all the necessary kernel drivers."""

        loaded = []
        for drvobj in self.drvobjs:
            try:
                drvobj.load(opts=self._drvinfo[drvobj.name]["params"])
                loaded.append(drvobj)
            except Error:
                # Unload the loaded drivers.
                for udrvobj in reversed(loaded):
                    try:
                        udrvobj.unload()
                    except Error as err:
                        _LOG.warning("failed to unload module '%s'%s:\n%s", udrvobj.name,
                                     self._pman.hostmsg, err)
                raise

    def _unload(self, everything=False):
        """
        Unload kernel drivers. The arguments are as follows.
          * everything - if 'False', unload only the previously loaded drivers, otherwise unload all
                         possible drivers.
        """

        unloaded = set()

        for drvobj in reversed(self.drvobjs):
            drvobj.unload()
            unloaded.add(drvobj.name)

        if not everything:
            return

        # Unload all the possible device drivers.
        for drvname in self._all_drvnames:
            if drvname in unloaded:
                continue

            with KernelModule.KernelModule(drvname, pman=self._pman,
                                           dmesg=self.dev.dmesg_obj) as drvobj:
                drvobj.unload()

    def __init__(self, dev, pman, drvinfo, all_drvnames):
        """
        Initialize a class instance. The arguments are as follows.
          * drvinfo - a dictionary describing the kernel drivers to load/unload.
          * all_drvnames - list of all possible driver names.
          * All other arguments are the same as in '_RawDataProviderBase.__init__()'.

        The 'drvinfo' dictionary schema is as follows.
          { drvname1: { "params" : <modulue parameters> },
            drvname2: { "params" : <modulue parameters> },
           ... etc ... }

          * drvname - driver name.
          * params - driver module parameters.
        """

        super().__init__(dev, pman)

        self._drvinfo = drvinfo
        self._all_drvnames = all_drvnames
        self.drvobjs = []

        self.debugfs_mntpoint = None
        self._unmount_debugfs = None

        for drvname in self._drvinfo.keys():
            drvobj = KernelModule.KernelModule(drvname, pman=pman, dmesg=dev.dmesg_obj)
            self.drvobjs.append(drvobj)

        self.debugfs_mntpoint, self._unmount_debugfs = FSHelpers.mount_debugfs(pman=pman)

    def close(self):
        """Uninitialize everything."""

        if getattr(self, "drvobjs", None):
            with contextlib.suppress(Error):
                self._unload()

            for drvobj in self.drvobjs:
                with contextlib.suppress(Error):
                    drvobj.close()
            self.drvobjs = []

        if getattr(self, "_unmount_debugfs", None):
            with contextlib.suppress(Error):
                self._pman.run("unmount {self.debugfs_mntpoint}")

        super().close()
