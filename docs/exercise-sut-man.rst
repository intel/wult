============
EXERCISE-SUT
============

:Date: 2024-02-09

.. contents::
   :depth: 3
..

NAME
====

exercise-sut

SYNOPSIS
========

**exercise-sut** [-h] [-q] [-d] [--version] [--force-color]
{start,report} ...

DESCRIPTION
===========

exercise-sut - Run a test tool or benchmark to collect test data.

OPTIONS
=======

**-h**
   Show this help message and exit.

**-q**
   Be quiet.

**-d**
   Print debugging information.

**--version**
   Print version and exit.

**--force-color**
   Force coloring of the text output.

COMMANDS
========

**exercise-sut** *start*
   Start collecting test data.

**exercise-sut** *report*
   Generate reports.

COMMAND *'exercise-sut* start'
==============================

usage: exercise-sut start [-h] [-q] [-d] [-H HOSTNAME] [-U USERNAME] [-K
PRIVKEY] [-T TIMEOUT] [--datapoints DATAPOINTS] [--reportid-prefix
REPORTID_PREFIX] [--reportid-suffix REPORTID_SUFFIX] [--cpunums CPUNUMS]
[--cstates CSTATES] [--pcstates PCSTATES] [--turbo TURBO] [--freqs
FREQS] [--uncore-freqs UNCORE_FREQS] [--governor GOVERNOR] [--aspm ASPM]
[--c1-demotion C1_DEMOTION] [--c1-undemotion C1_UNDEMOTION]
[--c1e-autopromote C1E_AUTOPROMOTE] [--cstate-prewake CSTATE_PREWAKE]
[--epp EPP] [--epb EPB] [--state-reset] [--deploy] [--devids DEVIDS]
[--stats STATS] [--command COMMAND] [--stop-on-failure]
[--only-measured-cpu] [--toolpath TOOLPATH] [--only-one-cstate]
[--cstates-always-enable CSTATES_ALWAYS_ENABLE] [--use-cstate-filters]
[--toolopts TOOLOPTS] [--outdir OUTDIR] [--dry-run] [--list-monikers]

Run a test tool or benchmark to collect test data.

OPTIONS *'exercise-sut* start'
==============================

**-h**
   Show this help message and exit.

**-q**
   Be quiet.

**-d**
   Print debugging information.

**-H** *HOSTNAME*, **--host** *HOSTNAME*
   Name of the host to run the command on.

**-U** *USERNAME*, **--username** *USERNAME*
   Name of the user to use for logging into the remote host over SSH.
   The default user name is 'root'.

**-K** *PRIVKEY*, **--priv-key** *PRIVKEY*
   Path to the private SSH key that should be used for logging into the
   remote host. By default the key is automatically found from standard
   paths like '~/.ssh'.

**-T** *TIMEOUT*, **--timeout** *TIMEOUT*
   SSH connect timeout in seconds, default is 8.

**--datapoints** *DATAPOINTS*, **-c** *DATAPOINTS*
   Applicable only to 'wult' and 'ndl' tools. Number of datapoints to
   collect per measurement. Default is 100000.

**--reportid-prefix** *REPORTID_PREFIX*
   String to prepend to the report ID.

**--reportid-suffix** *REPORTID_SUFFIX*
   String to append to the report ID.

**--cpunums** *CPUNUMS*
   Applicable only to the 'wult' and 'ndl' tools. Comma-separated list
   of CPU numbers to measure with.

**--cstates** *CSTATES*
   Comma-separated list of requestable C-states to measure with.

**--pcstates** *PCSTATES*
   Comma-separated list of package C-states to measure with.

**--turbo** *TURBO*
   Comma-separated list of turbo configurations to measure with.
   Supported values are "on" and "off".

**--freqs** *FREQS*
   Comma-separated list of frequencies to be measured with. For more
   information, see '--min-freq' and '--max-freq' options of the 'pepc
   pstates config' command.

**--uncore-freqs** *UNCORE_FREQS*
   Comma-separated list of package uncore frequencies to measure with.
   For more information, see '--min-uncore-freq' and '--max-uncore-freq'
   options of the 'pepc pstates config' command.

**--governor** *GOVERNOR*
   Name of the CPU frequency governor to measure with.

**--aspm** *ASPM*
   Comma-separated list of PCIe ASPM configurations to measure with.
   Supported values are "on" and "off".

**--c1-demotion** *C1_DEMOTION*
   Comma-separated list of C1 demotion configurations to measure with.
   Supported values are "on" and "off".

**--c1-undemotion** *C1_UNDEMOTION*
   Comma-separated list of C1 undemotion configurations to measure with.
   Supported values are "on" and "off".

**--c1e-autopromote** *C1E_AUTOPROMOTE*
   Comma-separated list of C1E autopromote configurations to measure
   with. Supported values are "on" and "off".

**--cstate-prewake** *CSTATE_PREWAKE*
   Comma-separated list of C-state prewake configurations to measure
   with. Supported values are "on" and "off".

**--epp** *EPP*
   Comma-separated list of EPP configurations to measure with. See 'pepc
   pstates config --epp' for more information.

**--epb** *EPB*
   Comma-separated list of EPB configurations to measure with. See 'pepc
   pstates config --epb' for more information.

**--state-reset**
   Set SUT settings to default values before starting measurements. The
   default values are: online all CPUs, enable all C-states, disable C1
   demotion, disable C1 undemotion, disable C1E autopromotion, disable
   C-state prewake, enable turbo, unlock CPU frequency, unlock uncore
   frequency, set EPP policy to 'balance_performance', set EPB policy to
   'balance-performance'.

**--deploy**
   Applicable only to 'wult' and 'ndl' tools. Run the 'deploy' command
   before starting the measurements.

**--devids** *DEVIDS*
   Applicable only to 'wult' and 'ndl' tools. Comma-separated list of
   device IDs to run the tools with.

**--stats** *STATS*
   Applicable to 'wult', 'ndl' 'stats-collect'tools. Comma-separated
   list of statistics to collect.

**--command** *COMMAND*
   Applicable only to 'stats-collect' tool. The command to that
   'stats-collect' should run.

**--stop-on-failure**
   Stop if any of the steps fail, instead of continuing (default).

**--only-measured-cpu**
   Change settings, for example CPU frequency and C-state limits, only
   for the measured CPU. By default settings are applied to all CPUs.

**--toolpath** *TOOLPATH*
   Path to the tool to run. Default is 'wult'.

**--only-one-cstate**
   By default C-states deeper than measured C-state are disabled and
   other C-states are enabled. This option will disable all C-states,
   excluding the measured C-state.

**--cstates-always-enable** *CSTATES_ALWAYS_ENABLE*
   Comma-separated list of always enabled C-states.

**--use-cstate-filters**
   Applicable to 'wult' and 'ndl' tools. Use filters to exclude
   datapoints with zero residency of measured C-state.

**--toolopts** *TOOLOPTS*
   Additional options to use for running the tool. The string
   "__reportid__" will be replaced with generated report ID.

**--outdir** *OUTDIR*, **-o** *OUTDIR*
   Path to directory to store the results at. Default is
   <toolname-date-time>.

**--dry-run**
   Do not run any commands, only print them.

**--list-monikers**
   A moniker is an abbreviation for a setting. The 'exercise-sut' uses
   monikers to create directory names and report IDs for collected
   results. Use this option to list monikers assosiated with each
   settings, if any, and exit.

COMMAND *'exercise-sut* report'
===============================

usage: exercise-sut report [-h] [-q] [-d] [--diffs DIFFS] [--include
INCLUDE] [--exclude EXCLUDE] [--jobs JOBS] [--toolpath TOOLPATH]
[--toolopts TOOLOPTS] [--outdir OUTDIR] [--stop-on-failure] [--dry-run]
[--list-monikers] [respaths ...]

Generate reports from collected data.

**respaths**
   One or multiple paths to be searched for test results.

OPTIONS *'exercise-sut* report'
===============================

**-h**
   Show this help message and exit.

**-q**
   Be quiet.

**-d**
   Print debugging information.

**--diffs** *DIFFS*
   Collected data is stored in directories, and each directory name is
   constructed from multiple monikers separated by dashes, e.g.
   'hrt-c6-uf_max-autoc1e_off'. This option can be used to create diff
   reports by including multiple results in one report. Comma-separated
   list of monikers to select results to include in the diff report.
   This option can be used multiple times. If this option is not
   provided, reports with single result are generated.

**--include** *INCLUDE*
   Comma-separated list of monikers that must be found from the result
   path name.

**--exclude** *EXCLUDE*
   Comma-separated list of monikers that must not be found from the
   result path name.

**--jobs** *JOBS*, **-j** *JOBS*
   Number of threads to use for generating reports with.

**--toolpath** *TOOLPATH*
   By default, name of the report tool is resolved from the results.
   This option can be used to override the tool.

**--toolopts** *TOOLOPTS*
   Additional options to use for running the tool. The string
   "__reportid__" will be replaced with generated report ID.

**--outdir** *OUTDIR*, **-o** *OUTDIR*
   Path to directory to store the results at. Default is
   <toolname-date-time>.

**--stop-on-failure**
   Stop if any of the steps fail, instead of continuing (default).

**--dry-run**
   Do not run any commands, only print them.

**--list-monikers**
   A moniker is an abbreviation for a setting. The 'exercise-sut' uses
   monikers to create directory names and report IDs for collected
   results. Use this option to list monikers assosiated with each
   settings, if any, and exit.

AUTHOR
======

::

   Artem Bityutskiy

::

   dedekind1@gmail.com

DISTRIBUTION
============

The latest version of wult may be downloaded from
` <https://github.com/intel/wult>`__
