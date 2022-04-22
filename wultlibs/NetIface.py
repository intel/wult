# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides API for managing network interfaces in Linux.
"""

import re
import logging
import ipaddress
import random
import time
import contextlib
from pathlib import Path
from collections import namedtuple
from pepclibs.helperlibs import FSHelpers, LocalProcessManager, Trivial, ClassHelpers
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
from wultlibs import LsPCI

_LOG = logging.getLogger()

# A unique object used as the default value for the 'default' keyword argument in various
# functions.
_RAISE = object()

# Base path to the network information in the sysfs filesystem.
_SYSFSBASE = Path("/sys/class/net")

# Unique PCI device ID.
PCIDeviceID = namedtuple("PCIDeviceID", ["domain", "bus", "device", "function"])

def _looks_like_ip(name):
    """Return 'True' if 'name' looks like an IP address and 'False' otherwise."""

    try:
        ipaddress.ip_address(name)
    except ValueError:
        return False
    return True

def _get_ifinfos(pman):
    """
    For every network interfaces backed by a real device on the system defined by 'pman', yield the
    following tuples:
    * interface name
    * device HW address
    """

    for ifname, path, typ in FSHelpers.lsdir(_SYSFSBASE, pman=pman):
        if typ != "@":
            # We expect a symlink.
            continue

        devpath = None
        with contextlib.suppress(Error):
            devpath = pman.abspath(path / "device")
        if not devpath:
            continue

        yield ifname, devpath.name

def _get_ifnames(pman):
    """
    Yields names of network interfaces backed by a real device on the system defined by 'pman'.
    """

    for ifname, _ in _get_ifinfos(pman):
        yield ifname

def _parse_ip_address_show(raw):
    """
    Parse output of the 'ip address show <IFNAME>' command and return the resulting dictionary.
    """

    info = {}
    for line in raw.splitlines():
        line = line.strip()
        elts = Trivial.split_csv_line(line, sep=" ")
        if re.match(r"^\d+:$", elts[0]):
            info["ifname"] = elts[1][:-1]
        elif elts[0] == "inet":
            ipnet = ipaddress.IPv4Network(elts[1], strict=False)
            info["ipv4"] = {}
            info["ipv4"]["ip"] = ipnet.network_address
            info["ipv4"]["mask"] = ipnet.netmask
            info["ipv4"]["bcast"] = ipnet.broadcast_address
            info["ipv4"]["ip_cidr"] = elts[1]
            info["ipv4"]["cidr"] = str(ipnet)
        elif elts[0] == "link/ether":
            info["ether"] = {}
            info["ether"]["mac"] = elts[1]
            info["ether"]["bcast"] = elts[3]

    return info

class NetIface:
    """API for managing network interfaces in Linux."""

    def get_unique_ipv4_addr(self):
        """
        Generate a random unique IPv4 address which does not belong to any network on the host.
        """

        max_attempts = 128
        for _ in range(max_attempts):
            ipaddr = ".".join([str(random.randint(0, 255)) for _ in range(4)])
            for ifname in _get_ifnames(self._pman):
                netif = NetIface(ifname, pman=self._pman)
                netinfo = netif.get_ip_info()

                if "ipv4" not in netinfo:
                    continue

                addrobj = ipaddress.IPv4Address(ipaddr)
                netobj = ipaddress.IPv4Network(netinfo["ipv4"]["cidr"])
                if addrobj in netobj:
                    _LOG.debug("IPv4 address '%s' belongs to interface '%s', retrying",
                               ipaddr, ifname)
                    break
            else:
                # We found the unique IP.
                return ipaddr

        raise Error(f"failed to find a random unique IP address for host '{self._pman.hostname}'")

    def has_carrier(self):
        """
        Returns 'True' if the network interface has carrier and 'False' otherwise. Returns 'None' if
        it is not possible to get carrier status, most probably because the interface is disabled.
        """

        path = self._sysfsbase.joinpath("carrier")
        try:
            with self._pman.open(path, "r") as fobj:
                value = fobj.read()
        except Error:
            return None

        return value.strip() == "1"

    def get_pci_info(self):
        """Return network interface PCI information."""

        with LsPCI.LsPCI(pman=self._pman) as lspci:
            return lspci.get_info(self.hwaddr)

    def up(self): # pylint: disable=invalid-name
        """Bring the network interface up."""

        self._pman.run_verify(f"ip link set dev {self.ifname} up")

    def down(self):
        """Bring the network interface down."""

        self._pman.run_verify(f"ip link set dev {self.ifname} down")

    def getstate(self):
        """Return the operational state of the itnerface (up, down, etc)."""

        path = self._sysfsbase.joinpath("operstate")
        with self._pman.open(path, "r") as fobj:
            return fobj.read().strip()

    def disable_ipv6(self):
        """Disable IPv6 for the network interface."""

        path = Path("/proc/sys/net/ipv6/conf/{self.ifname}/disable_ipv6")
        if self._pman.is_file(path):
            with self._pman.open(path, "w") as fobj:
                fobj.write("1")

    def wait_for_carrier(self, timeout):
        """Wait for the network interface carrier to appear for maximum of 'timeout' seconds."""

        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.has_carrier():
                return
            time.sleep(0.1)

        raise Error(f"network interface '{self.ifname}'{self._pman.hostmsg} has no carrier, "
                    f"waited for {timeout} seconds")

    def get_ip_info(self):
        """
        Run the "ip address show" for the network interface, parse the output and return the result
        and return the output.
        """

        stdout, _ = self._pman.run_verify(f"ip address show {self.ifname}")
        return _parse_ip_address_show(stdout)

    def get_ipv4_addr(self, default=_RAISE):
        """
        Returns IPv4 address of the network interface. If it does not have an IP address, this
        method raises an exception. However, the 'default' argument overrides this behavior and
        makes this function return 'default' instead.
        """

        info = self.get_ip_info()
        if "ipv4" not in info:
            if default is _RAISE:
                raise Error(f"interface '{self.ifname}'{self._pman.hostmsg} does not have an IPv4 "
                            f"address")
            return default

        return info["ipv4"]["ip"]

    def set_ipv4_addr(self, ip):
        """
        Set IPv4 address of the network interface to 'ip', which should have the "x.y.z.w/pfx"
        format. The previous IP address can later be restored with 'restore_ipv4_addr()'.
        """

        self._saved_ip_info = self.get_ip_info()
        self._pman.run_verify(f"ip address add {ip} dev {self.ifname}")

    def restore_ipv4_addr(self):
        """
        Restore the IPv4 address that the network interface was using before the 'set_ipv4_addr()'
        function was called.
        """

        if not self._saved_ip_info:
            return

        info = self._saved_ip_info
        cmd = "add"
        if "ipv4" not in self._saved_ip_info:
            info = self.get_ip_info()
            if "ipv4" not in info:
                return
            cmd = "del"

        self._pman.run_verify(f"ip address {cmd} {info['ipv4']['ip_cidr']} dev {self.ifname}")

    def _get_hw_addr(self):
        """
        Return the hardware address for the NIC corresponding to the network interface. Typically
        the hardware address is a PCI address, such as '0000:04:00.0'.
        """

        # The "device" symlink leads to the sysfs subdirectory corresponding to the underlying NIC.
        path = self._sysfsbase / "device"
        if not self._pman.exists(path):
            raise ErrorNotFound(f"cannot find network interface '{self.ifname}':\n"
                                f"path '{path}' does not exist{self._pman.hostmsg}'")

        # The name of the subdirectory is the hardware address.
        path = self._pman.abspath(path)
        return path.name

    def _raise_iface_not_found(self):
        """
        Raise and error with a helpful message in case the network interface corresponding to
        'self._ifid' was not found.
        """

        msg1 = msg2 = ""
        if _looks_like_ip(self._ifid):
            msg1 = "\nIt looks like you specified an IP address. Please, specify name of network " \
                   "interface instead."
        try:
            msg2 = ", ".join(_get_ifnames(self._pman))
            msg2 = f"\nHere is the list of network iterfaces available{self._pman.hostmsg}: {msg2}."
        except Error:
            pass

        raise ErrorNotFound(f"network interface '{self._ifid}' was not found{self._pman.hostmsg}."
                            f"{msg1}{msg2}")

    def _hw_addr_to_ifname(self):
        """
        Find network interface name corresponding to hardware address in 'self._ifid'. Returns
        'None' if the network interface was not found.
        """

        # Go through all network interfaces and check for the "device" symlink, which will contain
        # the HW address of the network interface. Tested with PCI devices.
        for ifname, hwaddr in _get_ifinfos(self._pman):
            if self._ifid == hwaddr:
                _LOG.debug("resolved '%s' to '%s'", self._ifid, ifname)
                return ifname

        return None

    def __init__(self, ifid, pman=None):
        """
        Initialize a class instance network interface corresponding to 'ifid' on the host associated
        with the 'pman' object. The 'ifid' argumen can be either the network interface name or its
        hardware address (e.g., the PCI address of the network card corresponding to the network
        interface).
        """

        self._ifid = ifid
        self._pman = pman
        self.ifname = None
        self.hwaddr = None
        self._sysfsbase = None
        self._saved_ip_info = {}
        self._ip_tool_present = None

        self._close_pman = pman is None

        if not self._pman:
            self._pman = LocalProcessManager.LocalProcessManager()

        sysfsbase = _SYSFSBASE.joinpath(ifid)
        if self._pman.is_dir(sysfsbase):
            # 'ifid' is a network interface name.
            self.ifname = ifid
            self._sysfsbase = sysfsbase
            self.hwaddr = self._get_hw_addr()
        else:
            # 'ifid' is probably a HW address (e.g., PCI address).
            self.ifname = self._hw_addr_to_ifname()
            if not self.ifname:
                self._raise_iface_not_found()
            self.hwaddr = ifid
            self._sysfsbase = _SYSFSBASE.joinpath(self.ifname)

    def close(self):
        """Uninitialize the class object."""
        ClassHelpers.close(self, close_attrs=("_pman",))

    def __enter__(self):
        """Enter the runtime context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()
