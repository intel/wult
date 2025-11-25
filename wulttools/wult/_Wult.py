# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
wult - a tool for measuring C-state latency.
"""

# TODO: finish adding type hints to this module.
from __future__ import annotations # Remove when switching to Python 3.10+.

import sys
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
from wulttools.wult import _WultCommon, ToolInfo

if typing.TYPE_CHECKING:
    from typing import Any, Sequence
    from statscollectlibs.deploy.DeployBase import DeployInfoTypedDict

VERSION = ToolInfo.VERSION
TOOLNAME = ToolInfo.TOOLNAME

# The deployment information dictionary. See 'DeployBase.__init__()' for details.
_WULT_DEPLOY_INFO: DeployInfoTypedDict = {
    "installables" : {
        "wult" : {
            "category" : "drivers",
            "minkver"  : "5.6",
            "deployables" : ("wult", "wult_igb", "wult_tdt", "wult_hrt",),
        },
    },
}

_LOG = Logging.getLogger(Logging.MAIN_LOGGER_NAME).configure(prefix=ToolInfo.TOOLNAME)

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

    text = f"{TOOLNAME} - a tool for measuring C-state latency."
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
    subpars = _ToolDeploy.add_deploy_cmdline_args(TOOLNAME, _WULT_DEPLOY_INFO, subparsers,
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
    descr = """Start measuring and recording C-state latency."""
    subpars = subparsers.add_parser("start", help=text, description=descr)
    subpars.set_defaults(func=_start_command)
    man_msg = "Please, refer to 'wult-start' manual page for more information."

    ArgParse.add_ssh_options(subpars)

    subpars.add_argument("-c", "--datapoints", default=1000000, metavar="COUNT", dest="dpcnt",
                         help=f"{_Common.DATAPOINTS_DESCR} {man_msg}")
    subpars.add_argument("--time-limit", dest="tlimit", metavar="LIMIT",
                         help=f"{_Common.TIME_LIMIT_DESCR} {man_msg}")
    subpars.add_argument("--exclude", action=ArgParse.OrderedArg,
                         help=f"{_Common.EXCL_DESCR} {man_msg}")
    subpars.add_argument("--include", action=ArgParse.OrderedArg, help=_Common.INCL_DESCR)
    text = f"{_Common.KEEP_FILTERED_DESCR} {man_msg}"
    subpars.add_argument("--keep-filtered", action="store_true", help=text)

    subpars.add_argument("-o", "--outdir", type=Path,
                         help=_Common.START_OUTDIR_DESCR).completer = completer

    subpars.add_argument("--reportid", help=_Common.START_REPORTID_DESCR)

    subpars.add_argument("--stats", default="default", help=f"{_Common.STATS_DESCR} {man_msg}")

    subpars.add_argument("--stats-intervals", help=_Common.STAT_INTERVALS_DESCR)

    subpars.add_argument("--list-stats", action="store_true",
                         help=_Common.LIST_STATS_DESCR % TOOLNAME)

    text = f"""The launch distance defines how far in the future the delayed event is scheduled. By
               default this tool randomly selects launch distance within a range. The default range
               is [0,4ms], but you can override it with this option. Specify a comma-separated range
               (e.g '--ldist 10,5000'), or a single value if you want launch distance to be
               precisely that value all the time. {man_msg}"""
    subpars.add_argument("-l", "--ldist", help=text, default="0,4000")

    text = """The logical CPU number to measure, default is CPU 0."""
    subpars.add_argument("--cpu", help=text, type=int, default=0)

    text = f"""TSC calculation time, the default distance is 10 seconds. Generally, longer TSC
               calculation time translates to better accuracy. {man_msg}"""
    subpars.add_argument("--tsc-cal-time", default="10s", help=text)

    text = f"""Save all raw and processed datapoints collected by {TOOLNAME.title()}. {man_msg}"""
    subpars.add_argument("--keep-raw-data", action="store_true", dest="keep_rawdp", help=text)

    text = f"""This option exists for debugging and troubleshooting purposes. Please, do not use
               for other reasons. If {TOOLNAME} loads kernel modules, they get unloaded after the
               measurements are done. But with this option {TOOLNAME} will not unload the
               modules."""
    subpars.add_argument("--no-unload", action="store_true", help=text)

    subpars.add_argument("--report", action="store_true", help=_Common.START_REPORT_DESCR)
    subpars.add_argument("--force", action="store_true", help=_Common.START_FORCE_DESCR)

    text = """The ID of the device to use for measuring the latency. For example, it can be a PCI
              address of the Intel I210 device, or "tdt" for the TSC deadline timer block of the
              CPU. Use the 'scan' command to get supported devices."""
    subpars.add_argument("devid", nargs="?" if "--list-stats" in sys.argv else None, help=text)

    #
    # Create parsers for the "report" command.
    #
    text = "Create an HTML report."
    descr = """Create an HTML report for one or multiple test results."""
    subpars = subparsers.add_parser("report", help=text, description=descr)
    subpars.set_defaults(func=_report_command)

    subpars.add_argument("-o", "--outdir", type=Path,
                         help=_Common.get_report_outdir_descr(TOOLNAME))
    subpars.add_argument("--exclude", action=ArgParse.OrderedArg, help=_Common.EXCL_DESCR)
    subpars.add_argument("--include", action=ArgParse.OrderedArg, help=_Common.INCL_DESCR)
    subpars.add_argument("--even-up-dp-count", action="store_true", dest="even_dpcnt",
                         help=_Common.EVEN_UP_DP_DESCR)

    # Format axes options' help texts with default axes.
    xaxes_help = _Common.XAXES_DESCR % _WultCommon.get_axes("xaxes", escape_percent=True)
    yaxes_help = _Common.YAXES_DESCR % _WultCommon.get_axes("yaxes", escape_percent=True)
    hist_help = _Common.HIST_DESCR % _WultCommon.get_axes("hist", escape_percent=True)
    chist_help = _Common.CHIST_DESCR % _WultCommon.get_axes("chist", escape_percent=True)
    subpars.add_argument("-x", "--xaxes", help=xaxes_help)
    subpars.add_argument("-y", "--yaxes", help=yaxes_help)
    subpars.add_argument("--hist", help=hist_help)
    subpars.add_argument("--chist", help=chist_help)

    subpars.add_argument("--reportids", help=_Common.REPORTIDS_DESCR)
    subpars.add_argument("--report-descr", help=_Common.REPORT_DESCR)
    subpars.add_argument("--copy-raw", action="store_true", help=_Common.COPY_RAW_DESCR)
    subpars.add_argument("--list-metrics", action="store_true", help=_Common.LIST_METRICS_DESCR)

    text = """Generate HTML report with a pre-defined set of diagrams and histograms. Possible
              values: 'small' or 'large'. This option is mutually exclusive with '--xaxes',
              '--yaxes', '--hist', '--chist'."""
    subpars.add_argument("--size", dest="report_size", type=str, help=text)

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
    # TODO: These 2 should be removed.
    args.toolname = TOOLNAME
    args.toolver = VERSION

    return args

def _deploy_command(args):
    """Implements the 'wult deploy' command."""

    _ToolDeploy.deploy_command(args, _WULT_DEPLOY_INFO)

def _scan_command(args):
    """Implements the 'wult scan' command."""

    _Common.scan_command(args, _WULT_DEPLOY_INFO)

def _start_command(args):
    """Implements the 'wult start' command."""

    if args.list_stats:
        _Common.start_command_list_stats()
        return

    from wulttools.wult import _WultStart # pylint: disable=import-outside-toplevel

    _WultStart.start_command(args, _WULT_DEPLOY_INFO)

def _report_command(args):
    """Implements the 'wult report' command."""

    from wulttools.wult import _WultReport # pylint: disable=import-outside-toplevel

    _WultReport.report_command(args)

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
    except Error as _err:
        _LOG.error_out(_err)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
