====
WULT
====

:Date: 2024-03-08
:Title: START

.. contents::
   :depth: 3
..

COMMAND *'wult* start'
======================

usage: wult start [-h] [-q] [-d] [-H HOSTNAME] [-U USERNAME] [-K PRIVKEY]
[-T TIMEOUT] [-c COUNT] [--time-limit LIMIT] [--exclude EXCLUDE]
[--include INCLUDE] [--keep-filtered] [-o OUTDIR] [--reportid REPORTID]
[--stats STATS] [--stats-intervals STATS_INTERVALS] [--list-stats]
[-l LDIST] [--cpu CPU] [--tsc-cal-time TSC_CAL_TIME]
[--keep-raw-data] [--no-unload] [--report] [--force]
[--freq-noise FREQ_NOISE] [--freq-noise-sleep FREQ_NOISE_SLEEP] devid

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
   allowed characters are: ACSII alphanumeric, '-', '.', ',', '\_', '~',
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
   more information about available statistics.

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

**--cpu** *CPU*
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

**--report**
   Generate an HTML report for collected results (same as calling
   'report' command with default arguments).

**--force**
   By default a network card is not accepted as a measurement device if
   it is used by a Linux network interface and the interface is in an
   active state, such as "up". Use '--force' to disable this safety
   mechanism. Use it with caution.

**--freq-noise** *FREQ_NOISE*
   Add frequency scaling noise to the measured system. This runs a
   background process that repeatedly modifies CPU or uncore frequencies
   for given domains. The reason for doing this is because frequency
   scaling is generally an expensive operation and is known to impact
   system latency. 'FREQ_NOISE' is specified as 'TYPE:ID:MIN:MAX',
   where: TYPE should be 'cpu' or 'uncore', specifies whether CPU or
   uncore frequency should be modified; ID is either CPU number or
   uncore domain ID to modify the frequency for (e.g. 'cpu:12:...' would
   target CPU12); MIN is the minimum CPU/uncore frequency value; MAX is
   the maximum CPU/uncore frequency value. For example, to add frequency
   scaling noise for CPU0, add '-- freq-noise cpu:0:min:max'. To add
   uncore frequency noise for uncore domain 0, add '--freq-noise
   uncore:0:min:max'. The parameter can be added multiple times to
   specify multiple frequency noise domains.

**--freq-noise-sleep** *FREQ_NOISE_SLEEP*
   Sleep between frequency noise operations. This time is added between
   every frequency scaling operation executed by the 'freq-noise'
   feature. The default time unit is microseconds, but it is possible to
   use time specifiers as well, ms - milliseconds, us - microseconds, ns
   - nanoseconds. Default sleep time is 50ms.
