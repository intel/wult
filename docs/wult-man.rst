====
WULT
====

:Date:   2023-04-28

.. contents::
   :depth: 3
..

NAME
====

wult

SYNOPSIS
========

**wult** [-h] [-q] [-d] [--version] [--force-color]
{deploy,scan,start,report,filter,calc} ...

DESCRIPTION
===========

wult - a tool for measuring C-state latency.

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

**wult** *deploy*
   Compile and deploy wult helpers and drivers.

**wult** *scan*
   Scan for available devices.

**wult** *start*
   Start the measurements.

**wult** *report*
   Create an HTML report.

**wult** *filter*
   Filter datapoints out of a test result.

**wult** *calc*
   Calculate summary functions for a wult test result.

COMMAND *'wult* deploy'
=======================

usage: wult deploy [-h] [-q] [-d] [--kernel-src KSRC] [--rebuild-bpf]
[--local-build] [--tmpdir-path TMPDIR_PATH] [--keep-tmpdir] [-H
HOSTNAME] [-U USERNAME] [-K PRIVKEY] [-T TIMEOUT] [--skip-drivers]

Compile and deploy wult helpers and drivers to the SUT (System Under
Test), which can be can be either local or a remote host, depending on
the '-H' option. By default, everything is built on the SUT, but the
'--local-build' can be used for building on the local system. The
drivers are searched for in the following directories (and in the
following order) on the local host: ./drivers/idle,
$WULT_DATA_PATH/drivers/idle, $HOME/.local/share/wult/drivers/idle,
/usr/local/share/wult/drivers/idle, /usr/share/wult/drivers/idle.

OPTIONS *'wult* deploy'
=======================

**-h**
   Show this help message and exit.

**-q**
   Be quiet.

**-d**
   Print debugging information.

**--kernel-src** *KSRC*
   Path to the Linux kernel sources to build drivers and eBPF helpers
   against. The default is '/lib/modules/$(uname -r)/build' on the SUT.
   If '--local-build' was used, then the path is considered to be on the
   local system, rather than the SUT.

**--rebuild-bpf**
   eBPF helpers sources consist of 2 components: the user-space
   component and the eBPF component. The user-space component is
   distributed as a source code, and must be compiled. The eBPF
   component is distributed as both source code and in binary (compiled)
   form. By default, the eBPF component is not re-compiled. This option
   is meant to be used by wult developers to re-compile the eBPF
   component if it was modified.

**--local-build**
   Build helpers and drivers locally, instead of building on HOSTNAME
   (the SUT).

**--tmpdir-path** *TMPDIR_PATH*
   When 'wult' is deployed, a random temporary directory is used. Use
   this option provide a custom path instead. It will be used as a
   temporary directory on both local and remote hosts. This option is
   meant for debugging purposes.

**--keep-tmpdir**
   Do not remove the temporary directories created while deploying
   'wult'. This option is meant for debugging purposes.

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

**--skip-drivers**
   Deploy the eBPF helper, but do not deploy the drivers. This is a
   debug and development option, do not use it for other purposes.

COMMAND *'wult* scan'
=====================

usage: wult scan [-h] [-q] [-d] [--all] [-H HOSTNAME] [-U USERNAME] [-K
PRIVKEY] [-T TIMEOUT]

Scan for available devices.

OPTIONS *'wult* scan'
=====================

**-h**
   Show this help message and exit.

**-q**
   Be quiet.

**-d**
   Print debugging information.

**--all**
   By default this command prints only the compatible devices which are
   supported by current wult installation. This option makes this
   command print about all the compatible devices.

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

COMMAND *'wult* start'
======================

usage: wult start [-h] [-q] [-d] [-H HOSTNAME] [-U USERNAME] [-K
PRIVKEY] [-T TIMEOUT] [-c COUNT] [--time-limit LIMIT] [--exclude
EXCLUDE] [--include INCLUDE] [--keep-filtered] [-o OUTDIR] [--reportid
REPORTID] [--stats STATS] [--stats-intervals STATS_INTERVALS]
[--list-stats] [-l LDIST] [--cpunum CPUNUM] [--tsc-cal-time
TSC_CAL_TIME] [--keep-raw-data] [--no-unload] [--early-intr] [--report]
[--force] devid

Start measuring and recording C-state latency.

**devid**
   The ID of the device to use for measuring the latency. For example,
   it can be a PCI address of the Intel I210 device, or "tdt" for the
   TSC deadline timer block of the CPU. Use the 'scan' command to get
   supported devices.

OPTIONS *'wult* start'
======================

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

**-c** *COUNT*, **--datapoints** *COUNT*
   How many datapoints should the test result include, default is
   1000000. Note, unless the '--start-over' option is used, the
   pre-existing datapoints are taken into account. For example, if the
   test result already has 6000 datapoints and memory.

**--time-limit** *LIMIT*
   The measurement time limit, i.e., for how long the SUT should be
   measured. The default unit is minute, but you can use the following
   handy specifiers as well: d - days, h - hours, m - minutes, s -
   seconds. For example '1h25m' would be 1 hour and 25 minutes, or 10m5s
   would be 10 minutes and 5 seconds. Value '0' means "no time limit",
   and this is the default. If this option is used along with the
   '--datapoints' option, then measurements will stop as when either the
   time limit is reached, or the required amount of datapoints is
   collected.

**--exclude** *EXCLUDE*
   Datapoints to exclude: remove all the datapoints satisfying the
   expression 'EXCLUDE'. Here is an example of an expression:
   '(WakeLatency < 10000) \| (PC6% < 1)'. This filter expression will
   remove all datapoints with 'WakeLatency' smaller than 10000
   nanoseconds or package C6 residency smaller than 1%. You can use any
   metrics in the expression.

**--include** *INCLUDE*
   Datapoints to include: remove all datapoints except for those
   satisfying the expression 'INCLUDE'. In other words, this option is
   the inverse of '--exclude'. This means, '--include expr' is the same
   as '--exclude "not (expr)"'.

**--keep-filtered**
   If the '--exclude' / '--include' options are used, then the
   datapoints not matching the selector or matching the filter are
   discarded. This is the default behavior which can be changed with
   this option. If '--keep-filtered' has been specified, then all
   datapoints are saved in result. Here is an example. Suppose you want
   to collect 100000 datapoints where PC6 residency is greater than 0.
   In this case, you can use these options: -c 100000 --exclude="PC6% ==
   0". The result will contain 100000 datapoints, all of them will have
   non-zero PC6 residency. But what if you do not want to simply discard
   the other datapoints, because they are also interesting? Well, add
   the '--keep-filtered' option. The result will contain, say, 150000
   datapoints, 100000 of which will have non-zero PC6 residency.

**-o** *OUTDIR*, **--outdir** *OUTDIR*
   Path to the directory to store the results at.

**--reportid** *REPORTID*
   Any string which may serve as an identifier of this run. By default
   report ID is the current date, prefixed with the remote host name in
   case the '-H' option was used: [hostname-]YYYYMMDD. For example,
   "20150323" is a report ID for a run made on March 23, 2015. The
   allowed characters are: ACSII alphanumeric, '-', '.', ',', '_', '~',
   and ':'.

**--stats** *STATS*
   Comma-separated list of statistics to collect. The statistics are
   collected in parallel with measuring C-state latency. They are stored
   in the the "stats" sub-directory of the output directory. By default,
   only 'turbostat, sysinfo' statistics are collected. Use 'all' to
   collect all possible statistics. Use '--stats=""' or '--stats="none"'
   to disable statistics collection. If you know exactly what statistics
   you need, specify the comma-separated list of statistics to collect.
   For example, use 'turbostat,acpower' if you need only turbostat and
   AC power meter statistics. You can also specify the statistics you do
   not want to be collected by pre-pending the '!' symbol. For example,
   'all,!turbostat' would mean: collect all the statistics supported by
   the SUT, except for 'turbostat'. Use the '--list-stats' option to get
   more information about available statistics. By default, only
   'sysinfo' statistics are collected.

**--stats-intervals** *STATS_INTERVALS*
   The intervals for statistics. Statistics collection is based on doing
   periodic snapshots of data. For example, by default the 'acpower'
   statistics collector reads SUT power consumption for the last second
   every second, and 'turbostat' default interval is 5 seconds. Use
   'acpower:5,turbostat:10' to increase the intervals to 5 and 10
   seconds correspondingly. Use the '--list-stats' to get the default
   interval values.

**--list-stats**
   Print information about the statistics 'wult' can collect and exit.

**-l** *LDIST*, **--ldist** *LDIST*
   This tool works by scheduling a delayed event, then sleeping and
   waiting for it to happen. This step is referred to as a "measurement
   cycle" and it is usually repeated many times. The launch distance
   defines how far in the future the delayed event is scheduled. By
   default this tool randomly selects launch distance within a range.
   The default range is [0,4ms], but you can override it with this
   option. Specify a comma-separated range (e.g '--ldist 10,5000'), or a
   single value if you want launch distance to be precisely that value
   all the time. The default unit is microseconds, but you can use the
   following specifiers as well: ms - milliseconds, us - microseconds,
   ns - nanoseconds. For example, ' --ldist 10us,5ms' would be a
   [10,5000] microseconds range. Too small values may cause failures or
   prevent the SUT from reaching deep C-states. If the range starts with
   0, the minimum possible launch distance value allowed by the delayed
   event source will be used. The optimal launch distance range is
   system-specific.

**--cpunum** *CPUNUM*
   The logical CPU number to measure, default is CPU 0.

**--tsc-cal-time** *TSC_CAL_TIME*
   Wult receives raw datapoints from the driver, then processes them,
   and then saves the processed datapoint in the 'datapoints.csv' file.
   The processing involves converting TSC cycles to microseconds, so
   wult needs SUT's TSC rate. TSC rate is calculated from the
   datapoints, which come with TSC counters and timestamps, so TSC rate
   can be calculated as "delta TSC / delta timestamp". In other words,
   wult needs two datapoints to calculate TSC rate. However, the
   datapoints have to be far enough apart, and this option defines the
   distance between the datapoints (in seconds). The default distance is
   10 seconds, which means that wult will keep collecting and buffering
   datapoints for 10s without processing them (because processing
   requires TSC rate to be known). After 10s, wult will start processing
   all the buffered datapoints, and then the newly collected datapoints.
   Generally, longer TSC calculation time translates to better accuracy.

**--keep-raw-data**
   Wult receives raw datapoints from the driver, then processes them,
   and then saves the processed datapoint in the 'datapoints.csv' file.
   In order to keep the CSV file smaller, wult keeps only the essential
   information, and drops the rest. For example, raw timestamps are
   dropped. With this option, however, wult saves all the raw data to
   the CSV file, along with the processed data.

**--no-unload**
   This option exists for debugging and troubleshooting purposes.
   Please, do not use for other reasons. If wult loads kernel modules,
   they get unloaded after the measurements are done. But with this
   option wult will not unload the modules.

**--early-intr**
   This option is for research purposes and you most probably do not
   need it. Linux's 'cpuidle' subsystem enters most C-states with
   interrupts disabled. So when the CPU exits the C-state because of an
   interrupt, it will not jump to the interrupt handler, but instead,
   continue running some 'cpuidle' housekeeping code. After this, the
   'cpuidle' subsystem enables interrupts, and the CPU jumps to the
   interrupt handler. Therefore, there is a tiny delay the 'cpuidle'
   subsystem adds on top of the hardware C-state latency. For fast
   C-states like C1, this tiny delay may even be measurable on some
   platforms. This option allows to measure that delay. It makes wult
   enable interrupts before linux enters the C-state.

**--report**
   Generate an HTML report for collected results (same as calling
   'report' command with default arguments).

**--force**
   By default a network card is not accepted as a measurement device if
   it is used by a Linux network interface and the interface is in an
   active state, such as "up". Use '--force' to disable this safety
   mechanism. Use it with caution.

COMMAND *'wult* report'
=======================

usage: wult report [-h] [-q] [-d] [-o OUTDIR] [--exclude EXCLUDE]
[--include INCLUDE] [--even-up-dp-count] [-x XAXES] [-y YAXES] [--hist
HIST] [--chist CHIST] [--reportids REPORTIDS] [--report-descr
REPORT_DESCR] [--relocatable] [--list-metrics] [--size REPORT_SIZE]
respaths [respaths ...]

Create an HTML report for one or multiple test results.

**respaths**
   One or multiple wult test result paths.

OPTIONS *'wult* report'
=======================

**-h**
   Show this help message and exit.

**-q**
   Be quiet.

**-d**
   Print debugging information.

**-o** *OUTDIR*, **--outdir** *OUTDIR*
   Path to the directory to store the report at. By default the report
   is stored in the 'wult-report-<reportid>' sub-directory of the test
   result directory. If there are multiple test results, the report is
   stored in the current directory. The '<reportid>' is report ID of
   wult test result.

**--exclude** *EXCLUDE*
   Datapoints to exclude: remove all the datapoints satisfying the
   expression 'EXCLUDE'. Here is an example of an expression:
   '(WakeLatency < 10000) \| (PC6% < 1)'. This filter expression will
   remove all datapoints with 'WakeLatency' smaller than 10000
   nanoseconds or package C6 residency smaller than 1%. The detailed
   expression syntax can be found in the documentation for the 'eval()'
   function of Python 'pandas' module. You can use metrics in the
   expression, or the special word 'index' for the row number (0-based
   index) of a datapoint in the results. For example, expression 'index
   >= 10' will get rid of all datapoints except for the first 10 ones.

**--include** *INCLUDE*
   Datapoints to include: remove all datapoints except for those
   satisfying the expression 'INCLUDE'. In other words, this option is
   the inverse of '--exclude'. This means, '--include expr' is the same
   as '--exclude "not (expr)"'.

**--even-up-dp-count**
   Even up datapoints count before generating the report. This option is
   useful when generating a report for many test results (a diff). If
   the test results contain different count of datapoints (rows count in
   the CSV file), the resulting histograms may look a little bit
   misleading. This option evens up datapoints count in the test
   results. It just finds the test result with the minimum count of
   datapoints and ignores the extra datapoints in the other test
   results.

**-x** *XAXES*, **--xaxes** *XAXES*
   A comma-separated list of metrics (or python style regular
   expressions matching the names) to use on X-axes of the scatter
   plot(s), default is 'SilentTime'. Use '--list-metrics' to get the
   list of the available metrics. Use value 'none' to disable scatter
   plots.

**-y** *YAXES*, **--yaxes** *YAXES*
   A comma-separated list of metrics (or python style regular
   expressions matching the names) to use on the Y-axes for the scatter
   plot(s). If multiple metrics are specified for the X- or Y-axes, then
   the report will include multiple scatter plots for all the X- and
   Y-axes combinations. The default is '.*Latency'. Use '--list-metrics'
   to get the list of the available metrics. Use value 'none' to disable
   scatter plots.

**--hist** *HIST*
   A comma-separated list of metrics (or python style regular
   expressions matching the names) to add a histogram for, default is
   '.*Latency'. Use '--list-metrics' to get the list of the available
   metrics. Use value 'none' to disable histograms.

**--chist** *CHIST*
   A comma-separated list of metrics (or python style regular
   expressions matching the names) to add a cumulative distribution for,
   default is 'None'. Use '--list-metrics' to get the list of the
   available metrics. Use value 'none' to disable cumulative histograms.

**--reportids** *REPORTIDS*
   Every input raw result comes with a report ID. This report ID is
   basically a short name for the test result, and it used in the HTML
   report to refer to the test result. However, sometimes it is helpful
   to temporarily override the report IDs just for the HTML report, and
   this is what the '--reportids' option does. Please, specify a
   comma-separated list of report IDs for every input raw test result.
   The first report ID will be used for the first raw rest result, the
   second report ID will be used for the second raw test result, and so
   on. Please, refer to the '--reportid' option description in the
   'start' command for more information about the report ID.

**--report-descr** *REPORT_DESCR*
   The report description - any text describing this report as whole, or
   path to a file containing the overall report description. For
   example, if the report compares platform A and platform B, the
   description could be something like

**--relocatable**
   Generate a report which contains a copy of the raw test results. With
   this option, viewers of the report will also be able to browse raw
   statistics files which are copied across with the raw test results.

**--list-metrics**
   Print the list of the available metrics and exit.

**--size** *REPORT_SIZE*
   Generate HTML report with a pre-defined set of diagrams and
   histograms. Possible values: 'small' or 'large'. This option is
   mutually exclusive with '--xaxes', '--yaxes', '--hist', '--chist'.

COMMAND *'wult* filter'
=======================

usage: wult filter [-h] [-q] [-d] [--exclude EXCLUDE] [--include
INCLUDE] [--exclude-metrics MEXCLUDE] [--include-metrics MINCLUDE]
[--human-readable] [-o OUTDIR] [--list-metrics] [--reportid REPORTID]
respath

Filter datapoints out of a test result by removing CSV rows and metrics
according to specified criteria. The criteria is specified using the row
and metric filter and selector options ('--include',
'--exclude-metrics', etc). The options may be specified multiple times.

**respath**
   The wult test result path to filter.

OPTIONS *'wult* filter'
=======================

**-h**
   Show this help message and exit.

**-q**
   Be quiet.

**-d**
   Print debugging information.

**--exclude** *EXCLUDE*
   Datapoints to exclude: remove all the datapoints satisfying the
   expression 'EXCLUDE'. Here is an example of an expression:
   '(WakeLatency < 10000) \| (PC6% < 1)'. This filter expression will
   remove all datapoints with 'WakeLatency' smaller than 10000
   nanoseconds or package C6 residency smaller than 1%. The detailed
   expression syntax can be found in the documentation for the 'eval()'
   function of Python 'pandas' module. You can use metrics in the
   expression, or the special word 'index' for the row number (0-based
   index) of a datapoint in the results. For example, expression 'index
   >= 10' will get rid of all datapoints except for the first 10 ones.

**--include** *INCLUDE*
   Datapoints to include: remove all datapoints except for those
   satisfying the expression 'INCLUDE'. In other words, this option is
   the inverse of '--exclude'. This means, '--include expr' is the same
   as '--exclude "not (expr)"'.

**--exclude-metrics** *MEXCLUDE*
   The metrics to exclude. Expects a comma-separated list of the metrics
   or python style regular expressions matching the names. For example,
   the expression 'SilentTime,WarmupDelay,.*Cyc', would remove metrics
   'SilentTime', 'WarmupDelay' and all metrics with 'Cyc' in their name.
   Use '--list-metrics' to get the list of the available metrics.

**--include-metrics** *MINCLUDE*
   The metrics to include: remove all metrics except for those specified
   by this option. The syntax is the same as for '--exclude-metrics'.

**--human-readable**
   By default the result 'filter' command print the result as a CSV file
   to the standard output. This option can be used to dump the result in
   a more human-readable form.

**-o** *OUTDIR*, **--outdir** *OUTDIR*
   By default the resulting CSV lines are printed to the standard
   output. But this option can be used to specify the output directly to
   store the result at. This will create a filtered version of the input
   test result.

**--list-metrics**
   Print the list of the available metrics and exit.

**--reportid** *REPORTID*
   Report ID of the filtered version of the result (can only be used
   with '--outdir').

COMMAND *'wult* calc'
=====================

usage: wult calc [-h] [-q] [-d] [--exclude EXCLUDE] [--include INCLUDE]
[--exclude-metrics MEXCLUDE] [--include-metrics MINCLUDE] [-f FUNCS]
[--list-funcs] [--list-metrics] [respath]

Calculates various summary functions for a wult test result (e.g., the
median value for one of the CSV columns).

**respath**
   The wult test result path to calculate summary functions for.

OPTIONS *'wult* calc'
=====================

**-h**
   Show this help message and exit.

**-q**
   Be quiet.

**-d**
   Print debugging information.

**--exclude** *EXCLUDE*
   Datapoints to exclude: remove all the datapoints satisfying the
   expression 'EXCLUDE'. Here is an example of an expression:
   '(WakeLatency < 10000) \| (PC6% < 1)'. This filter expression will
   remove all datapoints with 'WakeLatency' smaller than 10000
   nanoseconds or package C6 residency smaller than 1%. The detailed
   expression syntax can be found in the documentation for the 'eval()'
   function of Python 'pandas' module. You can use metrics in the
   expression, or the special word 'index' for the row number (0-based
   index) of a datapoint in the results. For example, expression 'index
   >= 10' will get rid of all datapoints except for the first 10 ones.

**--include** *INCLUDE*
   Datapoints to include: remove all datapoints except for those
   satisfying the expression 'INCLUDE'. In other words, this option is
   the inverse of '--exclude'. This means, '--include expr' is the same
   as '--exclude "not (expr)"'.

**--exclude-metrics** *MEXCLUDE*
   The metrics to exclude. Expects a comma-separated list of the metrics
   or python style regular expressions matching the names. For example,
   the expression 'SilentTime,WarmupDelay,.*Cyc', would remove metrics
   'SilentTime', 'WarmupDelay' and all metrics with 'Cyc' in their name.
   Use '--list-metrics' to get the list of the available metrics.

**--include-metrics** *MINCLUDE*
   The metrics to include: remove all metrics except for those specified
   by this option. The syntax is the same as for '--exclude-metrics'.

**-f** *FUNCS*, **--funcs** *FUNCS*
   Comma-separated list of summary functions to calculate. By default
   all generally interesting functions are calculated (each metric is
   associated with a list of functions that make sense for that metric).
   Use '--list-funcs' to get the list of supported functions.

**--list-funcs**
   Print the list of the available summary functions.

**--list-metrics**
   Print the list of the available metrics and exit.

AUTHORS
=======

::

   Artem Bityutskiy

::

   dedekind1@gmail.com

DISTRIBUTION
============

The latest version of wult may be downloaded from
` <https://github.com/intel/wult>`__
