# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""stats-collect - a tool for collecting and visualising system statistics and telemetry."""

import sys
import logging
from pathlib import Path

try:
    import argcomplete
except ImportError:
    # We can live without argcomplete, we only lose tab completions.
    argcomplete = None

from pepclibs.helperlibs import Logging, ArgParse
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.deploylibs import _Deploy
from statscollectlibs.helperlibs import ReportID
from statscollectlibs.collector import StatsCollectBuilder

_VERSION = "1.0.0"
TOOLNAME = "stats-collect"
_STC_DEPLOY_INFO = {
    "installables" : {
        "stc-agent" : {
            "category" : "pyhelpers",
            "deployables" : ("stc-agent", "ipmi-helper", ),
        },
    },
}

_LOG = logging.getLogger()
Logging.setup_logger(prefix=TOOLNAME)

def build_arguments_parser():
    """Build and return the arguments parser object."""

    text = "stats-collect - a tool for collecting and visualising system statistics and telemetry."
    parser = ArgParse.SSHOptsAwareArgsParser(description=text, prog=TOOLNAME, ver=_VERSION)

    text = "Force coloring of the text output."
    parser.add_argument("--force-color", action="store_true", help=text)
    subparsers = parser.add_subparsers(title="commands", dest="a command")
    subparsers.required = True

    #
    # Create parsers for the "deploy" command.
    #
    subpars = _Deploy.add_deploy_cmdline_args(TOOLNAME, subparsers, _deploy_command,
                                              argcomplete=argcomplete)

    #
    # Create parsers for the "start" command.
    #
    text = "Start the measurements."
    descr = """Start collecting statistics."""
    subpars = subparsers.add_parser("start", help=text, description=descr)
    subpars.set_defaults(func=_start_command)

    ArgParse.add_ssh_options(subpars)

    text = """The logical CPU number to measure, default is CPU 0."""
    subpars.add_argument("--cpunum", help=text, type=int, default=0)
    text = """The time limit for statistics collection, after which the collection will stop if the
              command 'cmd' (given as a positional argument) has not finished executing."""
    subpars.add_argument("--time-limit", help=text, dest="tlimit", metavar="LIMIT", default=None)
    arg = subpars.add_argument("-o", "--outdir", type=Path)
    if argcomplete:
        arg.completer = argcomplete.completers.DirectoriesCompleter()

    text = f"""Any string which may serve as an identifier of this run. By default report ID is the
               current date, prefixed with the remote host name in case the '-H' option was used:
               [hostname-]YYYYMMDD. For example, "20150323" is a report ID for a run made on March
               23, 2015. The allowed characters are: {ReportID.get_charset_descr()}."""
    subpars.add_argument("--reportid", help=text)

    default_stats = ", ".join(StatsCollectBuilder.DEFAULT_STNAMES)
    text = f"""Comma-separated list of statistics to collect. They are stored in the the "stats"
               sub-directory of the output directory. By default, only '{default_stats}' statistics
               are collected. Use 'all' to collect all possible statistics. Use '--stats=""' or
               '--stats="none"' to disable statistics collection. If you know exactly what
               statistics you need, specify the comma-separated list of statistics to collect. For
               example, use 'turbostat,acpower' if you need only turbostat and AC power meter
               statistics. You can also specify the statistics you do not want to be collected by
               pre-pending the '!' symbol. For example, 'all,!turbostat' would mean: collect all the
               statistics supported by the SUT, except for 'turbostat'. Use the '--list-stats'
               option to get more information about available statistics. By default, only 'sysinfo'
               statistics are collected."""
    subpars.add_argument("--stats", default="default", help=text)

    text = """The intervals for statistics. Statistics collection is based on doing periodic
              snapshots of data. For example, by default the 'acpower' statistics collector reads
              SUT power consumption for the last second every second, and 'turbostat' default
              interval is 5 seconds. Use 'acpower:5,turbostat:10' to increase the intervals to 5 and
              10 seconds correspondingly.  Use the '--list-stats' to get the default interval
              values."""
    subpars.add_argument("--stats-intervals", help=text)
    subpars.add_argument("--report", action="store_true")

    text = """Command to run on the SUT during statistics collection. If 'HOSTNAME' is provided,
              the tool will run the command on that host, otherwise the tool will run the command on
              'localhost'."""
    subpars.add_argument("cmd", type=str, help=text)

    #
    # Create parsers for the "report" command.
    #
    text = "Create an HTML report."
    descr = """Create an HTML report for one or multiple test results."""
    subpars = subparsers.add_parser("report", help=text, description=descr)
    subpars.set_defaults(func=_report_command)

    text = f"""Path to the directory to store the report at. By default the report is stored in the
               '{TOOLNAME}-report-<reportid>' sub-directory of the test result directory. If there
               are multiple test results, the report is stored in the current directory. The
               '<reportid>' is report ID of {TOOLNAME} test result."""
    subpars.add_argument("-o", "--outdir", type=Path, help=text)

    text = f"""One or multiple {TOOLNAME} test result paths."""
    subpars.add_argument("respaths", nargs="+", type=Path, help=text)

    if argcomplete:
        argcomplete.autocomplete(parser)

    return parser

def parse_arguments():
    """Parse input arguments."""

    parser = build_arguments_parser()

    args = parser.parse_args()
    args.toolname = TOOLNAME
    args.toolver = _VERSION
    args.deploy_info = _STC_DEPLOY_INFO

    return args

def _deploy_command(args):
    """Implements the 'stats-collect deploy' command."""

    from statscollecttools import _StatsCollectDeploy # pylint: disable=import-outside-toplevel

    _StatsCollectDeploy.deploy_command(args)

def _start_command(args):
    """Implements the 'stats-collect start' command."""

    from statscollecttools import _StatsCollectStart # pylint: disable=import-outside-toplevel

    _StatsCollectStart.start_command(args)

def _report_command(args):
    """Implements the 'stats-collect report' command."""

    from statscollecttools import _StatsCollectReport # pylint: disable=import-outside-toplevel

    _StatsCollectReport.report_command(args)

def main():
    """Script entry point."""

    try:
        args = parse_arguments()

        if not getattr(args, "func", None):
            _LOG.error("please, run '%s -h' for help.", TOOLNAME)
            return -1

        args.func(args)
    except KeyboardInterrupt:
        _LOG.info("Interrupted, exiting")
        return -1
    except Error as err:
        _LOG.error_out(err)

    return 0

# The script entry point.
if __name__ == "__main__":
    sys.exit(main())
