# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""ndl - a tool for measuring memory access latency observed by a network card."""

# TODO: finish adding type hints to this module.
from __future__ import annotations # Remove when switching to Python 3.10+.

import typing
import argparse
from pathlib import Path

try:
    import argcomplete
    _ARGCOMPLETE_AVAILABLE = True
except ImportError:
    # We can live without argcomplete, we only lose tab completions.
    _ARGCOMPLETE_AVAILABLE = False

from pepclibs.helperlibs import Logging, ArgParse, ProjectFiles
from pepclibs.helperlibs.Exceptions import Error
from wulttools import _Common, _ToolDeploy
from wulttools.ndl import ToolInfo
from wultlibs.htmlreport import NdlReportParams

if typing.TYPE_CHECKING:
    from typing import Any, Sequence
    from statscollectlibs.deploy.DeployBase import DeployInfoTypedDict

VERSION = ToolInfo.VERSION
TOOLNAME = ToolInfo.TOOLNAME

# The deployment information dictionary. See 'DeployBase.__init__()' for details.
_NDL_DEPLOY_INFO: DeployInfoTypedDict = {
    "installables" : {
        "ndl" : {
            "category" : "drivers",
            "minkver"  : "5.2",
            "deployables" : ("ndl",),
        },
        "ndl-helper" : {
            "category" : "shelpers",
            "deployables" : ("ndl-helper",),
        },
    },
}

_LOG = Logging.getLogger(Logging.MAIN_LOGGER_NAME).configure(prefix=ToolInfo.TOOLNAME)

def _get_axes_default(name):
    """Returns the default CSV column names for X- or Y-axes, as well as histograms."""

    names = getattr(NdlReportParams, f"DEFAULT_{name.upper()}")
    # The result is used for argparse, which does not accept '%' symbols.
    return names.replace("%", "%%")

class _PrintManPathAction(argparse.Action):
    """
    Custom argparse action class to print the path to the manual pages directory and exit.
    """

    def __call__(self,
                 parser: argparse.ArgumentParser,
                 namespace: argparse.Namespace,
                 values: str | Sequence[Any] | None,
                 option_string: str | None = None):
        """Print the path to the manual pages directory and exit."""

        manpath = ProjectFiles.find_project_data(ToolInfo.TOOLNAME, "man")
        _LOG.info("%s", manpath)
        parser.exit()

def _build_arguments_parser():
    """Build and return the arguments parser object."""

    if _ARGCOMPLETE_AVAILABLE:
        completer = argcomplete.completers.DirectoriesCompleter()
    else:
        completer = None

    text = "ndl - a tool for measuring memory access latency observed by a network card."
    parser = ArgParse.ArgsParser(description=text, prog=TOOLNAME, ver=VERSION)

    subparsers = parser.add_subparsers(title="commands", dest="a command")
    subparsers.required = True

    text = f"""Print path to {ToolInfo.TOOLNAME} manual pages directory and exit. This path can be
               added to the 'MANPATH' environment variable to make the manual pages available to the
              'man' tool."""
    parser.add_argument("--print-man-path", action=_PrintManPathAction, nargs=0, help=text)

    #
    # Create parsers for the "deploy" command.
    #
    subpars = _ToolDeploy.add_deploy_cmdline_args(TOOLNAME, _NDL_DEPLOY_INFO, subparsers,
                                                  _deploy_command)

    #
    # Create parsers for the "scan" command.
    #
    text = "Scan for available devices."
    descr = """Scan for available devices."""
    subpars = subparsers.add_parser("scan", help=text, description=descr)
    subpars.set_defaults(func=_scan_command)
    subpars.add_argument("--all", action="store_true", help=_Common.get_scan_all_descr(TOOLNAME))

    ArgParse.add_ssh_options(subpars)

    #
    # Create parsers for the "start" command.
    #
    text = "Start the measurements."
    descr = """Start measuring and recording the latency data."""
    subpars = subparsers.add_parser("start", help=text, description=descr)
    subpars.set_defaults(func=_start_command)
    man_msg = "Please, refer to 'ndl-start' manual page for more information."

    ArgParse.add_ssh_options(subpars)

    subpars.add_argument("-c", "--datapoints", default=1000000, metavar="COUNT", dest="dpcnt",
                         help=f"{_Common.DATAPOINTS_DESCR} {man_msg}")
    subpars.add_argument("--time-limit", dest="tlimit", metavar="LIMIT",
                         help=f"{_Common.TIME_LIMIT_DESCR} {man_msg}")

    subpars.add_argument("-o", "--outdir", type=Path,
                          help=_Common.START_OUTDIR_DESCR).completer = completer

    subpars.add_argument("--reportid", help=_Common.START_REPORTID_DESCR)

    subpars.add_argument("--stats", default="default", help=f"{_Common.STATS_DESCR} {man_msg}")

    subpars.add_argument("--stats-intervals", help=_Common.STAT_INTERVALS_DESCR)

    subpars.add_argument("--list-stats", action="store_true",
                         help=_Common.LIST_STATS_DESCR % TOOLNAME)

    text = f"""The launch distance in microseconds. By default this tool randomly selects launch
               distance in range of [5000, 50000] microseconds (same as '--ldist 5000,50000').
               Specify a comma-separated range or a single value if you want launch distance to be
               precisely that value all the time. Note, too low values may cause failures or prevent
               the SUT from reaching deep C-states. {man_msg}"""
    subpars.add_argument("-l", "--ldist", default="5000,50000", help=text)

    text = f"""The CPU number to bind the helper to. The helper will use this CPU to send delayed
               packets. Special value 'local' can be used to specify a CPU with lowest CPU number
               local to the NIC, and this is the default value. A special value 'remote' can be used
               to specify a CPU with the lowest number remote to the NIC. {man_msg}"""
    subpars.add_argument("--cpu", help=text, default="local")

    subpars.add_argument("--exclude", action=ArgParse.OrderedArg, help=_Common.EXCL_DESCR)
    subpars.add_argument("--include", action=ArgParse.OrderedArg, help=_Common.INCL_DESCR)
    text = f"""{_Common.KEEP_FILTERED_DESCR} {man_msg}"""
    subpars.add_argument("--keep-filtered", action="store_true", help=text)

    text = """Generate an HTML report for collected results (same as calling 'report' command with
              default arguments)."""
    subpars.add_argument("--report", action="store_true", help=text)

    subpars.add_argument("--force", action="store_true", help=_Common.START_FORCE_DESCR)

    text = f"""Trash CPU cache to make sure NIC accesses memory when measuring latency. Without
               this option, there is a change the data NIC accesses is in a CPU cache. With this
               option, {TOOLNAME} allocates a buffer and fills it with data every time a delayed
               packet is scheduled. Supposedly, this should push out cached data to the memory. By
               default, the CPU cache trashing buffer size a sum of sizes of all caches on all CPUs
               (includes all levels, excludes instruction cache)."""
    subpars.add_argument("--trash-cpu-cache", action="store_true", help=text)

    text = """The network interface backed by the NIC to use for latency measurements. Today only
              Intel I210 and I211 NICs are supported. Please, specify NIC's network interface name
              (e.g., eth0)."""
    subpars.add_argument("devid", metavar="ifname", help=text)

    #
    # Create parsers for the "report" command.
    #
    text = "Create an HTML report."
    descr = """Create an HTML report for one or multiple test results."""
    subpars = subparsers.add_parser("report", help=text, description=descr)
    subpars.set_defaults(func=_report_command)
    man_msg = "Please, refer to 'ndl-report' manual page for more information."

    subpars.add_argument("-o", "--outdir", type=Path,
                         help=_Common.get_report_outdir_descr(TOOLNAME))
    subpars.add_argument("--exclude", action=ArgParse.OrderedArg,
                         help=f"{_Common.EXCL_DESCR} {man_msg}")
    subpars.add_argument("--include", action=ArgParse.OrderedArg,
                         help=f"{_Common.INCL_DESCR} {man_msg}")
    subpars.add_argument("--even-up-dp-count", action="store_true", dest="even_dpcnt",
                         help=_Common.EVEN_UP_DP_DESCR)
    subpars.add_argument("-x", "--xaxes", help=_Common.XAXES_DESCR % _get_axes_default("xaxes"))
    subpars.add_argument("-y", "--yaxes", help=_Common.YAXES_DESCR % _get_axes_default("yaxes"))
    subpars.add_argument("--hist", help=_Common.HIST_DESCR % _get_axes_default("hist"))
    subpars.add_argument("--chist", help=_Common.CHIST_DESCR % _get_axes_default("chist"))
    subpars.add_argument("--reportids", help=_Common.REPORTIDS_DESCR)
    subpars.add_argument("--report-descr", help=_Common.REPORT_DESCR)
    subpars.add_argument("--copy-raw", action="store_true", help=_Common.COPY_RAW_DESCR)
    subpars.add_argument("--list-metrics", action="store_true", help=_Common.LIST_METRICS_DESCR)

    text = f"""One or multiple {TOOLNAME} test result paths."""
    subpars.add_argument("respaths", nargs="+", type=Path, help=text)

    #
    # Create parsers for the "filter" command.
    #
    text = "Filter datapoints out of a test result."
    subpars = subparsers.add_parser("filter", help=text, description=_Common.FILT_DESCR)
    subpars.set_defaults(func=_Common.filter_command)

    subpars.add_argument("--exclude", action=ArgParse.OrderedArg, help=_Common.EXCL_DESCR)
    subpars.add_argument("--include", action=ArgParse.OrderedArg, help=_Common.INCL_DESCR)
    subpars.add_argument("--exclude-metrics", action=ArgParse.OrderedArg, dest="mexclude",
                         help=_Common.MEXCLUDE_DESCR)
    subpars.add_argument("--include-metrics", action=ArgParse.OrderedArg, dest="minclude",
                         help=_Common.MINCLUDE_DESCR)
    subpars.add_argument("--human-readable", action="store_true", help=_Common.FILTER_HUMAN_DESCR)
    subpars.add_argument("-o", "--outdir", type=Path, help=_Common.FILTER_OUTDIR_DESCR)
    subpars.add_argument("--list-metrics", action="store_true", help=_Common.LIST_METRICS_DESCR)
    subpars.add_argument("--reportid", help=_Common.FILTER_REPORTID_DESCR)

    text = f"The {TOOLNAME} test result path to filter."
    subpars.add_argument("respath", type=Path, help=text)

    #
    # Create parsers for the "calc" command.
    #
    text = f"Calculate summary functions for a {TOOLNAME} test result."
    descr = f"""Calculates various summary functions for a {TOOLNAME} test result (e.g., the median
                value for one of the CSV columns)."""
    subpars = subparsers.add_parser("calc", help=text, description=descr)
    subpars.set_defaults(func=_Common.calc_command)

    subpars.add_argument("--exclude", action=ArgParse.OrderedArg, help=_Common.EXCL_DESCR)
    subpars.add_argument("--include", action=ArgParse.OrderedArg, help=_Common.INCL_DESCR)
    subpars.add_argument("--exclude-metrics", action=ArgParse.OrderedArg, dest="mexclude",
                         help=_Common.MEXCLUDE_DESCR)
    subpars.add_argument("--include-metrics", action=ArgParse.OrderedArg, dest="minclude",
                         help=_Common.MINCLUDE_DESCR)
    subpars.add_argument("-f", "--funcs", help=_Common.FUNCS_DESCR)
    subpars.add_argument("--list-funcs", action="store_true", help=_Common.LIST_FUNCS_DESCR)
    subpars.add_argument("--list-metrics", action="store_true", help=_Common.LIST_METRICS_DESCR)

    text = f"""The {TOOLNAME} test result path to calculate summary functions for."""
    subpars.add_argument("respath", type=Path, help=text, nargs="?")

    if _ARGCOMPLETE_AVAILABLE:
        argcomplete.autocomplete(parser)

    return parser

def parse_arguments():
    """Parse input arguments."""

    parser = _build_arguments_parser()

    args = parser.parse_args()
    args.toolname = TOOLNAME
    args.toolver = VERSION

    return args

def _deploy_command(args):
    """Implements the 'ndl deploy' command."""

    _ToolDeploy.deploy_command(args, _NDL_DEPLOY_INFO)

def _scan_command(args):
    """Implements the 'ndl scan' command."""

    _Common.scan_command(args, _NDL_DEPLOY_INFO)

def _start_command(args):
    """Implements the 'ndl start' command."""

    if args.list_stats:
        _Common.start_command_list_stats()
        return

    from wulttools.ndl import _NdlStart # pylint: disable=import-outside-toplevel

    _NdlStart.start_command(args, _NDL_DEPLOY_INFO)

def _report_command(args):
    """Implements the 'ndl report' command."""

    from wulttools.ndl import _NdlReport # pylint: disable=import-outside-toplevel

    _NdlReport.report_command(args)

def main():
    """Script entry point."""

    try:
        args = parse_arguments()

        if not getattr(args, "func", None):
            _LOG.error("Please, run '%s -h' for help", TOOLNAME)
            return -1

        args.func(args)
    except KeyboardInterrupt:
        _LOG.info("\nInterrupted, exiting")
        return -1
    except Error as err:
        _LOG.error_out(err)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
