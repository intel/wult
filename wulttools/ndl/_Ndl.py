# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""ndl - a tool for measuring memory access latency observed by a network card."""

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
from wulttools import _Common
from wulttools.ndl import ToolInfo
from wultlibs.deploylibs import _Deploy
from wultlibs.helperlibs import Human
from wultlibs.htmlreport import NdlReportParams

VERSION = ToolInfo.VERSION
TOOLNAME = ToolInfo.TOOLNAME

# The deployment information dictionary. See 'DeployBase.__init__()' for details.
_NDL_DEPLOY_INFO = {
    "installables" : {
        "ndl" : {
            "category" : "drivers",
            "minkver"  : "5.2",
            "deployables" : ("ndl", ),
        },
        "ndl-helper" : {
            "category" : "shelpers",
            "deployables" : ("ndl-helper", ),
        },
    },
}

_LOG = logging.getLogger()
Logging.setup_logger(prefix=TOOLNAME)

def _get_axes_default(name):
    """Returns the default CSV column names for X- or Y-axes, as well as histograms."""

    names = getattr(NdlReportParams, f"DEFAULT_{name.upper()}")
    # The result is used for argparse, which does not accept '%' symbols.
    return names.replace("%", "%%")

def _build_arguments_parser():
    """Build and return the arguments parser object."""

    text = "ndl - a tool for measuring memory access latency observed by a network card."
    parser = ArgParse.SSHOptsAwareArgsParser(description=text, prog=TOOLNAME, ver=VERSION)

    text = "Force coloring of the text output."
    parser.add_argument("--force-color", action="store_true", help=text)
    subparsers = parser.add_subparsers(title="commands", dest="a command")
    subparsers.required = True

    #
    # Create parsers for the "deploy" command.
    #
    _Deploy.add_deploy_cmdline_args(TOOLNAME, _NDL_DEPLOY_INFO, subparsers, _deploy_command,
                                    argcomplete=argcomplete)

    #
    # Create parsers for the "scan" command.
    #
    text = "Scan for available devices."
    descr = """Scan for available devices."""
    subpars = subparsers.add_parser("scan", help=text, description=descr)
    subpars.set_defaults(func=_Common.scan_command)
    subpars.add_argument("--all", action="store_true",
                         help=_Common.get_scan_all_descr(TOOLNAME))

    ArgParse.add_ssh_options(subpars)

    #
    # Create parsers for the "start" command.
    #
    text = "Start the measurements."
    descr = """Start measuring and recording the latency data."""
    subpars = subparsers.add_parser("start", help=text, description=descr)
    subpars.set_defaults(func=_start_command)

    ArgParse.add_ssh_options(subpars)

    subpars.add_argument("-c", "--datapoints", default=1000000, metavar="COUNT", dest="dpcnt",
                         help=_Common.DATAPOINTS_DESCR)
    subpars.add_argument("--time-limit", dest="tlimit", metavar="LIMIT",
                         help=_Common.TIME_LIMIT_DESCR)

    arg = subpars.add_argument("-o", "--outdir", type=Path, help=_Common.START_OUTDIR_DESCR)
    if argcomplete:
        arg.completer = argcomplete.completers.DirectoriesCompleter()

    subpars.add_argument("--reportid", help=_Common.START_REPORTID_DESCR)

    subpars.add_argument("--stats", default="default", help=_Common.STATS_DESCR)

    subpars.add_argument("--stats-intervals", help=_Common.STAT_INTERVALS_DESCR)

    subpars.add_argument("--list-stats", action="store_true",
                         help=_Common.LIST_STATS_DESCR % TOOLNAME)

    text = f"""The launch distance in microseconds. This tool works by scheduling a delayed network
               packet, then sleeping and waiting for the packet to be sent. This step is referred to
               as a "measurement cycle" and it is usually repeated many times. The launch distance
               defines how far in the future the delayed network packets are scheduled. By
               default this tool randomly selects launch distance in range of [5000, 50000]
               microseconds (same as '--ldist 5000,50000'). Specify a comma-separated range or a
               single value if you want launch distance to be precisely that value all the time. The
               default unit is microseconds, but you can use the following specifiers as well:
               {Human.DURATION_NS_SPECS_DESCR}. For example, '--ldist 500us,100ms' would be a
               [500,100000] microseconds range.  Note, too low values may cause failures or prevent
               the SUT from reaching deep C-states. The optimal value is system-specific."""
    subpars.add_argument("-l", "--ldist", default="5000,50000", help=text)

    text = """The CPU number to bind the helper to. The helper will use this CPU to send delayed
              packets. In normal conditions this means that network packet buffers will be allocated
              on the NUMA node local to the CPU, but not necessarily local to the network card. Use
              this option to measure different packet memory locations on a NUMA system. Default is
              the first CPU local to the NIC."""
    subpars.add_argument("--cpunum", help=text, type=int)

    subpars.add_argument("--exclude", action=ArgParse.OrderedArg,
                         help=_Common.EXCL_START_DESCR)
    subpars.add_argument("--include", action=ArgParse.OrderedArg, help=_Common.INCL_DESCR)
    text = f"""{_Common.KEEP_FILTERED_DESCR} Here is an example. Suppose you want to collect
               100000 datapoints where RTD is greater than 50 microseconds. In this case, you can
               use these options: -c 100000 --exclude="RTD > 50". The result will contain 100000
               datapoints, all of them will have RTD bigger than 50 microseconds. But what if you do
               not want to simply discard the other datapoints, because they are also interesting?
               Well, add the '--keep-filtered' option. The result will contain, say, 150000
               datapoints, 100000 of which will have RTD value greater than 50."""
    subpars.add_argument("--keep-filtered", action="store_true", help=text)

    text = """Generate an HTML report for collected results (same as calling 'report' command with
              default arguments)."""
    subpars.add_argument("--report", action="store_true", help=text)
    subpars.add_argument("--force", action="store_true", help=_Common.START_FORCE_DESCR)

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

    subpars.add_argument("-o", "--outdir", type=Path,
                         help=_Common.get_report_outdir_descr(TOOLNAME))
    subpars.add_argument("--exclude", action=ArgParse.OrderedArg, help=_Common.EXCL_DESCR)
    subpars.add_argument("--include", action=ArgParse.OrderedArg, help=_Common.INCL_DESCR)
    subpars.add_argument("--even-up-dp-count", action="store_true", dest="even_dpcnt",
                         help=_Common.EVEN_UP_DP_DESCR)
    subpars.add_argument("-x", "--xaxes",
                         help=_Common.XAXES_DESCR % _get_axes_default("xaxes"))
    subpars.add_argument("-y", "--yaxes",
                         help=_Common.YAXES_DESCR % _get_axes_default("yaxes"))
    subpars.add_argument("--hist", help=_Common.HIST_DESCR % _get_axes_default("hist"))
    subpars.add_argument("--chist", help=_Common.CHIST_DESCR % _get_axes_default("chist"))
    subpars.add_argument("--reportids", help=_Common.REPORTIDS_DESCR)
    subpars.add_argument("--report-descr", help=_Common.REPORT_DESCR)
    subpars.add_argument("--relocatable", action="store_true", help=_Common.RELOCATABLE_DESCR)
    subpars.add_argument("--list-metrics", action="store_true",
                         help=_Common.LIST_METRICS_DESCR)

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
    subpars.add_argument("--human-readable", action="store_true",
                         help=_Common.FILTER_HUMAN_DESCR)
    subpars.add_argument("-o", "--outdir", type=Path, help=_Common.FILTER_OUTDIR_DESCR)
    subpars.add_argument("--list-metrics", action="store_true",
                         help=_Common.LIST_METRICS_DESCR)
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
    subpars.add_argument("respath", type=Path, help=text, nargs='?')

    if argcomplete:
        argcomplete.autocomplete(parser)

    return parser

def _parse_arguments():
    """Parse input arguments."""

    parser = _build_arguments_parser()

    args = parser.parse_args()
    args.toolname = TOOLNAME
    args.toolver = VERSION
    args.deploy_info = _NDL_DEPLOY_INFO

    return args

def _deploy_command(args):
    """Implements the 'ndl deploy' command."""

    from wulttools.ndl import _NdlDeploy # pylint: disable=import-outside-toplevel

    _NdlDeploy.deploy_command(args)

def _start_command(args):
    """Implements the 'ndl start' command."""

    from wulttools.ndl import _NdlStart # pylint: disable=import-outside-toplevel

    _NdlStart.start_command(args)

def _report_command(args):
    """Implements the 'ndl report' command."""

    from wulttools.ndl import _NdlReport # pylint: disable=import-outside-toplevel

    _NdlReport.report_command(args)

def main():
    """Script entry point."""

    try:
        args = _parse_arguments()

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
