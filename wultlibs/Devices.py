# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides an abstraction for a device that can be used as the source of raw datapoints
for wult and ndl tools.

This module provides the following methods.
  * GetDevice() - a factory for creating and returning device class objects.
  * scan_devices() - scan for compatible devices.
"""

import time
import contextlib
from pathlib import Path
from pepclibs.helperlibs import Logging, Dmesg, ClassHelpers, Trivial, PCI
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound, ErrorNotSupported
from wultlibs import NetIface

# All the possible wult/ndl device driver names in order suitable for unloading.
ALL_DRVNAMES = ("ndl", "wult_igb", "wult_hrt", "wult_tdt", "pbe")

# The maximum expected device clock resolution in nanoseconds.
_MAX_RESOLUTION = 100

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

class _DeviceBase(ClassHelpers.SimpleCloseContext):
    """This is the base class for device classes."""

    def bind(self, drvname=None):
        """
        Bind the device its driver. The arguments are as follows.
          * drvname - name of the driver to bind to (wult/ndl driver by default).
        """

    def unbind(self):
        """
        Unbind the device from its driver if it is bound to any driver. Returns name of the
        driver the device was unbinded from (or 'None' if it was not).
        """
        return None

    def get_new_dmesg(self):
        """
        Return new dmesg messages as a single string, if available."""

        if not self.dmesg_obj:
            return ""
        new_msgs = self.dmesg_obj.get_new_messages(join=True)
        if new_msgs:
            return f"New kernel messages{self._pman.hostmsg}:\n{new_msgs}"
        return ""

    def __init__(self, devid, pman, drvname=None, helpername=None, dmesg=True):
        """
        The class constructor. The arguments are as follows.
          * devid - device ID. What the "ID" is depends on the device type.
          * pman - the process manager object defining the host to operate on.
          * drvname - name of the kernel driver which will be used for handling this device.
          * helpername - name of the helper tool required for handling this device.
          * dmesg - 'True' to enable 'dmesg' output checks, 'False' to disable them.
        """

        if not devid:
            raise Error("device ID was not provided")

        self._devid = devid
        self._pman = pman
        self.drvname = drvname
        self.helpername = helpername

        # 'True' if this is a PCI device.
        self.is_pci = False
        # 'True' if this is a NIC.
        self.is_nic = False
        # 'True' if this device is based on processors' LAPIC timers.
        self.is_timer = False

        self.dmesg_obj = None

        if dmesg:
            self.dmesg_obj = Dmesg.Dmesg(pman=self._pman)
            self.dmesg_obj.run(capture=True)

        # Device information dictionary. Every subclass is expected to provide the following keys.
        # * devid - canonical device ID (string). Does not have to be the same as the 'devid'
        #           argument. Instead, it should be the best type of ID the device can be found on
        #           the system. E.g., in case of PCI devices it would be the PCI address.
        # * descr - device description. May contain multiple sentences. Every sentence should start
        #           with a capital letter and end with a dot.
        #
        # Each subclass is free to add more information to this dictionary.
        self.info = {"devid": None, "descr": None, "resolution": None}

    def close(self):
        """Uninitialize the device."""
        ClassHelpers.close(self, close_attrs=("dmesg_obj",), unref_attrs=("_pman",))

class _PCIDevice(_DeviceBase):
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
        if not self._pman.exists(drvpath):
            return (None, None)

        drvpath = self._pman.abspath(drvpath)
        drvname = Path(drvpath).name
        return (drvname, drvpath)

    def bind(self, drvname=None):
        """Bind the PCI device to driver 'drvname' (wult/ndl driver by default)."""

        if not drvname:
            drvname = self.drvname

        _LOG.info("Binding device '%s' to driver '%s'", self.info["devid"], drvname)

        failmsg = f"failed to bind device '{self._pci_info['addr']}' to driver '{drvname}'" \
                  f"{self._pman.hostmsg}"

        drvpath = Path(f"/sys/bus/pci/drivers/{drvname}")
        if not self._pman.exists(drvpath):
            raise Error(f"{failmsg}':\npath '{drvpath}' does not exist{self._pman.hostmsg}")

        cur_drvname = self._get_driver()[0]
        if cur_drvname == drvname:
            _LOG.debug("device '%s' is already bound to driver '%s'%s",
                       self._pci_info["addr"], drvname, self._pman.hostmsg)
            return

        if cur_drvname:
            raise Error(f"{failmsg}:\nit is already bound to driver '{cur_drvname}'")

        # At this point we do not know if the driver supports this PCI ID. So start with the
        # assumption that it does not, in which case writing to the 'new_id' file should do both of
        # the following.
        # * make the driver aware of the PCI ID.
        # * bind the device.
        path = f"{drvpath}/new_id"
        val = f"{self._pci_info['vendorid']:x} {self._pci_info['devid']:x}"
        bound = True

        try:
            with self._pman.open(path, "wt") as fobj:
                _LOG.debug("writing '%s' to file '%s'", val, path)
                fobj.write(val)
        except Error:
            bound = False

        if not bound:
            # Probably the driver already knows about this PCI ID. Use the 'bind' file in this case.
            path = f"{drvpath}/bind"
            val = self._pci_info["addr"]
            with self._pman.open(path, "wt") as fobj:
                _LOG.debug("writing '%s' to file '%s'", val, path)
                try:
                    fobj.write(val)
                except Error as err:
                    raise Error(f"{failmsg}:\n{err.indent(2)}\n{self.get_new_dmesg()}") from err

        # Verify that the device is bound to the driver.
        if not self._get_driver()[1]:
            raise Error(f"{failmsg}\n{self.get_new_dmesg()}")

        _LOG.debug("binded device '%s' to driver '%s'%s\n%s", self._pci_info["addr"], drvname,
                   self._pman.hostmsg, self.get_new_dmesg())

    def unbind(self):
        """
        Unbind the PCI device from its driver if it is bound to any driver. Returns name of the
        driver the device was unbinded from (or 'None' if it was not).
        """

        drvname, drvpath = self._get_driver()

        if not drvname:
            _LOG.debug("device '%s' is not bound to any driver%s",
                       self._pci_info["addr"], self._pman.hostmsg)
            return drvname

        _LOG.debug("unbinding device '%s' from driver '%s'%s",
                   self._pci_info["addr"], drvname, self._pman.hostmsg)

        failmsg = f"failed to unbind PCI device '{self._pci_info['addr']}' from driver " \
                  f"'{drvname}'{self._pman.hostmsg}"

        with self._pman.open(drvpath / "unbind", "wt") as fobj:
            _LOG.debug("writing '%s' to '%s'", self._pci_info["addr"], drvpath / "unbind")
            try:
                fobj.write(self._pci_info["addr"])
            except Error as err:
                raise Error(f"{failmsg}:\n{err.indent(2)}\n{self.get_new_dmesg()}") from err

        if self._get_driver()[1]:
            raise Error(f"{failmsg}:\npath '{drvpath}' still exists\n{self.get_new_dmesg()}")

        _LOG.info("Unbinded device '%s' from driver '%s'%s", self.info["devid"], drvname,
                  self._pman.hostmsg)
        _LOG.debug(self.get_new_dmesg())

        if not self._orig_drvname:
            self._orig_drvname = drvname

        return drvname

    def __init__(self, devid, pman, drvname=None, helpername=None, dmesg=None):
        """
        The class constructor. The arguments are as follows.
          * devid - PCI address of the device.
          * pman - the process manager object defining the host to operate on.
          * drvname - name of the kernel driver which will be used for handling this device.
          * helpername - name of the helper tool required for handling this device.
          * dmesg - 'True' to enable 'dmesg' output checks, 'False' to disable them.
        """

        super().__init__(devid, pman, drvname=drvname, helpername=helpername, dmesg=dmesg)

        self._pci_info = None
        self._devpath = None
        # Name of the driver the device was bound too before 'bind()' was called.
        self._orig_drvname = None

        path = Path(f"/sys/bus/pci/devices/{self._devid}")
        if not pman.exists(path):
            raise ErrorNotSupported(f"cannot find device '{self._devid}'{self._pman.hostmsg}:\n"
                                    f"path {path} does not exist")

        self._devpath = self._pman.abspath(path)
        self._pci_info = PCI.get_basic_info(self._devid, pman=pman)

        if self.supported_devices and self._pci_info["devid"] not in self.supported_devices:
            supported = [f"{key} - {val}" for key, val in self.supported_devices.items()]
            supported = "\n * ".join(supported)
            if drvname:
                drvtext = f" by driver {self.drvname}"
            raise ErrorNotSupported(f"PCI device '{self._pci_info['addr']}' (PCI ID "
                                    f"{self._pci_info['devid']}) is not supported{drvtext}.\n"
                                    f"Here is the list of supported PCI IDs:\n* {supported}")

        self.is_pci = True

        self.info["devid"] = self._pci_info["addr"]
        if self.supported_devices:
            self.info["descr"] = self.supported_devices[self._pci_info["devid"]]
        else:
            self.info["descr"] = "Unknown device"

        self.info["descr"] += f". PCI address {self._pci_info['addr']}, Vendor ID " \
                              f"{self._pci_info['vendorid']:#x}, " \
                              f"Device ID {self._pci_info['devid']:#x}."

    def close(self):
        """Uninitialize the device."""

        if getattr(self, "_orig_drvname", None):
            with contextlib.suppress(Error):
                self.unbind()
                self.bind(drvname=self._orig_drvname)

        super().close()

class _IntelI210Base(_PCIDevice):
    """
    Base class for Intel I210 NIC devices.
    """

    supported_devices = {
        0x1533: "Intel I210 (copper)",
        0x1536: "Intel I210 (fiber)",
        0x1537: "Intel I210 (serdes)",
        0x1538: "Intel I210 (sgmii)",
        0x157b: "Intel I210 (copper flashless)",
        0x157c: "Intel I210 (serdes flashless)",
        0x1539: "Intel I211 (copper)"}

    def bind(self, drvname=None):
        """Bind the PCI device to driver 'drvname' (wult/ndl driver by default)."""

        super().bind(drvname=drvname)

        if drvname == self._orig_drvname and self._orig_operstate:
            operstate = "up" if self._orig_operstate == "up" else "down"
            _LOG.debug("operational state of network interface '%s' was '%s', setting it to '%s'",
                       self.netif.ifname, self._orig_operstate, operstate)

            try:
                getattr(self.netif, operstate)()
            except Error as err:
                _LOG.warning("cannot restore interface '%s' state:\n%s",
                             self.netif.ifname, err.indent(2))

    def unbind(self):
        """
        Unbind the PCI device from its driver if it is bound to any driver. Returns name of the
        driver the device was unbinded from (or 'None' if it was not).
        """

        # Save the original operational state in order to restore it in 'bind()'. The reason is that
        # 'bind()' may put it to "up", even if it was "down".
        if not self._orig_drvname and self.netif:
            # Save it only when unbinding for the first time.
            self._orig_operstate = self.netif.get_operstate()

        super().unbind()

    def __init__(self, devid, pman, drvname=None, helpername=None, no_netif_ok=True, dmesg=None):
        """
        The class constructor. The arguments are as follows.
          * devid - device ID (network interface name or PCI address).
          * pman - the process manager object defining the host to operate on.
          * drvname - name of the kernel driver which will be used for handling this device.
          * helpername - name of the helper tool required for handling this device.
          * no_netif_ok - if 'True', the network interface does not have to exist for the NIC,
                          otherwise raises an exception if the network interface does not exist.
          * dmesg - 'True' to enable 'dmesg' output checks, 'False' to disable them.

        Note, 'devid' can be be the PCI address or the network interface name.
        """

        netif = None
        try:
            netif = NetIface.NetIface(devid, pman=pman)
        except ErrorNotFound as err:
            if not no_netif_ok:
                raise
            _LOG.debug(err)

        if netif:
            hwaddr = netif.hwaddr
            alias = netif.ifname
        else:
            hwaddr = devid
            alias = None

        super().__init__(hwaddr, pman, drvname=drvname, helpername=helpername, dmesg=dmesg)

        self.is_nic = True

        self.netif = netif
        self.info["alias"] = alias
        # I210 NIC clock has 1 nanosecond resolution.
        self.info["resolution"] = 1

        self._orig_operstate = None

    def close(self):
        """Uninitialize the device."""

        super().close()

        ClassHelpers.close(self, close_attrs=("netif",))

class _WultIntelI210(_IntelI210Base):
    """
    The Intel I210 NIC device for wult.
    """

    def __init__(self, devid, pman, dmesg=None):
        """The arguments are the same as in '_WultIntelI210.__init__()'."""

        super().__init__(devid, pman, drvname="wult_igb", dmesg=dmesg)

class _NdlIntelI210(_IntelI210Base):
    """
    The Intel I210 NIC device for ndl.
    """

    def __init__(self, devid, pman, dmesg=None):
        """The arguments are the same as in '_WultIntelI210.__init__()'."""

        super().__init__(devid, pman, drvname="ndl", helpername="ndl-helper", no_netif_ok=False,
                         dmesg=dmesg)

class _WultTSCDeadlineTimer(_DeviceBase):
    """
    This class represents the TSC deadline timer (TDT). TDT is a LAPIC feature supported by modern
    Intel CPUs. TDT allows to schedule a timer interrupt to happen in the future when TSC reaches
    certain value. Wult can use this as a source of delayed events.
    """

    supported_devices = {"tdt" : "TSC deadline timer"}

    def __init__(self, devid, pman, cpu=0, dmesg=None):
        """
        The class constructor. The arguments are as follows.
          * devid - device ID.
          * pman - the process manager object defining the host to operate on.
          * cpu - measured CPU number.
          * dmesg - 'True' to enable 'dmesg' output checks, 'False' to disable them.
        """

        errmsg = f"device '{devid}' is not supported for CPU {cpu}{pman.hostmsg}."
        if devid not in self.supported_devices:
            raise ErrorNotSupported(f"{errmsg}")

        path = Path(f"/sys/devices/system/clockevents/clockevent{cpu}/current_device")
        with pman.open(path, "r") as fobj:
            clkname = fobj.read().strip()
            if clkname != "lapic-deadline":
                raise ErrorNotSupported(f"{errmsg}\nCurrent clockevent device is {clkname}, "
                                        f"should be 'lapic-deadline' (see {path})")

        super().__init__(devid, pman, drvname="wult_tdt", dmesg=dmesg)

        self.is_timer = True

        self.info["devid"] = devid
        self.info["descr"] = self.supported_devices["tdt"]
        # TSC resolution is 1 cycle, but we assume it is 1 nanosecond.
        self.info["resolution"] = 1

class _HRTimerDeviceBase(_DeviceBase):
    """
    Base class for Linux High Resolution Timer (hrtimers) devices. Hrtimer is basically a Linux
    kernel API for using hardware timers in a platform-independent manner. On a modern Intel CPUs,
    hrtimers typically use TSC deadline timer under the hood, but may also use LAPIC timers.
    """

    supported_devices = {}

    def _get_resolution(self):
        """Returns Linux High Resolution Timer resolution in nanoseconds."""

        errmsg_prefix = "Linux High Resolution Timer"
        errmsg_suffix = f"The resolution was acquired by running the following command" \
                        f"{self._pman.hostmsg}"

        # Get resolution in seconds and convert to nanoseconds.
        cmd = "time.clock_getres(time.CLOCK_MONOTONIC) * 1000000000"
        if self._pman.is_remote:
            python_path = self._pman.get_python_path()
            cmd = f"{python_path} -c 'import time; print(int({cmd}))'"
            resolution = self._pman.run_verify(cmd)[0].strip()

            if not Trivial.is_int(resolution):
                raise Error(f"{errmsg_prefix}: bad resolution '{resolution}' - should be an "
                            f"integer amount of nanoseconds.\n{errmsg_suffix}:\n\t{cmd}")
        else:
            resolution = time.clock_getres(time.CLOCK_MONOTONIC) * 1000000000

        resolution = int(resolution)

        if resolution < 1:
            raise Error(f"{errmsg_prefix}: bad resolution of 0 nanoseconds.\n"
                        f"{errmsg_suffix}:\n\t{cmd}")

        if resolution > 1:
            msg = f"{errmsg_prefix}: poor resolution of '{resolution}' nanoseconds."

            try:
                with self._pman.open("/proc/cmdline", "r") as fobj:
                    cmdline = fobj.read().strip()
            except Error as err:
                _LOG.debug("failed to read cmdline parameters%s: %s", self._pman.hostmsg, err)
                cmdline = ""

            if "highres=off" in cmdline:
                msg += "\nYour system uses the 'highres=off' kernel boot parameter, try " \
                       "removing it."
            else:
                msg += "\nMake sure your kernel has high resolution timers enabled " \
                       "(CONFIG_HIGH_RES_TIMERS)."

            if resolution > _MAX_RESOLUTION:
                raise Error(msg)

            _LOG.warning(msg)

        return resolution

    def __init__(self, devid, pman, drvname=None, helpername=None, dmesg=None):
        """
        The class constructor. The arguments are as follows.
          * devid - device ID.
          * pman - the process manager object defining the host to operate on.
          * drvname - name of the kernel driver which will be used for handling this device.
          * helpername - name of the helper tool required for handling this device.
          * dmesg - 'True' to enable 'dmesg' output checks, 'False' to disable them.
          """

        if devid not in self.supported_devices:
            raise ErrorNotSupported(f"device '{devid}' is not supported{pman.hostmsg}.")

        super().__init__(devid, pman, drvname=drvname, helpername=helpername, dmesg=dmesg)

        self.is_timer = True
        self.info["devid"] = devid
        self.info["resolution"] = self._get_resolution()

class _WultHRT(_HRTimerDeviceBase):
    """The High Resolution Timers device controlled by the 'wult_hrt' driver."""

    supported_devices = {"hrt" : "Linux High Resolution Timer via kernel driver"}

    def __init__(self, devid, pman, dmesg=None):
        """The class constructor. The arguments are the same as in '_DeviceBase.__init__()'."""

        super().__init__(devid, pman, drvname="wult_hrt", dmesg=dmesg)

        self.info["descr"] = self.supported_devices["hrt"]

class _PbeHRTimer(_HRTimerDeviceBase):
    """The High Resolution Timers device controlled by 'pbe'."""

    supported_devices = {"hrtimer" : "Linux High Resolution Timer via 'clock_nanosleep'"}

    def __init__(self, devid, pman, dmesg=None):
        """The class constructor. The arguments are the same as in '_DeviceBase.__init__()'."""

        super().__init__(devid, pman, drvname="pbe", dmesg=dmesg)

        self.info["descr"] = self.supported_devices["hrtimer"]

def GetDevice(toolname, devid, pman, cpu=0, dmesg=None):
    """
    The device object factory - creates and returns the correct type of device object
    depending on the tool and 'devid'. The arguments are as follows:
      * toolname - name of the tool to create a device object for ("wult" or "ndl").
      * devid - same as in '_DeviceBase.__init__()'.
      * pman - same as in '_DeviceBase.__init__()'.
      * cpu - measured CPU number.
      * dmesg - 'True' to enable 'dmesg' output checks, 'False' to disable them.
    """

    if toolname == "wult":
        if devid in _WultTSCDeadlineTimer.supported_devices:
            return _WultTSCDeadlineTimer(devid, pman, cpu=cpu, dmesg=dmesg)

        if devid in _WultHRT.supported_devices:
            return _WultHRT(devid, pman, dmesg=dmesg)

    if toolname == "pbe":
        if devid in _PbeHRTimer.supported_devices:
            return _PbeHRTimer(devid, pman, dmesg=dmesg)

    if toolname == "wult":
        clsname = "_WultIntelI210"
    elif toolname == "ndl":
        clsname = "_NdlIntelI210"
    else:
        raise Error(f"BUG: bad tool name '{toolname}'")

    try:
        return globals().get(clsname)(devid, pman, dmesg=dmesg)
    except ErrorNotSupported as err:
        raise ErrorNotSupported(f"unsupported device '{devid}'{pman.hostmsg}") from err

def scan_devices(toolname, pman):
    """
    Scan the host defined by 'pman' for devices suitable for the 'toolname' tool. The arguments are
    as follows.
      * toolname - name of the tool to scan for ("wult" or "ndl").
      * pman - the process manager object defining the host to scan on.

    Yields the device object for every compatible device.
    """

    if toolname == "pbe":
        for devid in _PbeHRTimer.supported_devices:
            with contextlib.suppress(Error):
                with _PbeHRTimer(devid, pman, dmesg=False) as timerdev:
                    yield timerdev
        return

    if toolname == "wult":
        for devid in _WultTSCDeadlineTimer.supported_devices:
            with contextlib.suppress(Error):
                with _WultTSCDeadlineTimer(devid, pman, dmesg=False) as timerdev:
                    yield timerdev

        for devid in _WultHRT.supported_devices:
            with contextlib.suppress(Error):
                with _WultHRT(devid, pman, dmesg=False) as timerdev:
                    yield timerdev

    if toolname == "wult":
        clsname = "_WultIntelI210"
    elif toolname == "ndl":
        clsname = "_NdlIntelI210"
    else:
        raise Error(f"BUG: bad tool name '{toolname}'")

    with PCI.LsPCI(pman) as lspci:
        for pci_info in lspci.lspci():
            cls = globals().get(clsname)
            if not cls.supported_devices.get(pci_info["devid"]):
                continue
            with contextlib.suppress(ErrorNotSupported):
                with cls(pci_info["addr"], pman, dmesg=False) as i210dev:
                    yield i210dev
