# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides an abstraction for a device that can be used as a source of delayed events
(e.g., the I210 network card). This module basically provides 2 methods - 'WultDevice()' and
'scan_devices()'. The former is a factory method that figures out what wult device object to return
(wult device class API is defined by '_WultDeviceBase'. The latter scans the target host for
compatible wult devices.
"""

import contextlib
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from wultlibs import _NetIface
from wultlibs.sysconfiglibs import LsPCI
from wultlibs.helperlibs import FSHelpers, Dmesg
from wultlibs.helperlibs.Exceptions import Error, ErrorNotFound, ErrorNotSupported

# All the possible wult device driver names.
DRVNAMES = set()

# All supported devicetypes.
DEVTYPES = ("i210", "tdt")

_LOG = logging.getLogger()

class _WultDeviceBase(ABC):
    """
    This is the base class for wult delayed event devices. It has 2 purposes.
       * Implement common functionality.
       * Define the API that subclasses (particular device types) have to implement.
    """

    # Name of wult driver that handles this device.
    drvname = None

    @abstractmethod
    def bind(self, drvname):
        """Bind the device to the 'drvname' driver."""

    @abstractmethod
    def unbind(self):
        """
        Unbind the device from its driver if it is bound to any driver. Returns name of the
        driver the was unbinded from (or 'None' if it was not).
        """
        return None

    def _dmesg_capture(self):
        """Capture all dmesg message."""

        if self.dmesg:
            self._captured_dmesg = Dmesg.capture(self._proc)

    def _get_new_dmesg(self):
        """Return new dmesg messages if available."""

        if not self.dmesg:
            return ""

        new_msgs = Dmesg.get_new_messages(self._captured_dmesg, self._proc, join=True, strip=True)
        if new_msgs:
            return f"New kernel messages{self._proc.hostmsg}:\n{new_msgs}"
        return ""

    def __init__(self, devid, cpunum, proc):
        """
        The class constructor. The arguments are as follows.
          * devid - device ID. What the "ID" is depends on the device type.
          * proc - the host to operate on. This object will keep a 'proc' reference and use it in
                   various methods.
          * cpunum - the measured CPU number.
        """

        if not devid:
            raise Error("device ID was not provided")

        self._devid = devid
        self._cpunum = cpunum
        self._proc = proc
        self._captured_dmesg = None

        # Whether kernel messages should be monitored. They are very useful if something goes wrong.
        self.dmesg = True

        # Device information dictionary. Every subclass is expected to provide the following keys.
        # * name - device name (string). Should be short (1-2 words), preferably human-readable.
        #          Should not be capitalized, unless it is necessary (e.g., in case of an acronym).
        # * devid - canonical device ID (string). Does not have to be the same as the 'devid'
        #           argument. Instead, it should be the best type of ID the device can be found on
        #           the system. E.g., in case of PCI devices it would be the PCI address.
        # * descr - device description. May contain multiple sentences. Every sentence should start
        #           with a capital letter and end with a dot.
        #
        # Each subclass is free to add more information to this dictionary.
        self.info = {"name" : None, "devid" : None, "descr" : None}

    def close(self):
        """Uninitialize the device."""
        if getattr(self, "_proc", None):
            self._proc = None

    def __enter__(self):
        """Enter the run-time context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()

    def __init_subclass__(cls, **_):
        """Populate the device driver names collection ('DRVNAMES')."""
        if cls.drvname:
            DRVNAMES.add(cls.drvname)


class _PCIDevice(_WultDeviceBase):
    """This class represents a PCI device that can be used for as a source of delayed events."""

    # Subclasses can define this dictionary to limit list of supported PCI devices.
    supported_devices = {}

    def _get_driver(self):
        """
        Find out whether the PCI device is bound to any driver. If it is not, returns the
        '(None, None)' tuple. Otherwise returns a tuple of:
         * driver name
         * driver sysfs path
        """

        drvpath = Path(f"{self._devpath}/driver")
        if not FSHelpers.exists(drvpath, proc=self._proc):
            return (None, None)

        drvpath = FSHelpers.abspath(drvpath, proc=self._proc)
        drvname = Path(drvpath).name
        return (drvname, drvpath)

    def get_driver_name(self):
        """
        Returns name of the driver the PCI device is bound to, or 'None' in case it is not bound to
        any driver.
        """

        return self._get_driver()[0]

    def bind(self, drvname):
        """Bind the PCI device to driver 'drvname'."""

        _LOG.debug("binding device '%s' to driver '%s'%s",
                   self._pci_info["pciaddr"], drvname, self._proc.hostmsg)

        failmsg = f"failed to bind device '{self._pci_info['pciaddr']}' to driver '{drvname}'" \
                  f"{self._proc.hostmsg}"

        self._dmesg_capture()

        drvpath = Path(f"/sys/bus/pci/drivers/{drvname}")
        if not FSHelpers.exists(drvpath, proc=self._proc):
            raise Error(f"{failmsg}':\npath '{drvpath}' does not exist{self._proc.hostmsg}")

        cur_drvname = self.get_driver_name()
        if cur_drvname == drvname:
            _LOG.debug("device '%s' is already bound to driver '%s'%s",
                       self._pci_info["pciaddr"], drvname, self._proc.hostmsg)
            return

        if cur_drvname:
            raise Error(f"{failmsg}:\nit is already bound to driver '{cur_drvname}'")

        # At this point we do not know if the driver supports this PCI ID. So start with the
        # assumption that it does not, in which case writing to the 'new_id' file should do both:
        # * make the driver aware of the PCI ID
        # * bind the device
        path = f"{drvpath}/new_id"
        val = f"{self._pci_info['vendorid']} {self._pci_info['devid']}"
        bound = True

        try:
            with self._proc.open(path, "wt") as fobj:
                _LOG.debug("writing '%s' to file '%s'", val, path)
                fobj.write(val)
        except Error as err:
            bound = False

        if not bound:
            # Probably the driver already knows about this PCI ID. Use the 'bind' file in this case.
            path = f"{drvpath}/bind"
            val = self._pci_info["pciaddr"]
            with self._proc.open(path, "wt") as fobj:
                _LOG.debug("writing '%s' to file '%s'", val, path)
                try:
                    fobj.write(val)
                except Error as err:
                    raise Error(f"{failmsg}:\n{err}\n{self._get_new_dmesg()}") from err

        # Verify that the device is bound to the driver.
        if not self._get_driver()[1]:
            raise Error(f"{failmsg}\n{self._get_new_dmesg()}")

        _LOG.debug("binded device '%s' to driver '%s'%s\n%s", self._pci_info["pciaddr"], drvname,
                   self._proc.hostmsg, self._get_new_dmesg())

    def unbind(self):
        """
        Unbind the PCI device from its driver if it is bound to any driver. Returns name of the
        driver the was unbinded from (or 'None' if it was not).
        """

        drvname, drvpath = self._get_driver()

        if not drvname:
            _LOG.debug("device '%s' is not bound to any driver%s",
                       self._pci_info["pciaddr"], self._proc.hostmsg)
            return drvname

        _LOG.debug("unbinding device '%s' from driver '%s'%s",
                   self._pci_info["pciaddr"], drvname, self._proc.hostmsg)

        self._dmesg_capture()

        failmsg = f"failed to unbind PCI device '{self._pci_info['pciaddr']}' from driver " \
                  f"'{drvname}'{self._proc.hostmsg}"

        with self._proc.open(drvpath / "unbind", "wt") as fobj:
            _LOG.debug("writing '%s' to '%s'", self._pci_info["pciaddr"], drvpath / "unbind")
            try:
                fobj.write(self._pci_info["pciaddr"])
            except Error as err:
                raise Error(f"{failmsg}:\n{err}\n{self._get_new_dmesg()}") from err

        if self._get_driver()[1]:
            raise Error(f"{failmsg}:\npath '{drvpath}' still exists\n{self._get_new_dmesg()}")

        _LOG.debug("unbinded device '%s' from driver '%s'%s\n%s", self._pci_info["pciaddr"],
                   drvname, self._proc.hostmsg, self._get_new_dmesg())

        return drvname

    def __init__(self, devid, cpunum, proc):
        """The class constructor. The arguments are the same as in '_WultDeviceBase.__init__()'."""

        super().__init__(devid, cpunum, proc)

        self._pci_info = None
        self._devpath = None
        self._captured = None

        path = Path(f"/sys/bus/pci/devices/{self._devid}")
        if not FSHelpers.exists(path, proc=proc):
            raise ErrorNotFound(f"cannot find device '{self._devid}'{self._proc.hostmsg}:\n"
                                f"path {path} does not exist")

        self._devpath = FSHelpers.abspath(path, proc=self._proc)
        self._pci_info = LsPCI.LsPCI(proc).get_info(Path(self._devpath).name)

        if self.supported_devices and self._pci_info['devid'] not in self.supported_devices:
            supported = ["%s - %s" % (key, val) for key, val in self.supported_devices.items()]
            supported = "\n * ".join(supported)
            raise ErrorNotSupported(f"PCI device '{self._pci_info['pciaddr']}' (PCI ID "
                                    f"{self._pci_info['devid']}) is not supported by wult driver "
                                    f"{self.drvname}.\nHere is the list of supported PCI IDs:\n* "
                                    f"{supported}")

        self.info["name"] = "Intel I210"
        self.info["devid"] = self._pci_info["pciaddr"]
        if self.supported_devices:
            self.info["descr"] = self.supported_devices[self._pci_info['devid']]
        else:
            self.info["name"] = self._pci_info["name"]
            self.info["descr"] = self.info['name'].capitalize()

        self.info["descr"] += f". PCI address {self._pci_info['pciaddr']}, Vendor ID " \
                              f"{self._pci_info['vendorid']}, Device ID {self._pci_info['devid']}."
        self.info["aspm_enabled"] = self._pci_info["aspm_enabled"]

class _IntelI210(_PCIDevice):
    """
    This class extends the '_PCIDevice' class with 'Intel I210' NIC support.
    """

    drvname = "wult_igb"
    supported_devices = {
        '1533' : 'Intel I210 (copper)',
        '1536' : 'Intel I210 (fiber)',
        '1537' : 'Intel I210 (serdes)',
        '1538' : 'Intel I210 (sgmii)',
        '157b' : 'Intel I210 (copper flashless)',
        '157c' : 'Intel I210 (serdes flashless)',
        '1539' : 'Intel I211 (copper)'}

    def __init__(self, devid, cpunum, proc, force=False):
        """
        The class constructor. The 'force' argument can be used to initialize I210 device for
        measurements even if its network interface state is "up". Other arguments are the same as in
        '_WultDeviceBase.__init__()'. The 'devid' can be be the PCI address or the network interface
        name.
        """

        with _NetIface.NetIface(devid, proc=proc) as netif:
            # Make sure the device is not used for networking, because we are about to unbind it
            # from the driver. This check makes sure users do not lose networking by specifying
            # wrong device by a mistake.
            if not force and netif.getstate() == "up":
                msg = ""
                if devid != netif.ifname:
                    msg = f" (network interface '{netif.ifname}')"

                raise Error(f"refusing to use device '{devid}'{msg}{proc.hostmsg}: "
                            f"it is up and might be used for networking. Please, bring it down "
                            f"if you want to use it for wult measurements.")

            super().__init__(netif.hwaddr, cpunum, proc)

class _TimerBase(_WultDeviceBase):
    """
    Base class for timer devices, such as TSC deadline timer. The are all very similar except for
    names and descriptions.
    """

    drvname = "wult_timer"
    supported_devices = {}
    # Name of the clock source device corresponding to the timer.
    _clkname = None

    def __init__(self, devid, cpunum, proc):
        """The class constructor. The arguments are the same as in '_WultDeviceBase.__init__()'."""

        errmsg = f"device '{devid}' is not supported for CPU {cpunum}{proc.hostmsg}."
        if devid not in self.supported_devices:
            raise ErrorNotSupported(f"{errmsg}")

        path = Path(f"/sys/devices/system/clockevents/clockevent{cpunum}/current_device")
        with proc.open(path, "r") as fobj:
            clkname = fobj.read().strip()
            if clkname != self._clkname:
                raise ErrorNotSupported(f"{errmsg}\nCurrent clockevent device is {clkname}, should "
                                        f"be {self._clkname} (see {path})")

        super().__init__(devid, cpunum, proc)

        self.info["name"] = self.supported_devices[devid]
        self.info["devid"] = devid
        self.info["descr"] = f"{self.info['name']} on CPU{cpunum}"

    def bind(self, drvname):
        """No bind for this device."""

    def unbind(self):
        """No unbind for this device."""
        return None

class _TSCDeadlineTimer(_TimerBase):
    """
    This class represents a TSC deadline timer device that can be used as a source of delayed
    events.
    """

    supported_devices = {'tdt' : 'TSC deadline timer'}
    _clkname = "lapic-deadline"

def WultDevice(devid, cpunum, proc, force=False):
    """
    The wult device object factory - creates and returns the correct type of wult device object
    depending on 'devid'. The arguments are the same as in '_WultDeviceBase.__init__()'.
    """

    # The "timer" device ID is an alias for "any timer type".
    # Note: we used to support LAPIC timers and the "timer" name meant "any timer" at that point.
    # But we removed LAPIC timers support later.
    if devid == "timer":
        failed = []
        for cls in [_TSCDeadlineTimer]:
            name = next(iter(cls.supported_devices))
            try:
                return cls(name, cpunum, proc)
            except ErrorNotSupported as err:
                _LOG.debug("'%s' probe error:\n%s", name, err)
                failed.append(name)

        failed = ", ".join(failed)
        raise ErrorNotSupported(f"none of the following are supported{proc.hostmsg}:\n{failed}")

    if devid in _TSCDeadlineTimer.supported_devices:
        return _TSCDeadlineTimer(devid, cpunum, proc)

    try:
        return _IntelI210(devid, cpunum, proc, force=force)
    except ErrorNotSupported as err:
        raise ErrorNotSupported(f"unsupported device '{devid}'{proc.hostmsg}") from err

def scan_devices(proc, devtypes=None):
    """
    Scan the host defined by 'proc' for compatible devices. The 'devtypes' argument can be
    used to limit the scan to only certain type of devices. Supported device types are 'i210' for
    Intel i210 NIC and 'tdt' for TSC deadline timer. Scanning all devices by default.

    Yields tuples of the following elements:
     * devid - device ID of the found compatible device
     * alias - device ID aliase for the device ('None' if there are no aliases). Alias is just
               another device ID for the same device.
     * descr - short device description
    """

    if devtypes is None:
        devtypes = DEVTYPES

    if "tdt" in devtypes:
        for devid in _TSCDeadlineTimer.supported_devices:
            with contextlib.suppress(Error):
                with _TSCDeadlineTimer(devid, 0, proc) as timerdev:
                    yield timerdev.info["devid"], "timer", timerdev.info["descr"]

    if "i210" in devtypes:
        for pci_info in LsPCI.LsPCI(proc).get_devices():
            pci_id = pci_info["devid"]
            if not _IntelI210.supported_devices.get(pci_id):
                continue

            devid = pci_info['pciaddr']

            # Find out the Linux network interface name for this NIC, if any.
            ifname = None
            with contextlib.suppress(Error):
                with _NetIface.NetIface(devid, proc=proc) as netif:
                    ifname = netif.ifname

            descr = _IntelI210.supported_devices.get(pci_id)
            descr += f". PCI address {pci_info['pciaddr']}, Vendor ID {pci_info['vendorid']}, " \
                     f"Device ID {devid}."
            yield devid, ifname, descr
