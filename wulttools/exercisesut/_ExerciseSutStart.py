# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Antti Laakso <antti.laakso@linux.intel.com>
#         Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module implements 'exercise-sut start' command."""

from pepclibs.helperlibs import Logging, Trivial
from statscollecttools import ToolInfo as StcToolInfo
from wulttools.exercisesut import _BatchConfig, _Common, ToolInfo
from wulttools.ndl import ToolInfo as NdlToolInfo
from wulttools.wult import ToolInfo as WultToolInfo

NDL_TOOLNAME = NdlToolInfo.TOOLNAME
STC_TOOLNAME = StcToolInfo.TOOLNAME
WULT_TOOLNAME = WultToolInfo.TOOLNAME

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

def _check_args(args, inprops):
    """
    Check arguments and print error message and exit if we cannot proceed with provided
    arguments.
    """

    if args.only_measured_cpu and args.cpus is None:
        _LOG.error_out("please provide CPU numbers with '--only-measured-cpu', use '--cpus'")

    if not inprops:
        if args.state_reset:
            return

        _LOG.error("no commands to run. Please, specify system properties to collect test data "
                   "with. See '%s start -h' for help.", ToolInfo.TOOLNAME)

    if args.toolpath.name in (WULT_TOOLNAME, NDL_TOOLNAME) and not args.devids:
        _LOG.error_out("please, provide device ID to measure with, use '--devids'")

    if args.toolpath.name == STC_TOOLNAME and not args.command:
        _LOG.error_out("please, provide the command 'stats-collect' should run, use '--command'")

def start_command(args):
    """Exercise SUT and run workload for each requested system configuration."""

    if args.list_monikers:
        _Common.list_monikers()
        return

    inprops = {}
    for pname in _Common.PROP_INFOS:
        pvalues = getattr(args, pname, None)
        if not pvalues:
            continue
        inprops[pname] = Trivial.split_csv_line(pvalues)

    _check_args(args, inprops)

    if not args.devids:
        devids = [None]
    else:
        devids = Trivial.split_csv_line(args.devids)

    if not args.cpus:
        cpus = [None]
    else:
        cpus = Trivial.split_csv_line(args.cpus)

    with _BatchConfig.BatchConfig(args) as batchconfig:
        if args.deploy:
            batchconfig.deploy()
            _LOG.info("")

        if args.state_reset:
            reset_props = {pname: pinfo["value"] for pname, pinfo in _Common.RESET_PROPS.items()}
            if not args.only_measured_cpu:
                batchconfig.configure(reset_props, "all")
                _LOG.info("")

        for cpu in cpus:
            if args.state_reset and args.only_measured_cpu:
                batchconfig.configure(reset_props, cpu)
                _LOG.info("")

            for props in batchconfig.get_props_batch(inprops):
                batchconfig.configure(props, cpu)

                for devid in devids:
                    kwargs = {}
                    if devid:
                        kwargs["devid"] = devid
                    if args.command:
                        kwargs["command"] = args.command

                    kwargs["cpu"] = cpu

                    reportid = batchconfig.create_reportid(props, **kwargs)
                    _LOG.notice(f"measuring with: {batchconfig.props_to_str(props)}, "
                                f"report ID: '{reportid}'")

                    batchconfig.run(props, reportid, **kwargs)

                _LOG.info("")
