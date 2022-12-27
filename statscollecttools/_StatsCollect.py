# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
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
from statscollecttools import _Common
from statscollectlibs.deploylibs import Deploy
from statscollectlibs.helperlibs import ReportID

_VERSION = "0.0.0"
_OWN_NAME = "stats-collect"
_STC_DEPLOY_INFO = {
    "installables" : {
        "stc-agent" : {
            "category" : "pyhelpers",
            "deployables" : ("stc-agent", "ipmi-helper", ),
        },
    },
}

_LOG = logging.getLogger()
Logging.setup_logger(prefix=_OWN_NAME)

def _build_arguments_parser():
    """Build and return the arguments parser object."""

    text = "stats-collect - a tool for collecting and visualising system statistics and telemetry."
    parser = ArgParse.SSHOptsAwareArgsParser(description=text, prog=_OWN_NAME, ver=_VERSION)

    text = "Force coloring of the text output."
    parser.add_argument("--force-color", action="store_true", help=text)
    subparsers = parser.add_subparsers(title="commands", dest="a command")
    subparsers.required = True

    #
    # Create parsers for the "deploy" command.
    #
    subpars = Deploy.add_deploy_cmdline_args(_OWN_NAME, _STC_DEPLOY_INFO, subparsers,
                                            _deploy_command, argcomplete=argcomplete)

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
    subpars.add_argument("--time-limit", dest="tlimit", metavar="LIMIT", required=True)
    arg = subpars.add_argument("-o", "--outdir", type=Path)
    if argcomplete:
        arg.completer = argcomplete.completers.DirectoriesCompleter()

    text = f"""Any string which may serve as an identifier of this run. By default report ID is the
               current date, prefixed with the remote host name in case the '-H' option was used:
               [hostname-]YYYYMMDD. For example, "20150323" is a report ID for a run made on March
               23, 2015. The allowed characters are: {ReportID.get_charset_descr()}."""
    subpars.add_argument("--reportid", help=text)

    text = """Comma-separated list of statistics to collect. They are stored in the the "stats"
              sub-directory of the output directory. By default, only 'sysinfo' statistics are
              collected. Use 'all' to collect all possible statistics. Use '--stats=""' or
              --stats='none' to disable statistics collection. If you know exactly what statistics
              you need, specify the comma-separated list of statistics to collect. For example, use
              'turbostat,acpower' if you need only turbostat and AC power meter statistics. You can
              also specify the statistics you do not want to be collected by pre-pending the '!'
              symbol. For example, 'all,!turbostat' would mean: collect all the statistics supported
              by the SUT, except for 'turbostat'. Use the '--list-stats' option to get more
              information about available statistics. By default, only 'sysinfo' statistics are
              collected."""
    subpars.add_argument("--stats", default="sysinfo", help=text)

    text = """The intervals for statistics. Statistics collection is based on doing periodic
              snapshots of data. For example, by default the 'acpower' statistics collector reads
              SUT power consumption for the last second every second, and 'turbostat' default
              interval is 5 seconds. Use 'acpower:5,turbostat:10' to increase the intervals to 5 and
              10 seconds correspondingly.  Use the '--list-stats' to get the default interval
              values."""
    subpars.add_argument("--stats-intervals", help=text)
    subpars.add_argument("--report", action="store_true")

    #
    # Create parsers for the "report" command.
    #
    text = "Create an HTML report."
    descr = """Create an HTML report for one or multiple test results."""
    subpars = subparsers.add_parser("report", help=text, description=descr)
    subpars.set_defaults(func=_report_command)

    subpars.add_argument("-o", "--outdir", type=Path,
                         help=_Common.get_report_outdir_descr(_OWN_NAME))

    text = f"""One or multiple {_OWN_NAME} test result paths."""
    subpars.add_argument("respaths", nargs="+", type=Path, help=text)

    if argcomplete:
        argcomplete.autocomplete(parser)

    return parser

def _parse_arguments():
    """Parse input arguments."""

    parser = _build_arguments_parser()

    args = parser.parse_args()
    args.toolname = _OWN_NAME
    args.toolver = _VERSION
    args.deploy_info = _STC_DEPLOY_INFO

    return args

def _deploy_command(args):
    """Implements the 'stats-collect deploy' command."""

    from statscollecttools import _StatsCollectDeploy # pylint: disable=import-outside-toplevel

    _StatsCollectDeploy.deploy_command(args)

def _start_command(args):
    """Implements the 'wult start' command."""

    from statscollecttools import _StatsCollectStart # pylint: disable=import-outside-toplevel

    _StatsCollectStart.start_command(args)

def _report_command(args):
    """Implements the 'stats-collect report' command."""

    from statscollecttools import _StatsCollectReport # pylint: disable=import-outside-toplevel

    _StatsCollectReport.report_command(args)

def main():
    """Script entry point."""

    try:
        args = _parse_arguments()

        if not getattr(args, "func", None):
            _LOG.error("please, run '%s -h' for help.", _OWN_NAME)
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
