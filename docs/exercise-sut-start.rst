============
EXERCISE-SUT
============

:Date: 2024-03-08

.. contents::
   :depth: 3
..

==============================
COMMAND *'exercise-sut* start'
==============================

usage: exercise-sut start [-h] [-q] [-d] [-H HOSTNAME] [-U USERNAME] [-K
PRIVKEY] [-T TIMEOUT] [--datapoints DATAPOINTS] [--reportid-prefix
REPORTID_PREFIX] [--reportid-suffix REPORTID_SUFFIX] [--cpus CPUS]
[--cstates CSTATES] [--pcstates PCSTATES] [--turbo TURBO]
[--freqs FREQS] [--uncore-freqs UNCORE_FREQS] [--cpufreq-governor GOVERNOR]
[--idle-governor GOVERNOR] [--aspm ASPM] [--c1-demotion C1_DEMOTION]
[--c1-undemotion C1_UNDEMOTION] [--c1e-autopromote C1E_AUTOPROMOTE]
[--cstate-prewake CSTATE_PREWAKE] [--epp EPP] [--epb EPB] [--state-reset]
[--deploy] [--devids DEVIDS] [--stats STATS] [--command COMMAND]
[--stop-on-failure] [--only-measured-cpu] [--toolpath TOOLPATH]
[--cstates-config-strategy {measured-only,measured-and-poll,
measured-and-shallower}] [--use-cstate-filters] [--toolopts TOOLOPTS]
[--outdir OUTDIR] [--dry-run] [--list-monikers]

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

**--cpus** *CPUS*
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
   pstates config' command. Special value 'unl' can be used to measure
   with unlocked frequency (minimum frequency set to smallest supported
   value, and maximum frequency set to highest supported value.

**--uncore-freqs** *UNCORE_FREQS*
   Comma-separated list of package uncore frequencies to measure with.
   For more information, see '--min-uncore-freq' and '--max-uncore-freq'
   options of the 'pepc pstates config' command. Special value 'unl' can
   be used to measure with unlocked frequency (minimum frequency set to
   smallest supported value, and maximum frequency set to highest
   supported value.

**--cpufreq-governor** *GOVERNOR*
   Name of the CPU frequency governor to measure with.

**--idle-governor** *GOVERNOR*
   Name of the idle governor to measure with.

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
   'stats-collect' should run. String "{REPORTID}" in COMMAND will be
   replaced with the report ID and string "{CPU}" in COMMAND will be replaced
   with the CPU number.

**--stop-on-failure**
   Stop if any of the steps fail, instead of continuing (default).

**--only-measured-cpu**
   When changing settings, such as CPU or uncore frequency, change them only
   for the measured CPU. Some settings have scope larger than "CPU", for
   example C-states limit scope may be "package", uncore frequency scope may be
   "die". In these cases, change only the package/die that inlcudes the
   measured CPU. By default the settings are applied to all CPUs, packages,
   dies. Note, this options does not exclude I/O dies, use '--skip-io-dies'
   for that.

**--skip-io-dies**
    Skip I/O dies when changing die-scope settings, such as uncore frequency.
    Even though I/O dies do not have CPUs, by default they are configured the
    same way as compute dies.

**--toolpath** *TOOLPATH*
   Path to the tool to run. Default is 'wult'.

**--cstate-config-strategy** *{measured-only,measured-and-poll,measured-and-shallower}*
   C-state configuration strategy to use for measuring the system. The default is 'measured-only'.

**--use-cstate-filters**
   Applicable to 'wult' and 'ndl' tools. Use filters to exclude
   datapoints with zero residency of measured C-state.

**--toolopts** *TOOLOPTS*
   Additional options to use for running the tool. The string
   "\__reportid\_\_" will be replaced with generated report ID.

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
