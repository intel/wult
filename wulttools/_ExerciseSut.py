# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Antti Laakso <antti.laakso@linux.intel.com>
#         Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
A helper tool for exercising SUT, running workloads with various system setting permutations.
"""

import sys
import copy
import logging
from pathlib import Path
try:
    import argcomplete
except ImportError:
    # We can live without argcomplete, we only lose tab completions.
    argcomplete = None
from pepclibs.helperlibs import ArgParse, Logging, Trivial
from pepclibs.helperlibs.Exceptions import Error
from wulttools import _BatchConfig

_OWN_NAME = "exercise-sut"
_VERSION = "1.1.1"

Logging.setup_logger(prefix=_OWN_NAME)
_LOG = logging.getLogger()

_RESET_PROPS = {
    "online" : {
        "value" : "all",
        "text" : "online all CPUs"},
    "cstates" : {
        "value" : "all",
        "text" : "enable all C-states"},
    "c1_demotion" : {
        "value" : "off",
        "text" : "disable C1 demotion"},
    "c1_undemotion" : {
        "value" : "off",
        "text" : "disable C1 undemotion"},
    "c1e_autopromote" : {
        "value" : "off",
        "text" : "disable C1E autopromotion"},
    "cstate_prewake" : {
        "value" : "off",
        "text" : "disable C-state prewake"},
    "freqs" : {
        "value" : "unl",
        "text" : "unlock CPU frequency"},
    "uncore_freqs" : {
        "value" : "unl",
        "text" : "unlock uncore frequency"},
    "epp" : {
        "value" : "balance_performance",
        "text" : "set EPP policy to 'balance_performance'"},
    "epb" : {
        "value" : "balance-performance",
        "text" : "set EPB policy to 'balance-performance'"},
}

reset_actions_text = ", ".join([pinfo["text"] for pinfo in _RESET_PROPS.values()])

def _get_reset_val(pname):
    """Return reset value for property 'pname'. If it doesn't exist, return strint 'don't care'."""

    if pname in _RESET_PROPS:
        return _RESET_PROPS[pname]["value"]

    return "don't care"

_COLLECT_OPTIONS = {
    "datapoints" : {
        "short" : "-c",
        "default" : 100000,
        "help" : """Applicable only for 'wult' and 'ndl' tools. Number of datapoints to collect per
                    measurement. Default is 100000."""
    },
    "reportid_prefix" : {
        "default" : "",
        "help" : """String to prepend to the report ID (nothing, by default)."""
    },
    "reportid_suffix" : {
        "default" : "",
        "help" : """String to append to the report ID (nothing, by default)."""
    },
    "cpunum" : {
        "default" : 0,
        "help" : """Applicable only for the 'wult' tool. The CPU number to measure with. Default is
                    CPU0."""
    },
    "cstates" : {
        "default" : "all",
        "help" : """Comma-separated list of requestable C-states to measure with. Default is all
                    C-states."""
    },
    "pcstates" : {
        "help" : f"""Comma-separated list of package C-states to measure with. Default is
                     "{_get_reset_val('pcstates')}"."""
    },
    "only_one_cstate" : {
        "action" : "store_true",
        "help" : """By default C-states deeper than measured C-state are disabled and other C-states
                    are enabled. This option will disable all C-states, excluding the measured
                    C-state."""
    },
    "cstates_always_enable" : {
        "default" : None,
        "help" : """Comma-separated list of always enabled C-states. Default is 'None'."""
    },
    "freqs" : {
        "help" : """Comma-separated list of frequencies to be measured with. For more information,
                    see '--min-freq' and '--max-freq' options of the 'pepc pstates config' command.
                    """
    },
    "uncore_freqs" : {
        "help" : """Comma-separated list of package uncore frequencies to measure with. For more
                    information, see '--min-uncore-freq' and '--max-uncore-freq' options of the
                    'pepc pstates config' command."""
    },
    "governor" : {
        "help" : """Name of the CPU frequency governor to measure with."""
    },
    "aspm" : {
        "help" : f"""Comma-separated list of PCIe ASPM configurations to measure with. The default
                     is "{_get_reset_val('aspm')}". Supported values are "on" and "off"."""
    },
    "c1_demotion" : {
        "help" : f"""Comma-separated list of C1 demotion configurations to measure with. Default is
                     "{_get_reset_val('c1_demotion')}". Supported values are "on" and "off"."""
    },
    "c1_undemotion" : {
        "help" : f"""Comma-separated list of C1 undemotion configurations to measure with. Default
                     is "{_get_reset_val('c1_undemotion')}". Supported values are "on" and "off"."""
    },
    "c1e_autopromote" : {
        "help" : f"""Comma-separated list of C1E autopromote configurations to measure with. Default
                     is "{_get_reset_val('c1e_autopromote')}". Supported values are "on" and "off".
                     """
    },
    "cstate_prewake" : {
        "help" : f"""Comma-separated list of C-state prewake configurations to measure with. Default
                     is "{_get_reset_val('cstate_prewake')}". Supported values are "on" and "off".
                     """
    },
    "state_reset" : {
        "action" : "store_true",
        "help" : f"""Set SUT settings to default values before starting measurements. The default
                     values are: {reset_actions_text}."""
    },
    "deploy" : {
        "action" : "store_true",
        "help" : """Applicable only for 'wult' and 'ndl' tools. Run the 'deploy' command before
                    starting the measurements."""
    },
    "devids" : {
        "help" : """Applicable only for 'wult' and 'ndl' tools. Comma-separated list of device IDs
                    to run the tools with."""
    },
    "stop_on_failure" : {
        "action" : "store_true",
        "help" : """Stop if any of the steps fail, instead of continuing (default)."""
    },
    "only_measured_cpu" : {
        "action" : "store_true",
        "help" : """Change settings, for example CPU frequency and C-state limits, only for the
                    measured CPU. By default settings are applied to all CPUs."""
    },
}

_GENERATE_OPTIONS = {
    "diff" : {
        "help" : """Collected data is stored in directories, and each directory name is constructed
                    from multiple monikers separated by dashes, e.g. 'hrt-c6-uf_max-autoc1e_off'.
                    This option can be used to create diff reports by including multiple results in
                    one report. Comma-separated list of monikers to select results to include in the
                    diff report. If this option is not provided, reports with single result are
                    generated."""
    },
    "include" : {
        "help" : "Comma-separated list of monikers that must be found from the result path name."
    },
    "exclude" : {
        "help" : """Comma-separated list of monikers that must not be found from the result path
                    name."""
    },
    "jobs" : {
        "short": "-j",
        "type" : int,
        "help" : """Number of threads to use for generating reports with."""
    },
}

_COMMON_OPTIONS = {
    "toolpath" : {
        "type" : Path,
        "default" : "wult",
        "help" : """Path to the tool to run. Default is 'wult'."""
    },
    "toolopts" : {
        "default" : "",
        "help" : """Additional options to use for running the tool."""
    },
    "outdir" : {
        "short" : "-o",
        "type" : Path,
        "help" : """Path to directory to store the results at. Default is <toolname-date-time>."""
    },
    "stop_on_failure" : {
        "action" : "store_true",
        "help" : """Stop if any of the steps fail, instead of continuing (default)."""
    },
    "dry_run" : {
        "action" : "store_true",
        "help" : """Do not run any commands, only print them."""
    },
    "list_monikers" : {
        "action" : "store_true",
        "help" : f"""A moniker is an abbreviation for a setting. The '{_OWN_NAME}' uses monikers to
                     create directory names and report IDs for collected results. Use this option to
                     list monikers assosiated with each settings, if any, and exit."""
    },
}

def _build_arguments_parser():
    """Build and return the arguments parser object."""

    text = f"{_OWN_NAME} - Run a test tool or benchmark to collect testdata."
    parser = ArgParse.SSHOptsAwareArgsParser(description=text, prog=_OWN_NAME, ver=_VERSION)

    text = "Force coloring of the text output."
    parser.add_argument("--force-color", action="store_true", help=text)
    subparsers = parser.add_subparsers(title="commands", dest="a command")
    subparsers.required = True

    text = "Start collecting testdata."
    descr = """Run a test tool or benchmark to collect testdata. Unknown options are passed as-is to
               the tool."""
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
    descr = """Generate reports from collected data. Unknown options are passed as-is to the report
               tool."""
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
    args, uargs = parser.parse_known_args()

    toolopts = args.toolopts
    if toolopts and uargs:
        toolopts += " "

    toolopts += " ".join(uargs)
    setattr(args, "toolopts", toolopts)

    return args

def _start_command(args):
    """Exercise SUT and run workload for each requested system configuration."""

    if args.list_monikers:
        _BatchConfig.list_monikers()
        return

    if args.toolpath.name in ("wult", "ndl") and not args.devids:
        _LOG.error_out("please, provide device ID to measure with, see '%s -h' for help", _OWN_NAME)

    inprops = {}
    for pname in _BatchConfig.PROP_INFOS:
        pvalues = getattr(args, pname, None)
        if not pvalues:
            continue
        inprops[pname] = Trivial.split_csv_line(pvalues)

    with _BatchConfig.BatchConfig(args) as batchconfig:
        if args.deploy:
            batchconfig.deploy()
            _LOG.info("")

        if args.state_reset:
            reset_props = {pname : pinfo["value"] for pname, pinfo in _RESET_PROPS.items()}
            batchconfig.configure(reset_props)
            _LOG.info("")

        for props in batchconfig.get_props_batch(inprops):
            _LOG.notice(f"Measuring with properties: {batchconfig.props_to_str(props)}")

            batchconfig.configure(props)
            batchconfig.run(props)
            _LOG.info("")

def _report_command(args):
    """Implements the 'report' command."""

    if args.list_monikers:
        _BatchConfig.list_monikers()
        return

    if not args.respaths:
        _LOG.error_out("please, provide one or multiple paths to be searched for test results")

    outdir = args.outdir
    if not outdir:
        outdir = Path(f"{args.toolpath.name}-results")

    with _BatchConfig.BatchReport(args.toolpath, outdir, args.toolopts, dry_run=args.dry_run,
                                  stop_on_failure=args.stop_on_failure, proc_count=args.jobs) as \
                                  batchreport:
        for outpath, respaths in batchreport.group_results(args.respaths, diff=args.diff,
                                                           include=args.include,
                                                           exclude=args.exclude):
            # Do not generate report if diff report is requested, but we have only one result.
            if args.diff and len(respaths) < 2:
                continue

            batchreport.generate_report(respaths, outdir / outpath)
        batchreport.wait()

def main():
    """Script entry point."""

    try:
        args = parse_arguments()

        if not getattr(args, "func", None):
            _LOG.error("please, run '%s -h' for help.", _OWN_NAME)
            return -1

        args.func(args)
    except KeyboardInterrupt:
        _LOG.info("\nInterrupted, exiting")
        return -1
    except Error as err:
        _LOG.error(err)
        return -1

    return 0

if __name__ == '__main__':
    sys.exit(main())
