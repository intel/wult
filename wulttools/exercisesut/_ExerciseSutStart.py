# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Antti Laakso <antti.laakso@linux.intel.com>
#         Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""This module implements 'exercise-sut start' command."""

import contextlib
import itertools
from pepclibs import CPUIdle, CPUInfo
from pepclibs.helperlibs import Logging, Trivial, Systemctl
from statscollecttools import ToolInfo as StcToolInfo
from wulttools._Common import get_pman
from wulttools.exercisesut import _Common, ToolInfo, _CmdBuilder, _PepcCmdBuilder
from wulttools.ndl import ToolInfo as NdlToolInfo
from wulttools.wult import ToolInfo as WultToolInfo

NDL_TOOLNAME = NdlToolInfo.TOOLNAME
STC_TOOLNAME = StcToolInfo.TOOLNAME
WULT_TOOLNAME = WultToolInfo.TOOLNAME

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

_RESET_PROPS = {pname: pinfo["value"] for pname, pinfo in _Common.RESET_PROPS.items()}

def _prepare_props(args):
    """Prepare dictionary where property name is key and list of property values is value."""

    props = {}
    for pname in _Common.PROP_INFOS:
        pvalues = getattr(args, pname, None)
        if not pvalues:
            continue
        props[pname] = Trivial.split_csv_line(pvalues)

    return props

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

def _deploy(wcb, runner):
    """Deploy workload tool to the target system."""

    deploy_cmd = wcb.get_deploy_command()
    runner.run_command(deploy_cmd)
    _LOG.info("")

def _state_reset(pcb, runner, args, cpu):
    """Reset the system to a known state."""

    if not args.state_reset:
        return

    _configure(pcb, runner, _RESET_PROPS, cpu)
    _LOG.info("")

def _configure(pcb, runner, props, cpu):
    """Configure the system for measurement."""

    for cmd in pcb.get_commands(props, cpu):
        runner.run_command(cmd)

def start_command(args):
    """Exercise SUT and run workload for each requested system configuration."""

    if args.list_monikers:
        _Common.list_monikers()
        return

    inprops = _prepare_props(args)
    _check_args(args, inprops)

    devids = Trivial.split_csv_line(args.devids) if args.devids else [None]
    cpus = Trivial.split_csv_line(args.cpus) if args.cpus else [None]

    with contextlib.ExitStack() as stack:
        pman = get_pman(args)
        stack.enter_context(pman)

        cpuinfo = CPUInfo.CPUInfo(pman)
        stack.enter_context(cpuinfo)

        cpuidle = CPUIdle.CPUIdle(pman=pman, cpuinfo=cpuinfo)
        stack.enter_context(cpuidle)

        pcb = _PepcCmdBuilder.PepcCmdBuilder(pman, cpuinfo, cpuidle,
                                             args.only_measured_cpu, args.skip_io_dies,
                                             args.only_one_cstate, args.cstates_always_enable)
        stack.enter_context(pcb)

        wcb = _CmdBuilder.get_workload_cmd_builder(cpuidle, args)
        stack.enter_context(wcb)

        runner = _Common.CmdlineRunner(dry_run=args.dry_run, ignore_errors=args.ignore_errors)
        stack.enter_context(runner)

        systemctl = Systemctl.Systemctl(pman=pman)
        stack.enter_context(systemctl)

        if systemctl.is_active("tuned"):
            systemctl.stop("tuned", save=True)

        if args.deploy:
            _deploy(wcb, runner)

        if not args.only_measured_cpu:
            _state_reset(pcb, runner, args, "all")

        for props in pcb.iter_props(inprops):
            prev_cpu = None

            for cpu, devid in itertools.product(cpus, devids):
                if cpu is None or cpu != prev_cpu:
                    if args.only_measured_cpu:
                        _state_reset(pcb, runner, args, cpu)

                    _configure(pcb, runner, props, cpu)

                kwargs = {}
                if devid:
                    kwargs["devid"] = devid
                if args.command:
                    kwargs["command"] = args.command

                kwargs["cpu"] = cpu

                reportid = wcb.create_reportid(props, **kwargs)
                _LOG.notice(f"measuring with: {pcb.props_to_str(props)}, report ID: '{reportid}'")

                cmd = wcb.get_command(props, reportid, **kwargs)
                runner.run_command(cmd)

                prev_cpu = cpu
                _LOG.info("")

        if systemctl:
            systemctl.restore()
