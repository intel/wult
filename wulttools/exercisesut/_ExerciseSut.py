# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Antti Laakso <antti.laakso@linux.intel.com>
#         Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
A helper tool for exercising SUT, running workloads with various system setting permutations.
"""

import sys
import copy
from pathlib import Path
try:
    import argcomplete
except ImportError:
    # We can live without argcomplete, we only lose tab completions.
    argcomplete = None
from pepclibs.helperlibs import Logging, ArgParse
from pepclibs.helperlibs.Exceptions import Error
from statscollecttools import ToolInfo as StcToolInfo
from wulttools.exercisesut import _Common, ToolInfo
from wulttools.ndl import ToolInfo as NdlToolInfo
from wulttools.pbe import ToolInfo as PbeToolInfo
from wulttools.wult import ToolInfo as WultToolInfo

NDL_TOOLNAME = NdlToolInfo.TOOLNAME
PBE_TOOLNAME = PbeToolInfo.TOOLNAME
STC_TOOLNAME = StcToolInfo.TOOLNAME
WULT_TOOLNAME = WultToolInfo.TOOLNAME

TOOLNAME = ToolInfo.TOOLNAME
VERSION = ToolInfo.VERSION

_LOG = Logging.getLogger(Logging.MAIN_LOGGER_NAME).configure(prefix=ToolInfo.TOOLNAME)

reset_actions_text = ", ".join([pinfo["text"] for pinfo in _Common.RESET_PROPS.values()])

_COLLECT_OPTIONS = {
    "datapoints": {
        "short": "-c",
        "default": 100000,
        "help": f"""Applicable only to '{WULT_TOOLNAME}' and '{NDL_TOOLNAME}' tools. Number of
                    datapoints to collect per measurement. Default is 100000."""
    },
    "reportid_prefix": {
        "help": """String to prepend to the report ID."""
    },
    "reportid_suffix": {
        "help": """String to append to the report ID."""
    },
    "cpus": {
        "help": f"""Applicable only to the '{WULT_TOOLNAME}' and '{NDL_TOOLNAME}' tools.
                    Comma-separated list of CPU numbers to measure with."""
    },
    "cstates": {
        "help": """Comma-separated list of requestable C-states to measure with."""
    },
    "pcstates": {
        "help": """Comma-separated list of package C-states to measure with."""
    },
    "turbo": {
        "help": """Comma-separated list of turbo configurations to measure with. Supported values
                   are "on" and "off"."""
    },
    "freqs": {
        "help": """Comma-separated list of frequencies to be measured with. For more information,
                   see '--min-freq' and '--max-freq' options of the 'pepc pstates config' command.
                   Special value 'unl' can be used to measure with unlocked frequency (minimum
                   frequency set to smallest supported value, and maximum frequency set to highest
                   supported value."""
    },
    "uncore_freqs": {
        "help": """Comma-separated list of package uncore frequencies to measure with. For more
                   information, see '--min-uncore-freq' and '--max-uncore-freq' options of the
                   'pepc pstates config' command. Special value 'unl' can be used to measure with
                   unlocked frequency (minimum frequency set to smallest supported value, and
                   maximum frequency set to highest supported value."""
    },
    "cpufreq-governors": {
        "help": """Name of the CPU frequency governor to measure with."""
    },
    "idle-governors": {
        "help": """Name of the idle governor to measure with."""
    },
    "aspm": {
        "help": """Comma-separated list of PCIe ASPM configurations to measure with. Supported
                   values are "on" and "off"."""
    },
    "c1_demotion": {
        "help": """Comma-separated list of C1 demotion configurations to measure with. Supported
                   values are "on" and "off"."""
    },
    "c1_undemotion": {
        "help": """Comma-separated list of C1 undemotion configurations to measure with. Supported
                   values are "on" and "off"."""
    },
    "c1e_autopromote": {
        "help": """Comma-separated list of C1E autopromote configurations to measure with.
                   Supported values are "on" and "off"."""
    },
    "cstate_prewake": {
        "help": """Comma-separated list of C-state prewake configurations to measure with.
                   Supported values are "on" and "off"."""
    },
    "epp": {
        "help": """Comma-separated list of EPP configurations to measure with. See 'pepc pstates
                   config --epp' for more information.""",
    },
    "epb": {
        "help": """Comma-separated list of EPB configurations to measure with. See 'pepc pstates
                   config --epb' for more information.""",
    },
    "state_reset": {
        "action": "store_true",
        "help": f"""Set SUT settings to default values before starting measurements. The default
                    values are: {reset_actions_text}."""
    },
    "deploy": {
        "action": "store_true",
        "help": f"""Applicable only to '{WULT_TOOLNAME}', '{NDL_TOOLNAME}', '{PBE_TOOLNAME}' and
                    '{STC_TOOLNAME}' tools. Run the 'deploy' command before starting the
                    measurements."""
    },
    "devids": {
        "help": f"""Applicable only to '{WULT_TOOLNAME}' and '{NDL_TOOLNAME}' tools.
                    Comma-separated list of device IDs to run the tools with."""
    },
    "stats": {
        "help": f"""Applicable to '{WULT_TOOLNAME}', '{NDL_TOOLNAME}', '{PBE_TOOLNAME}' and
                    '{STC_TOOLNAME}' tools. Comma-separated list of statistics to collect."""
    },
    "stats_intervals": {
        "help": f"""Applicable to '{WULT_TOOLNAME}', '{NDL_TOOLNAME}', '{PBE_TOOLNAME}' and
                    '{STC_TOOLNAME}' tools. The intervals for statistics."""
    },
    "command": {
        "help": """Applicable only to 'stats-collect' tool. The command to that 'stats-collect'
                   should run. String "{reportid}}" in COMMAND will be replaced with the report ID
                   and the string "{CPU}" will be replaced with the CPU number."""
    },
    "only_measured_cpu": {
        "action": "store_true",
        "help": """Change settings, for example CPU frequency and C-state limits, only for the
                   measured CPU. By default settings are applied to all CPUs."""
    },
    "skip_io_dies": {
        "action": "store_true",
        "help": """Skip I/O dies when changing die-scope settings, such as uncore frequency. Even
                   though I/O dies do not have CPUs, by default they are configured the same way as
                   compute dies."""
    },
    "toolpath": {
        "type": Path,
        "default": WULT_TOOLNAME,
        "help": f"""Path to the tool to run. Default is '{WULT_TOOLNAME}'."""
    },
    "cstates_config_strategy": {
        "help": f"""C-state configuration strategy to use for measuring the system. The default is
                   '{_Common.CSTATES_CONFIG_STRATEGIES[0]}'.""",
        "choices": _Common.CSTATES_CONFIG_STRATEGIES,
        "default": _Common.CSTATES_CONFIG_STRATEGIES[0]
    },
    "no-cstate-filters": {
        "action": "store_true",
        "help": f"""Applicable to '{WULT_TOOLNAME}' and '{NDL_TOOLNAME}' tools. Do not use C-state
                    filters. C-state filters are used to exclude datapoints with zero residency of
                    measured C-state. By default C-state filters are enabled."""
    },
}

_GENERATE_OPTIONS = {
    "diffs": {
        "help": """Collected data is stored in directories, and each directory name is constructed
                   from multiple monikers separated by dashes, e.g. 'hrt-c6-uf_max-autoc1e_off'.
                   This option can be used to create diff reports by including multiple results in
                   one report. Comma-separated list of monikers to select results to include in the
                   diff report. This option can be used multiple times. If this option is not
                   provided, reports with single result are generated.""",
        "action": "append",
    },
    "include": {
        "help": "Comma-separated list of monikers that must be found from the result path name."
    },
    "exclude": {
        "help": """Comma-separated list of monikers that must not be found from the result path
                   name."""
    },
    "jobs": {
        "short": "-j",
        "type": int,
        "help": """Number of threads to use for generating reports with."""
    },
    "toolpath": {
        "type": Path,
        "help": """By default, name of the report tool is resolved from the results. This option
                   can be used to override the tool."""
    },
}

_COMMON_OPTIONS = {
    "toolopts": {
        "default": "",
        "help": """Additional options to use for running the tool. The string "reportid" in 
                   TOOLOPTS will be replaced with the report ID."""
    },
    "outdir": {
        "short": "-o",
        "type": Path,
        "help": """Path to directory to store the results at. Default is <toolname-date-time>."""
    },
    "ignore_errors": {
        "action": "store_true",
        "help": """Keep going even if any of the steps fail. Default is to stop processing commands
                   on errors."""
    },
    "dry_run": {
        "action": "store_true",
        "help": """Do not run any commands, only print them."""
    },
    "list_monikers": {
        "action": "store_true",
        "help": f"""A moniker is an abbreviation for a setting. The '{TOOLNAME}' uses monikers to
                    create directory names and report IDs for collected results. Use this option to
                    list monikers assosiated with each settings, if any, and exit."""
    },
}

def _build_arguments_parser():
    """Build and return the arguments parser object."""

    text = f"{TOOLNAME} - Run a test tool or benchmark to collect test data."
    parser = ArgParse.ArgsParser(description=text, prog=TOOLNAME, ver=VERSION)

    text = "Force coloring of the text output."
    parser.add_argument("--force-color", action="store_true", help=text)
    subparsers = parser.add_subparsers(title="commands", dest="a command")
    subparsers.required = True

    text = "Start collecting test data."
    descr = """Run a test tool or benchmark to collect test data."""
    subpars = subparsers.add_parser("start", help=text, description=descr)
    subpars.set_defaults(func=_start_command)
    ArgParse.add_ssh_options(subpars)

    options = _COLLECT_OPTIONS
    options.update(copy.deepcopy(_COMMON_OPTIONS))
    for name, kwargs in options.items():
        opt_names = [f"--{name.replace('_', '-')}"]
        if "short" in kwargs:
            opt_names += [kwargs.pop("short")]
        subpars.add_argument(*opt_names, **kwargs)

    text = "Generate reports."
    descr = """Generate reports from collected data."""
    subpars = subparsers.add_parser("report", help=text, description=descr)
    subpars.set_defaults(func=_report_command)

    options = _GENERATE_OPTIONS
    options.update(copy.deepcopy(_COMMON_OPTIONS))
    for name, kwargs in options.items():
        opt_names = [f"--{name.replace('_', '-')}"]
        if "short" in kwargs:
            opt_names += [kwargs.pop("short")]
        subpars.add_argument(*opt_names, **kwargs)

    text = """One or multiple paths to be searched for test results."""
    subpars.add_argument("respaths", nargs="*", type=Path, help=text)

    if argcomplete:
        argcomplete.autocomplete(parser)

    return parser

def parse_arguments():
    """Parse input arguments."""

    parser = _build_arguments_parser()
    return parser.parse_args()

def _start_command(args):
    """Implements the 'start' command."""

    from wulttools.exercisesut import _ExerciseSutStart # pylint: disable=import-outside-toplevel

    _ExerciseSutStart.start_command(args)

def _report_command(args):
    """Implements the 'report' command."""

    from wulttools.exercisesut import _ExerciseSutReport # pylint: disable=import-outside-toplevel

    _ExerciseSutReport.report_command(args)

def main():
    """Script entry point."""

    try:
        args = parse_arguments()

        if not getattr(args, "func", None):
            _LOG.error("please, run '%s -h' for help", TOOLNAME)
            return -1

        args.func(args)
    except KeyboardInterrupt:
        _LOG.info("\nInterrupted, exiting")
        return -1
    except Error as err:
        _LOG.error_out(err)

    return 0

if __name__ == "__main__":
    sys.exit(main())
