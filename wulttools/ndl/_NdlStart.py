# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module includes the "start" 'ndl' command implementation.
"""

import logging
import contextlib
from pathlib import Path
from pepclibs import CPUInfo, CPUIdle, CStates
from pepclibs.helperlibs import Logging, Trivial, ArgParse
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound, ErrorNotSupported
from statscollectlibs.collector import StatsCollectBuilder
from wulttools import _Common
from wultlibs import NdlRunner, Devices, _FreqNoise
from wultlibs.deploylibs import _Deploy
from wultlibs.helperlibs import Human
from wultlibs.rawresultlibs import WORawResult

_LOG = logging.getLogger()

def _generate_report(args):
    """Implement the 'report' command for start."""

    from wultlibs.htmlreport import NdlReport # pylint: disable=import-outside-toplevel

    rsts = _Common.open_raw_results([args.outdir], args.toolname)
    rep = NdlReport.NdlReport(rsts, args.outdir / "html-report", report_descr=args.reportid)
    rep.relocatable = False
    rep.generate()

def _get_local_cpus(pman, ifname):
    """
    Get and return the list of integer CPU numbers local to the NIC. The list is sorted in
    ascending CPU number order.
    """

    path = f"/sys/class/net/{ifname}/device/local_cpulist"

    try:
        str_of_ranges = pman.read(path).strip()
    except Error as err:
        raise Error(f"failed to find local CPUs for the '{ifname}' NIC.\n{err.indent(2)}.\n"
                    f"Please specify CPU number, use '--cpunum'.") from err

    # The 'local_cpulist' file contains a string of comma-separated CPU numbers or ranges, smaller
    # CPU numbers go first. Example: "24-27,31-33,37-39". Only online CPUs are included. Parse the
    # string and turn into a list of integers.
    cpus = ArgParse.parse_int_list(str_of_ranges, ints=True)
    if not cpus:
        raise Error(f"failed to find local CPUs for the '{ifname}' NIC:\n  no CPU numbers in "
                    f"'{path}'")
    return cpus

def _get_remote_cpus(pman, ifname, cpuinfo):
    """
    Get and return the list of integer CPU numbers remote to the NIC. The list is sorted in
    ascending CPU number order.
    """

    lcpus = _get_local_cpus(pman, ifname)
    all_cpus = cpuinfo.get_cpus()

    rcpus = set(all_cpus) - set(lcpus)

    # Get list of NUMA node and package numbers the local CPUs belong to.
    lnodes, lpackages = set(), set()
    for lcpu in lcpus:
        levels = cpuinfo.get_cpu_levels(lcpu, levels=("node", "package"))
        lnodes.add(levels["node"])
        lpackages.add(levels["package"])

    # Try to exclude remote CPUs that are on the same NUMA node or package as local CPUs.
    new_rcpus = rcpus - set(cpuinfo.nodes_to_cpus(nodes=lnodes))
    if new_rcpus:
        rcpus = new_rcpus
    new_rcpus = rcpus - set(cpuinfo.packages_to_cpus(packages=lpackages))
    if new_rcpus:
        rcpus = new_rcpus

    return list(rcpus)

def _get_cbuf_size(args, cpuinfo):
    """Calculate the CPU cache trashing buffer size."""

    if not args.trash_cpu_cache:
        return 0

    cbuf_size = 0

    # It should be enough to write to a buffer of size equivalent to sum of all CPU caches.
    cacheinfo = cpuinfo.get_cache_info()
    for cinfo in cacheinfo.values():
        if cinfo["type"] in ("Data", "Unified"):
            cbuf_size += cinfo["all-size"]

    return cbuf_size

def _check_settings(args, pman, dev, cpuinfo):
    """
    Check platform settings and notify the user about potential "pitfalls" - the settings that may
    affect the measurements in a way an average user does not usually want.
    """

    info = dev.netif.get_pci_info()
    _Common.check_aspm_setting(info, f"the '{args.devid}' NIC")

    with contextlib.suppress(ErrorNotSupported), \
         CPUIdle.CPUIdle(pman=pman, cpuinfo=cpuinfo) as cpuidle, \
         CStates.CStates(pman=pman, cpuinfo=cpuinfo, cpuidle=cpuidle) as cstates:

        pvinfo = cstates.get_cpu_prop("pkg_cstate_limit", args.cpunum)
        if pvinfo["val"] == "PC0":
            return

        csinfo = cpuidle.get_cpu_cstates_info(args.cpunum)
        for info in csinfo.values():
            if info["name"].startswith("C6") and not info["disable"]:
                break
        else:
            return

        for pname in ("c1_demotion", "cstate_prewake"):
            pvinfo = cstates.get_cpu_prop(pname, args.cpunum)
            if pvinfo["val"] == "on":
                name = cstates.props[pname]["name"]
                _LOG.notice("%s is enabled, this may lead to lower C6 residency. It is "
                            "recommended to disable %s.", name, name)

def start_command(args):
    """
    Implement the 'start' command. The arguments are as follows.
      * args - the command line arguments object.
    """

    if args.list_stats:
        _Common.start_command_list_stats()
        return

    with contextlib.ExitStack() as stack:
        pman = _Common.get_pman(args)
        stack.enter_context(pman)

        args.reportid = _Common.start_command_reportid(args, pman)

        if not args.outdir:
            args.outdir = Path(f"./{args.reportid}")
        if args.tlimit:
            if Trivial.is_num(args.tlimit):
                args.tlimit = f"{args.tlimit}m"
            args.tlimit = Human.parse_human(args.tlimit, unit="s", integer=True, name="time limit")

        args.ldist = _Common.parse_ldist(args.ldist)

        if not Trivial.is_int(args.dpcnt) or int(args.dpcnt) <= 0:
            raise Error(f"bad datapoints count '{args.dpcnt}', should be a positive integer")
        args.dpcnt = int(args.dpcnt)

        cpuinfo = CPUInfo.CPUInfo(pman=pman)
        stack.enter_context(cpuinfo)

        try:
            dev = Devices.GetDevice(args.toolname, args.devid, pman, dmesg=True)
        except ErrorNotFound as err:
            msg = f"{err}\nTo list all usable network interfaces, please run: ndl scan"
            if pman.is_remote:
                msg += f" -H {pman.hostname}"
            raise ErrorNotFound(msg) from err
        stack.enter_context(dev)

        if Trivial.is_int(args.cpunum):
            args.cpunum = cpuinfo.normalize_cpu(int(args.cpunum))
            cpus_msg = None
        elif args.cpunum == "local":
            lcpus = _get_local_cpus(pman, dev.info["alias"])
            args.cpunum = lcpus[0]
            cpus_msg = f"Local CPU numbers: {Human.rangify(lcpus)}"
        elif args.cpunum == "remote":
            rcpus = _get_remote_cpus(pman, dev.info["alias"], cpuinfo)
            args.cpunum = rcpus[0]
            cpus_msg = f"Remote CPU numbers: {Human.rangify(rcpus)}"
        else:
            raise Error(f"bad CPU number '{args.cpunum}")

        res = WORawResult.WORawResult(args.toolname, args.toolver, args.reportid, args.outdir,
                                      cpunum=args.cpunum)
        stack.enter_context(res)

        Logging.setup_stdout_logging(args.toolname, res.logs_path)

        if cpus_msg:
            _LOG.info(cpus_msg)
        _LOG.info("Bind to CPU %d", args.cpunum)

        _Common.set_filters(args, res)

        cbuf_size = _get_cbuf_size(args, cpuinfo)
        if cbuf_size:
            human_size = Human.bytesize(cbuf_size)
            _LOG.info("CPU cache trashing buffer size: %s", human_size)

        stcoll_builder = StatsCollectBuilder.StatsCollectBuilder()
        stack.enter_context(stcoll_builder)

        if args.stats and args.stats != "none":
            stcoll_builder.parse_stnames(args.stats)
        if args.stats_intervals:
            stcoll_builder.parse_intervals(args.stats_intervals)

        stcoll = stcoll_builder.build_stcoll_nores(pman, args.reportid, cpunum=args.cpunum,
                                                   local_outdir=res.stats_path)
        if stcoll:
            stack.enter_context(stcoll)

        deploy_info = _Common.reduce_installables(args.deploy_info, dev)
        with _Deploy.DeployCheck("wult", args.toolname, deploy_info, pman=pman) as depl:
            depl.check_deployment()

        _Common.start_command_check_network(args, pman, dev.netif)
        _check_settings(args, pman, dev, cpuinfo)

        fnobj = _FreqNoise.FreqNoise(_Common.parse_freq_noise_cmdline_args(args), pman=pman)
        stack.enter_context(fnobj)

        runner = NdlRunner.NdlRunner(pman, dev, res, args.ldist, stcoll=stcoll, cbuf_size=cbuf_size,
                                     fnobj=fnobj)
        stack.enter_context(runner)

        runner.prepare()
        runner.run(dpcnt=args.dpcnt, tlimit=args.tlimit)

    if args.report:
        _generate_report(args)
