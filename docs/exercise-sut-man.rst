============
EXERCISE-SUT
============

:Date:   2022-11-25

.. contents::
   :depth: 3
..

NAME
====

exercise-sut

SYNOPSIS
========

**exercise-sut** [-h] [-q] [-d] [--version] [-H HOSTNAME] [-U USERNAME]
[-K PRIVKEY] [-T TIMEOUT] [--force-color] [--datapoints DATAPOINTS]
[--reportid-prefix REPORTID_PREFIX] [--reportid-suffix REPORTID_SUFFIX]
[--cpunum CPUNUM] [--cstates CSTATES] [--pcstates PCSTATES]
[--only-one-cstate] [--freqs FREQS] [--uncore-freqs UNCORE_FREQS]
[--governor GOVERNOR] [--aspm ASPM] [--c1-demotion C1_DEMOTION]
[--c1e-autopromote C1E_AUTOPROMOTE] [--cstate-prewake CSTATE_PREWAKE]
[--state-reset] [--deploy] [--devids DEVIDS] [--toolpath TOOLPATH]
[--toolopts TOOLOPTS] [--outdir OUTDIR] [--stop-on-failure] [--dry-run]
[--only-measured-cpu]

DESCRIPTION
===========

exercise-sut - Run a test tool or benchmark to collect testdata.

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

**-H** *HOSTNAME*, **--host** *HOSTNAME*
   Name of the host to run the command on.

**-U** *USERNAME*, **--username** *USERNAME*
   Name of the user to use for logging into the remote host over SSH.
   The default user name is 'root'.

**-K** *PRIVKEY*, **--priv-key** *PRIVKEY*
   Path to the private SSH key that should be used for logging into the
   remote host. By default the key is automatically found from standard
   paths like

**-T** *TIMEOUT*, **--timeout** *TIMEOUT*
   SSH connect timeout in seconds, default is 8.

**--force-color**
   Force coloring of the text output.

**--datapoints** *DATAPOINTS*, **-c** *DATAPOINTS*
   Applicable only for 'wult' and 'ndl' tools. Number of datapoints to
   collect per measurement. Default is 100000.

**--reportid-prefix** *REPORTID_PREFIX*
   Custom report ID prefix string, default is the name of the SUT.

**--reportid-suffix** *REPORTID_SUFFIX*
   String to append to the report ID (nothing, by default).

**--cpunum** *CPUNUM*
   Applicable only for the 'wult' tool. The CPU number to measure with.
   Default is CPU0.

**--cstates** *CSTATES*
   Comma-separated list of requestable C-states to measure with. Default
   is all C-states.

**--pcstates** *PCSTATES*
   Comma-separated list of package C-states to measure with.

**--only-one-cstate**
   By default C-states deeper than measured C-state are disabled and
   other C-states are enabled. This option will disable all C-states,
   excluding the measured C-state.

**--freqs** *FREQS*
   Comma-separated list of frequencies to be measured with. For more
   information, see '--min-freq' and '--max-freq' options of the 'pepc
   pstates config' command.

**--uncore-freqs** *UNCORE_FREQS*
   Comma-separated list of package uncore frequencies to measure with.
   For more information, see '--min-uncore-freq' and '--max-uncore-freq'
   options of the 'pepc pstates config' command.

**--governor** *GOVERNOR*
   Name of the CPU frequency governor to measure with, default is
   "powersave".

**--aspm** *ASPM*
   Comma-separated list of PCIe ASPM configurations to measure with. The
   default is "don't care". Supported values are "on" and "off".

**--c1-demotion** *C1_DEMOTION*
   Comma-separated list of C1 demotion configurations to measure with.
   Default is "off". Supported values are "on" and "off".

**--c1e-autopromote** *C1E_AUTOPROMOTE*
   Comma-separated list of C1E autopromote configurations to measure
   with. Default is "off". Supported values are "on" and "off".

**--cstate-prewake** *CSTATE_PREWAKE*
   Comma-separated list of C-state prewake configurations to measure
   with. Default is "off". Supported values are "on" and "off".

**--state-reset**
   Set SUT settings to default values before starting measurements. The
   default values are: online all CPUs, enable all C-states, disable C1
   demotion, disable C1 undemotion, disable C1E autopromotion, disable
   C-state prewake, set CPU frequency governor to 'powersave', unlock
   CPU frequency, unlock uncore frequency, set EPP policy to
   'balance_performance', set EPB policy to 'balance_performance'.

**--deploy**
   Applicable only for 'wult' and 'ndl' tools. Run the 'deploy' command
   before starting the measurements.

**--devids** *DEVIDS*
   Applicable only for 'wult' and 'ndl' tools. Comma-separated list of
   device IDs to run the tools with.

**--toolpath** *TOOLPATH*
   Path to the tool to run. Default is "wult".

**--toolopts** *TOOLOPTS*
   Additional options to use for running the tool.

**--outdir** *OUTDIR*, **-o** *OUTDIR*
   Path to directory to store the results at.

**--stop-on-failure**
   Stop if any of the steps fail, instead of continuing (default).

**--dry-run**
   Do not run any commands, only print them.

**--only-measured-cpu**
   Change settings, for example CPU frequency and C-state limits, only
   for the measured CPU. By default settings are applied to all CPUs.

AUTHORS
=======

::

   Artem Bityutskiy

::

   dedekind1@gmail.com