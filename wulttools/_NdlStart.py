# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module includes the "start" 'ndl' command implementation.
"""

import logging
import contextlib
from pathlib import Path

from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
from wultlibs import Deploy, ToolsCommon, NdlRunner, Devices
from wultlibs.helperlibs import Human
from wultlibs.rawresultlibs import WORawResult

_LOG = logging.getLogger()

def _generate_report(args):
    """Implements the 'report' command for start."""

    from wultlibs.htmlreport import NdlReport # pylint: disable=import-outside-toplevel

    rsts = ToolsCommon.open_raw_results([args.outdir], args.toolname)
    rep = NdlReport.NdlReport(rsts, args.outdir, title_descr=args.reportid)
    rep.relocatable = False
    rep.generate()

def start_command(args):
    """Implements the 'start' command."""

    with contextlib.ExitStack() as stack:
        pman = ToolsCommon.get_pman(args)
        stack.enter_context(pman)

        args.reportid = ToolsCommon.start_command_reportid(args, pman)

        if not args.outdir:
            args.outdir = Path(f"./{args.reportid}")
        if args.tlimit:
            args.tlimit = Human.parse_duration(args.tlimit, default_unit="m", name="time limit")

        args.ldist = ToolsCommon.parse_ldist(args.ldist)

        if not Trivial.is_int(args.dpcnt) or int(args.dpcnt) <= 0:
            raise Error(f"bad datapoints count '{args.dpcnt}', should be a positive integer")
        args.dpcnt = int(args.dpcnt)

        res = WORawResult.NdlWORawResult(args.reportid, args.outdir, args.toolver)
        stack.enter_context(res)

        ToolsCommon.setup_stdout_logging(args.toolname, res.logs_path)
        ToolsCommon.set_filters(args, res)

        try:
            dev = Devices.GetDevice(args.toolname, args.devid, pman, dmesg=True)
        except ErrorNotFound as err:
            msg = f"{err}\nTo list all usable network interfaces, please run: ndl scan"
            if pman.is_remote:
                msg += f" -H {pman.hostname}"
            raise ErrorNotFound(msg) from err
        stack.enter_context(dev)

        with Deploy.Deploy(args.toolname, args.deploy_info, pman=pman, debug=args.debug) as depl:
            depl.check_deployment(dev)

        ToolsCommon.start_command_check_network(args, pman, dev.netif)

        info = dev.netif.get_pci_info()
        if info.get("aspm_enabled"):
            _LOG.notice("PCI ASPM is enabled for the NIC '%s', and this typically increases "
                        "the measured latency.", args.devid)

        runner = NdlRunner.NdlRunner(pman, dev, res, ldist=args.ldist)
        stack.enter_context(runner)

        runner.prepare()
        runner.run(dpcnt=args.dpcnt, tlimit=args.tlimit)

    if args.report:
        _generate_report(args)
