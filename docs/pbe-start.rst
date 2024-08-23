===
PBE
===

:Date: 2024-05-28

.. contents::
   :depth: 3
..

COMMAND *'pbe* start'
=====================

usage: pbe start [-h] [-q] [-d] [-H HOSTNAME] [-U USERNAME] [-K PRIVKEY]
[-T TIMEOUT] [-l LDIST] [-S LDIST_STEP] [--span SPAN]
[--warmup WARMUP] [-o OUTDIR] [--reportid REPORTID] [--report]

Start measuring C-states power break even.

OPTIONS *'pbe* start'
=====================

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

**-w** *LDIST*, **--ldist** *LDIST*
   The launch distance range to go through. The default range is
   [10us,10ms], but you can override it with this option by specifying a
   comma-separated range. The default unit is microseconds, but you can
   use the following specifiers as well: ms - milliseconds, us -
   microseconds, ns - nanoseconds. For example, '--ldist 20us,1ms'
   would be a [20,1000] microseconds range.

**-S** *LDIST_STEP*, **--ldist-step** *LDIST_STEP*
   The launch distance step. By default it is 1%. You can specify a percent
   value or an absolute time value. In the latter case, you can use one
   of the following specifiers: ms - milliseconds, us - microseconds, ns
   - nanoseconds. For example, '--ldist-step=1ms' means that launch
   distance will be incremented by 1 millisecond on every iteration. If no
   unit was specified, microseconds are assumed.

**--span** *SPAN*
   For how long a single launch distance value should be measured. By
   default, it is 1 minute. Specify time value in minutes, or use one of
   the following specifiers: d - days, h - hours, m - minutes, s -
   seconds.

**--warmup** *WARMUP*
   When this tool starts measuring a new launch distance value, first it
   lets the system "warm up" for some amount of time, and starts
   collecting the data (e.g., power) only after the warm up period. This
   allows the system to get into the "steady state" (e.g., fans speed
   and CPU temperature stabilizes). By default, the warm up period is 1
   minute. Specify a value in minutes, or use one of the following
   specifiers: d - days, h - hours, m - minutes, s - seconds.

**-o** *OUTDIR*, **--outdir** *OUTDIR*
   Path to the directory to store the results at.

**--stats** *STATS*
   Comma-separated list of statistics to collect. The statistics are
   collected in parallel with power break-even data collection. They are stored
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
   Print information about the statistics 'pbe' can collect and exit.

**--reportid** *REPORTID*
   Any string which may serve as an identifier of this run. By default
   report ID is the current date, prefixed with the remote host name in
   case the '-H' option was used: [hostname-]YYYYMMDD. For example,
   "20150323" is a report ID for a run made on March 23, 2015. The
   allowed characters are: ACSII alphanumeric, '-', '.', ',', '\_', '~',
   and ':'.

**--report**
   Generate an HTML report for collected results (same as calling
   'report' command with default arguments).

**--lead-cpu**
   The lead CPU. This is the CPU that will set timers and send interrupts
   to all other CPUs to wake them when the timers expire. The default is CPU 0.
