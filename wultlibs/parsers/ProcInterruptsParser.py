# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Antti Laakso <antti.laakso@intel.com>

"""
This module implements parsing for the interrupt information table in '/proc/interrupts'.
"""

from statscollectlibs.parsers import _ParserBase

class ProcInterruptsParser(_ParserBase.ParserBase):
    """This class represents the parser for the content of '/proc/interrupts' -file."""

    def _next(self):
        """Yield dictionary of interrupts table."""

        interrupts = {}
        for line in self._lines:
            line = line.strip().split()

            if line[0] == "CPU0":
                # This is heading line. Example:
                #            CPU0       CPU1       CPU2       CPU3       CPU4
                if interrupts:
                    yield interrupts

                interrupts = {}
                interrupts["CPU"] = {}
                interrupts["IRQ"] = {}
                cpu_count = len(line)
                interrupts["cpu_count"] = cpu_count

                for cpu in range(cpu_count):
                    interrupts["CPU"][cpu] = {}
                continue

            # Interrupt info line. Example:
            # NMI:       1390       1036       1002       1707   Non-maskable interrupts
            irq_name = line.pop(0).strip(":")
            irq_info = " ".join(line[cpu_count:])
            interrupts["IRQ"][irq_name] = irq_info
            for cpu, count in enumerate(line[:cpu_count]):
                interrupts["CPU"][cpu][irq_name] = count

        yield interrupts
