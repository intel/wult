# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
pbe - a tool for measuring C-states power break even.
"""

# TODO: finish adding type hints to this module.
from __future__ import annotations # Remove when switching to Python 3.10+.

import typing
from pathlib import Path

try:
    import argcomplete
    _ARGCOMPLETE_AVAILABLE = True
except ImportError:
    # We can live without argcomplete, we only lose tab completions.
    _ARGCOMPLETE_AVAILABLE = False

from pepclibs.helperlibs import Logging, ArgParse
from pepclibs.helperlibs.Exceptions import Error
from wulttools import _Common, _ToolDeploy
from wulttools.pbe import ToolInfo

if typing.TYPE_CHECKING:
    from statscollectlibs.deploy.DeployBase import DeployInfoTypedDict

VERSION = ToolInfo.VERSION
TOOLNAME = ToolInfo.TOOLNAME

# The deployment information dictionary. See 'DeployBase.__init__()' for details.
_PBE_DEPLOY_INFO: DeployInfoTypedDict = {
    "installables" : {
        "pbe": {
            "category": "drivers",
            "minkver": "5.2",
            "deployables": ("pbe",)
        },
    },
}

_LOG = Logging.getLogger(Logging.MAIN_LOGGER_NAME).configure(prefix=ToolInfo.TOOLNAME)

def _build_arguments_parser():
    """Build and return the arguments parser object."""

    if _ARGCOMPLETE_AVAILABLE:
        completer = argcomplete.completers.DirectoriesCompleter()
    else:
        completer = None

    text = f"{TOOLNAME} - a tool for measuring C-states power break even."
    parser = ArgParse.ArgsParser(description=text, prog=TOOLNAME, ver=VERSION)

    subparsers = parser.add_subparsers(title="commands", metavar="")
    subparsers.required = True

    #
    # Create parsers for the "deploy" command.
    #
    subpars = _ToolDeploy.add_deploy_cmdline_args(TOOLNAME, _PBE_DEPLOY_INFO, subparsers,
                                                  _deploy_command)

    #
    # Create parsers for the "scan" command.
    #
    text = "Scan for device id."
    descr = """Scan for compatible devices."""
    subpars = subparsers.add_parser("scan", help=text, description=descr)
    subpars.set_defaults(func=_scan_command)

    ArgParse.add_ssh_options(subpars)

    #
    # Create parsers for the "start" command.
    #
    text = "Start the measurements."
    descr = """Start measuring C-states power break even."""
    subpars = subparsers.add_parser("start", help=text, description=descr)
    subpars.set_defaults(func=_start_command)
    man_msg = "Please, refer to 'pbe-start' manual page for more information."

    ArgParse.add_ssh_options(subpars)

    text = f"""The launch distance range to go through. The default range is [10us,10ms], but it can
               be overriden with this option by specifying a comma-separated range. The default unit
               is microseconds, but the following unit specifiers can be used:
               {_Common.DURATION_NS_SPECS_DESCR}. For example, '--ldist 20us,1ms' would be a
               [20,1000] microseconds range."""
    subpars.add_argument("-l", "--ldist", help=text, default="10,10000")

    text = f"""The launch distance step. By default it is 1%%. You can specify a percent value or an
               absolute time value. In the latter case, one of the following specifiers can be used:
               {_Common.DURATION_NS_SPECS_DESCR}. For example, '--ldist-step=1ms' means that
               launch distance will be incremented by 1 millisecond on every iteration. If no unit was
               specified, microseconds are assumed."""
    subpars.add_argument("-S", "--ldist-step", help=text, default="1%%")

    text = f"""For how long a single launch distance value should be measured. By default, it is 1
               minute. Specify time value in minutes, or use one of the following specifiers:
               {_Common.DURATION_SPECS_DESCR}."""
    subpars.add_argument("--span", help=text, default="1m")

    text = f"""When this tool starts measuring a new launch distance value, first it lets the system
               "warm up" for some amount of time, and starts collecting the data (e.g., power)
               only after the warm up period. This allows the system to get into the "steady state"
               (e.g., fans speed and CPU temperature stabilizes). By default, the warm up period is
               1 minute. Specify a value in minutes, or use one of the following specifiers:
               {_Common.DURATION_SPECS_DESCR}."""
    subpars.add_argument("--warmup", help=text, default="1m")

    subpars.add_argument("-o", "--outdir", type=Path,
                         help=_Common.START_OUTDIR_DESCR).completer = completer

    subpars.add_argument("--reportid", help=_Common.START_REPORTID_DESCR)

    subpars.add_argument("--stats", default="default", help=f"{_Common.STATS_DESCR} {man_msg}")

    subpars.add_argument("--stats-intervals", help=_Common.STAT_INTERVALS_DESCR)

    subpars.add_argument("--list-stats", action="store_true",
                         help=_Common.LIST_STATS_DESCR % TOOLNAME)

    subpars.add_argument("--report", action="store_true", help=_Common.START_REPORT_DESCR)

    text = """The lead CPU. This CPU will set timers and send interrupts to all other CPUs to wake
              them when the timers expire. The default is CPU 0."""
    subpars.add_argument("--lead-cpu", help=text, type=int, default=0)

    #
    # Create parsers for the "report" command.
    #
    text = "Create an HTML report."
    descr = """Create an HTML report for one or multiple test results."""
    subpars = subparsers.add_parser("report", help=text, description=descr)
    subpars.set_defaults(func=_report_command)

    subpars.add_argument("-o", "--outdir", type=Path,
                         help=_Common.get_report_outdir_descr(TOOLNAME))
    subpars.add_argument("--reportids", help=_Common.REPORTIDS_DESCR)
    subpars.add_argument("--report-descr", help=_Common.REPORT_DESCR)
    subpars.add_argument("--copy-raw", action="store_true", help=_Common.COPY_RAW_DESCR)

    text = f"""One or multiple {TOOLNAME} test result paths."""
    subpars.add_argument("respaths", nargs="+", type=Path, help=text)

    if _ARGCOMPLETE_AVAILABLE:
        argcomplete.autocomplete(parser)

    return parser

def parse_arguments():
    """Parse input arguments."""

    parser = _build_arguments_parser()

    args = parser.parse_args()
    args.devid = "hrtimer"
    args.toolname = TOOLNAME
    args.toolver = VERSION

    return args

def _deploy_command(args):
    """Implements the 'deploy' command."""

    _ToolDeploy.deploy_command(args, _PBE_DEPLOY_INFO)

def _scan_command(args):
    """Implements the 'pbe scan' command."""

    _Common.scan_command(args, _PBE_DEPLOY_INFO)

def _start_command(args):
    """Implements the 'start' command."""

    if args.list_stats:
        _Common.start_command_list_stats()
        return

    from wulttools.pbe import _PbeStart # pylint: disable=import-outside-toplevel

    _PbeStart.start_command(args, _PBE_DEPLOY_INFO)

def _report_command(args):
    """Implements the 'report' command."""

    from wulttools.pbe import _PbeReport # pylint: disable=import-outside-toplevel

    _PbeReport.report_command(args)

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
