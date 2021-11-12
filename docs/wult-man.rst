====
wult
====

:Date:   Manual

.. contents::
   :depth: 3
..

NAME
====

wult

SYNOPSIS
========

**wult** [-h] [-q] [-d] [--version] [--force-color] ...

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

**Sub-commands**
----------------

**wult** *deploy*
   Compile and deploy wult helpers and drivers.

**wult** *scan*
   Scan for device id.

**wult** *load*
   Load wult drivers and exit.

**wult** *start*
   Start the measurements.

**wult** *report*
   Create an HTML report.

**wult** *filter*
   Filter datapoints out of a test result.

**wult** *calc*
   Calculate summary functions for a wult test result.

OPTIONS 'wult deploy'
=====================

usage: wult deploy [-h] [-q] [-d] [--kernel-src KSRC] [-H HOSTNAME] [-U
USERNAME] [-K PRIVKEY] [-T TIMEOUT]

Compile and deploy wult helpers and drivers to the SUT (System Under
Test), which can be either local or a remote host, depending on the '-H'
option.The drivers are searched for in the following directories (and in
the following order) on the local host: /usr/bin/drivers/idle,
$WULT_DATA_PATH/drivers/idle (if 'WULT_DATA_PATH' environment variable
is defined), $HOME/.local/share/wult/drivers/idle,
/usr/local/share/wult/drivers/idle, /usr/share/wult/drivers/idle.The
wult tool also depends on the following helpers: stats-collect. These
helpers will be compiled on the SUT and deployed to the SUT. The sources
of the helpers are searched for in the following paths (and in the
following order) on the local host: /usr/bin/helpers,
$WULT_DATA_PATH/helpers (if 'WULT_DATA_PATH' environment variable is
defined), $HOME/.local/share/wult/helpers,
/usr/local/share/wult/helpers, /usr/share/wult/helpers. By default,
helpers are deployed to the path defined by the WULT_HELPERSPATH
environment variable. If the variable is not defined, helpers are
deployed to '$HOME/.local/bin', where '$HOME' is the home directory of
user 'USERNAME' on host 'HOST' (see '--host' and '--username' options).

**-h**
   Show this help message and exit.

**-q**
   Be quiet.

**-d**
   Print debugging information.

**--kernel-src** *KSRC*
   Path to the Linux kernel sources to build the drivers against. The
   default is '/lib/modules/$(uname -r)/build' on the SUT. In case of
   deploying to a remote host, this is the path on the remote host
   (HOSTNAME).

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

OPTIONS 'wult scan'
===================

usage: wult scan [-h] [-q] [-d] [-H HOSTNAME] [-U USERNAME] [-K PRIVKEY]
[-T TIMEOUT]

Scan for compatible device.

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

OPTIONS 'wult load'
===================

usage: wult load [-h] [-q] [-d] [--no-unload] [--force] [-H HOSTNAME]
[-U USERNAME] [-K PRIVKEY] [-T TIMEOUT] devid

Load wult drivers and exit without starting the measurements.

**devid**
   The device ID, same as in the 'start' command.

**-h**
   Show this help message and exit.

**-q**
   Be quiet.

**-d**
   Print debugging information.

**--no-unload**
   This command exists for debugging and troubleshooting purposes.
   Please, do not use for other reasons. keep in mind that if the the
   specified 'devid' device was bound to some driver (e.g., a network
   driver), it will be unbinded and with this option It won't be binded
   back.

**--force**
   By default wult refuses to load network card drivers if its Linux
   network interface is in an active state, such as "up". Use '--force'
   to disable this safety mechanism. Use '--force' option with caution.

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

OPTIONS 'wult start'
====================

usage: wult start [-h] [-q] [-d] [-H HOSTNAME] [-U USERNAME] [-K
PRIVKEY] [-T TIMEOUT] [-c COUNT] [--time-limit LIMIT] [--rfilt RFILT]
[--rsel RSEL] [--keep-filtered] [-o OUTDIR] [--reportid REPORTID]
[--stats STATS] [--stats-intervals STATS_INTERVALS] [--list-stats] [-l
LDIST] [--cpunum CPUNUM] [--intr-focus] [--tsc-cal-time TSC_CAL_TIME]
[--keep-raw-data] [--no-unload] [--early-intr] [--dirty-cpu-cache]
[--dcbuf-size DCBUF_SIZE] [--offline OFFLINE] [--report] [--force] devid

Start measuring and recording C-state latency.

**devid**
   The ID of the device to use for measuring the latency. For example,
   it can be a PCI address of the Intel I210 device, or "tdt" for the
   TSC deadline timer block of the CPU. Use the 'scan' command to get
   supported devices.

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

**-c** COUNT, **--datapoints** COUNT
   How many datapoints should the test result include, default is
   1000000. Note, unless the '--start-over' option is used, the
   pre-existing datapoints are taken into account. For example, if the
   test result already has 6000 datapoints and memory.

**--time-limit** LIMIT
   The measurement time limit, i.e., for how long the SUT should be
   measured. The default unit is minutes, but you can use the following
   handy specifiers as well: d - days, h - hours, m - minutes, s -
   seconds. For example '1h25m' would be 1 hour and 25 minutes, or 10m5s
   would be 10 minutes and 5 seconds. Value '0' means "no time limit",
   and this is the default. If this option is used along with the
   '--datapoints' option, then measurements will stop as when either the
   time limit is reached, or the required amount of datapoints is
   collected.

**--rfilt** *RFILT*
   The row filter: remove all the rows satisfying the filter expression.
   Here is an example of an expression: '(WakeLatency < 10000) \| (PC6%
   < 1)'. This row filter expression will remove all rows with
   'WakeLatency' smaller than 10000 nanoseconds or package C6 residency
   smaller than 1%. You can use any column names in the expression.

**--rsel** *RSEL*
   The row selector: remove all rows except for those satisfying the
   selector expression. In other words, the selector is just an inverse
   filter: '--rsel expr' is the same as '--rfilt "not (expr)"'.

**--keep-filtered**
   If the '--rfilt' / '--rsel' options are used, then the datapoints not
   matching the selector or matching the filter are discarded. This is
   the default behavior which can be changed with this option. If
   '--keep-filtered' has been specified, then all datapoints are saved
   in result. Here is an example. Suppose you want to collect 100000
   datapoints where PC6 residency is greater than 0. In this case, you
   can use these options: -c 100000 --rfilt="PC6% == 0". The result will
   contain 100000 datapoints, all of them will have non-zero PC6
   residency. But what if you do not want to simply discard the other
   datapoints, because they are also interesting? Well, add the
   '--keep-filtered' option. The result will contain, say, 150000
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
   only 'sysinfo' statistics are collected. Use 'all' to collect all
   possible statistics. Use '--stats=""' or --stats='none' to disable
   statistics collection. If you know exactly what statistics you need,
   specify the comma-separated list of statistics to collect. For
   example, use 'turbostat,acpower' if you need only turbostat and AC
   power meter statistics. You can also specify the statistics you do
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
   defines how far in the future the delayed event is sceduled. By
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

**--intr-focus**
   Enable interrupt latency focused measurements. Most C-states are
   entered using the 'mwait' instruction with interrupts disabled. When
   there is an interrupt, the CPU wakes up and continues running the
   instructions after the 'mwait'. The CPU first runs some housekeeping
   code, and only then the interrupts get enabled and the CPU jumps to
   the interrupt handler. Wult measures 'WakeLatency' during the
   "housekeeping" stage, and 'IntrLatency' is measured in the interrupt
   handler. However, the 'WakeLatency' measurement takes time and
   affects the measured 'IntrLatency'. This option disables
   'WakeLatency' measurements, which improves 'IntrLatency'
   measurements' accuracy.

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
   In order to keep the CSV file smaller, wult keeps only the esential
   information, and drops the rest. For example, raw timestamps are
   dropped. With this option, however, wult saves all the raw data to
   the CSV file, along with the processed data.

**--no-unload**
   This option exists for debugging and troubleshooting purposes.
   Please, do not use for other reasons. While normally wult kernel
   modules are unloaded after the measurements are done, with this
   option the modules will stay loaded into the kernel. Keep in mind
   that if the the specified 'devid' device was bound to some driver
   (e.g., a network driver), it will be unbinded and with this option it
   won't be binded back.

**--early-intr**
   This option is for research purposes and you most probably do not
   need it. Linux's 'cpuidle' subsystem enters most C-states with
   interrupts disabled. So when the CPU exits the C-state becaouse of an
   interrupt, it will not jump to the interrupt handler, but instead,
   continue running some 'cpuidle' housekeeping code. After this, the
   'cpuidle' subsystem enables interrupts, and the CPU jumps to the
   interrupt hanlder. Therefore, there is a tiny delay the 'cpuidle'
   subsystem adds on top of the hardware C-state latency. For fast
   C-states like C1, this tiny delay may even be measurable on some
   platforms. This option allows to measure that delay. It makes wult
   enable interrupts before linux enters the C-state. This option is
   generally a crude option along with '--intr-focus'. When this option
   is used, often it makes sense to use '--intr-focus' at the same time.

**--dirty-cpu-cache**
   Deeper C-states like Intel CPU core C6 flush the CPU cache before
   entering the C-state. Therefore, the dirty CPU cache lines must be
   written back to the main memory before entering the C-state. This may
   increase C-state latency observed by the operating system. If this
   option is used, wult will try to "dirty" the measured CPU cache
   before requesting C-states. This is done by writing zeroes to a
   pre-allocated 2MiB buffer.

**--dcbuf-size** *DCBUF_SIZE*
   By default, in order to make CPU cache be filled with dirty cache
   lines, wult filles a 2MiB buffer with zeroes before requesting a
   C-state. This buffer is reffered to as "dirty cache buffer", or
   "dcbuf". This option allows for changing the dcbuf size. For example,
   in order to make it 4MiB, use '--dcbuf-size=4MiB'.

**--offline** *OFFLINE*
   Offline CPUs before the measurements. The possible values are:
   same-core, same-package, all. The "same-core" value offlines all
   other CPUs on the same core as the measured CPU. The "same-package"
   value offlines all CPUs on the same package as the measured CPU, and
   the "all" value offlines all CPUs except for the measured CPU.
   Example: consider a hypothetical 2-socket system with 2 cores per
   socket and 2 CPUs per core (e.g., hyper-threads). The default
   measured CPU is CPU0 (see '--cpunum'). Suppose CPU0-3 are on package
   0, and CPU4-7 are on package 1. Suppose CPU2 is the hyper-thread
   running on the same core as CPU0. In this case '--offline same-core'
   would offline only CPU2, '--offline same- package' would offline
   CPU1-3, '--offline all' would offline CPU1-7. The CPUs are offlined
   before starting the measurements, and onlined back after the
   measurements.

**--report**
   Generate an HTML report for collected results (same as calling
   'report' command with default arguments).

**--force**
   By default wult does not accept network card as a measurement device
   if its Linux network interface is in an active state, such as "up".
   Use '--force' to disable this safety mechanism. Use '--force' option
   with caution.

OPTIONS 'wult report'
=====================

usage: wult report [-h] [-q] [-d] [-o OUTDIR] [--rfilt RFILT] [--rsel
RSEL] [--even-up-dp-count] [-x XAXES] [-y YAXES] [--hist HIST] [--chist
CHIST] [--reportids REPORTIDS] [--title-descr TITLE_DESCR]
[--relocatable RELOCATABLE] [--list-columns] [--size REPORT_SIZE]
respaths [respaths ...]

Create an HTML report for one or multiple test results.

**respaths**
   One or multiple wult test result paths.

**-h**
   Show this help message and exit.

**-q**
   Be quiet.

**-d**
   Print debugging information.

**-o** *OUTDIR*, **--outdir** *OUTDIR*
   Path to the directory to store the report at. By default the report
   is stored in the 'wult-report-<reportid>' sub-directory of the
   current working directory, where '<reportid>' is report ID of wult
   test result (the first one if there are multiple).

**--rfilt** *RFILT*
   The row filter: remove all the rows satisfying the filter expression.
   Here is an example of an expression: '(WakeLatency < 10000) \| (PC6%
   < 1)'. This row filter expression will remove all rows with
   'WakeLatency' smaller than 10000 nanoseconds or package C6 residency
   smaller than 1%. The detailed row filter expression syntax can be
   found in the documentation for the 'eval()' function of Python
   'pandas' module. You can use column names in the expression, or the
   special word 'index' for the row number. Value '0' is the header,
   value '1' is the first row, and so on. For example, expression 'index
   >= 10' will get rid of all data rows except for the first 10 ones.

**--rsel** *RSEL*
   The row selector: remove all rows except for those satisfying the
   selector expression. In other words, the selector is just an inverse
   filter: '--rsel expr' is the same as '--rfilt "not (expr)"'.

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
   A comma-separated list of CSV column names (or python style regular
   expressions matching the names) to use on X-axes of the scatter
   plot(s), default is 'SilentTime'. Use '--list-columns' to get the
   list of the available column names. Use value 'none' to disable
   scatter plots.

**-y** *YAXES*, **--yaxes** *YAXES*
   A comma-separated list of CSV column names (or python style regular
   expressions matching the names) to use on the Y-axes for the scatter
   plot(s). If multiple CSV column names are specified for the X- or
   Y-axes, then the report will include multiple scatter plots for all
   the X- and Y-axes combinations. The default is '.*Latency'. Use
   '--list-columns' to get the list of the available column names. se
   value 'none' to disable scatter plots.

**--hist** *HIST*
   A comma-separated list of CSV column names (or python style regular
   expressions matching the names) to add a histogram for, default is
   '.*Latency'. Use '--list-columns' to get the list of the available
   column names. Use value 'none' to disable histograms.

**--chist** *CHIST*
   A comma-separated list of CSV column names (or python style regular
   expressions matching the names) to add a cumulative distribution for,
   default is 'None'. Use '--list-columns' to get the list of the
   available column names. Use value

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

**--title-descr** *TITLE_DESCR*
   The report title description - any text describing this report as
   whole, or path to a file containing the overall report description.
   For example, if the report compares platform A and platform B, the
   description could be something like

**--relocatable** *RELOCATABLE*
   By default the generated report includes references to the raw test
   results, and at the file-system level, the raw test results are
   symlinks pointing to the raw test results directory paths. This means
   that if raw test results are moved somewhere, or the generated report
   is moved to another system, it may end up with broken raw results
   links. This option accepts 3 possible values: 'copy' and 'noraw', and
   'symlink'. In case of the 'copy' value, raw results will be copied to
   the report output directory, which will make the report relocatable,
   but in expense of increased disk space consumption. In case of the
   'noraw' value, the raw results wont be referenced at all, neither in
   the HTML report, nor at the file-system level. This will also exclude
   the logs and the statistics. This option may be useful for minimizing
   the output directory disk space usage. The 'symlink' value
   corresponds to the default behavior.

**--list-columns**
   Print the list of the available column names and exit.

**--size** *REPORT_SIZE*
   Generate HTML report with a pre-defined set of diagrams and
   histograms. This option is mutually exclusive with '--xaxes',
   '--yaxes', '--hist', '--chist', therefore cannot be used in
   combination with any of these options. This option can be set to
   'small', 'medium' or 'large'. Here are the regular expressions for
   each setting: small: {XAXES='SilentTime', YAXES='.*Latency',
   HIST='.*Latency', CHIST='None'} medium: {XAXES='SilentTime',
   YAXES='.*Latency,.*Delay', HIST='.*Latency,.*Delay',
   CHIST='.*Latency'} large: {XAXES='SilentTime,LDist',
   YAXES='.*Latency.*,.*Delay(?!Cyc).*,[PC]C.+%,SilentTime,ReqCState',
   HIST='.*Latency.*,.*Delay(?!Cyc).*,[PC]C.+%,SilentTime,ReqCState,LDist',
   CHIST='.*Latency'}

OPTIONS 'wult filter'
=====================

usage: wult filter [-h] [-q] [-d] [--rfilt RFILT] [--rsel RSEL] [--cfilt
CFILT] [--csel CSEL] [--human-readable] [-o OUTDIR] [--list-columns]
[--reportid REPORTID] respath

Filter datapoints out of a test result by removing CSV rows and columns
according to specified criteria. The criteria is specified using the row
and column filter and selector options ('--rsel', '--cfilt', etc). The
options may be specified multiple times.

**respath**
   The wult test result path to filter.

**-h**
   Show this help message and exit.

**-q**
   Be quiet.

**-d**
   Print debugging information.

**--rfilt** *RFILT*
   The row filter: remove all the rows satisfying the filter expression.
   Here is an example of an expression: '(WakeLatency < 10000) \| (PC6%
   < 1)'. This row filter expression will remove all rows with
   'WakeLatency' smaller than 10000 nanoseconds or package C6 residency
   smaller than 1%. The detailed row filter expression syntax can be
   found in the documentation for the 'eval()' function of Python
   'pandas' module. You can use column names in the expression, or the
   special word 'index' for the row number. Value '0' is the header,
   value '1' is the first row, and so on. For example, expression 'index
   >= 10' will get rid of all data rows except for the first 10 ones.

**--rsel** *RSEL*
   The row selector: remove all rows except for those satisfying the
   selector expression. In other words, the selector is just an inverse
   filter: '--rsel expr' is the same as '--rfilt "not (expr)"'.

**--cfilt** *CFILT*
   The columns filter: remove all column specified in the filter. The
   columns filter is just a comma-separated list of the CSV file column
   names or python style regular expressions matching the names. For
   example expression

**--csel** *CSEL*
   The columns selector: remove all column except for those specified in
   the selector. The syntax is the same as for '--cfilt'.

**--human-readable**
   By default the result 'filter' command print the result as a CSV file
   to the standard output. This option can be used to dump the result in
   a more human-readable form.

**-o** *OUTDIR*, **--outdir** *OUTDIR*
   By default the resulting CSV lines are printed to the standard
   output. But this option can be used to specify the output directly to
   store the result at. This will create a filtered version of the input
   test result.

**--list-columns**
   Print the list of the available column names and exit.

**--reportid** *REPORTID*
   Report ID of the filtered version of the result (can only be used
   with '--outdir').

OPTIONS 'wult calc'
===================

usage: wult calc [-h] [-q] [-d] [--rfilt RFILT] [--rsel RSEL] [--cfilt
CFILT] [--csel CSEL] [-f FUNCS] [--list-funcs] respath

Calculates various summary functions for a wult test result (e.g., the
median value for one of the CSV columns).

**respath**
   The wult test result path to calculate summary functions for.

**-h**
   Show this help message and exit.

**-q**
   Be quiet.

**-d**
   Print debugging information.

**--rfilt** *RFILT*
   The row filter: remove all the rows satisfying the filter expression.
   Here is an example of an expression: '(WakeLatency < 10000) \| (PC6%
   < 1)'. This row filter expression will remove all rows with
   'WakeLatency' smaller than 10000 nanoseconds or package C6 residency
   smaller than 1%. The detailed row filter expression syntax can be
   found in the documentation for the 'eval()' function of Python
   'pandas' module. You can use column names in the expression, or the
   special word 'index' for the row number. Value '0' is the header,
   value '1' is the first row, and so on. For example, expression 'index
   >= 10' will get rid of all data rows except for the first 10 ones.

**--rsel** *RSEL*
   The row selector: remove all rows except for those satisfying the
   selector expression. In other words, the selector is just an inverse
   filter: '--rsel expr' is the same as '--rfilt "not (expr)"'.

**--cfilt** *CFILT*
   The columns filter: remove all column specified in the filter. The
   columns filter is just a comma-separated list of the CSV file column
   names or python style regular expressions matching the names. For
   example expression

**--csel** *CSEL*
   The columns selector: remove all column except for those specified in
   the selector. The syntax is the same as for '--cfilt'.

**-f** *FUNCS*, **--funcs** *FUNCS*
   Comma-separated list of summary functions to calculate. By default
   all generally interesting functions are calculated (each column name
   is associated with a list of functions that make sense for this
   column). Use '--list-funcs' to get the list of supported functions.

**--list-funcs**
   Print the list of the available summary functions.

AUTHORS
=======

**wult** was written by Artem Bityutskiy <dedekind1@gmail.com>.

DISTRIBUTION
============

The latest version of wult may be downloaded from
` <https://github.com/intel/wult>`__
