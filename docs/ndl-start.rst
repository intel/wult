===
NDL
===

:Date: 2024-03-08

.. contents::
   :depth: 3
..

=====================
COMMAND *'ndl* start'
=====================

usage: ndl start [-h] [-q] [-d] [-H HOSTNAME] [-U USERNAME] [-K PRIVKEY]
[-T TIMEOUT] [-c COUNT] [--time-limit LIMIT] [-o OUTDIR]
[--reportid REPORTID] [--stats STATS] [--stats-intervals STATS_INTERVALS]
[--list-stats] [-l LDIST] [--cpu CPU] [--exclude EXCLUDE]
[--include INCLUDE] [--keep-filtered] [--report] [--force]
[--trash-cpu-cache] ifname

Start measuring and recording the latency data.

**ifname**
   The network interface backed by the NIC to use for latency
   measurements. Today only Intel I210 and I211 NICs are supported.
   Please, specify NIC's network interface name (e.g., eth0).

OPTIONS *'ndl* start'
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
   Print information about the statistics 'ndl' can collect and exit.

**-l** *LDIST*, **--ldist** *LDIST*
   The launch distance in microseconds. This tool works by scheduling a
   delayed network packet, then sleeping and waiting for the packet to
   be sent. This step is referred to as a "measurement cycle" and it is
   usually repeated many times. The launch distance defines how far in
   the future the delayed network packets are scheduled. By default this
   tool randomly selects launch distance in range of [5000, 50000]
   microseconds (same as '--ldist 5000,50000'). Specify a comma-
   separated range or a single value if you want launch distance to be
   precisely that value all the time. The default unit is microseconds,
   but you can use the following specifiers as well: ms - milliseconds,
   us - microseconds, ns - nanoseconds. For example, '--ldist
   500us,100ms' would be a [500,100000] microseconds range. Note, too
   low values may cause failures or prevent the SUT from reaching deep
   C-states. The optimal value is system-specific.

**--cpu** *CPU*
   The CPU number to bind the helper to. The helper will use this CPU to
   send delayed packets. In normal conditions this means that network
   packet buffers will be allocated on the NUMA node local to the CPU,
   but not necessarily local to the network card. Use this option to
   measure different packet memory locations on a NUMA system. Special
   value 'local' can be used to specify a CPU with lowest CPU number
   local to the NIC, and this is the default value.a Special value

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
   to collect 100000 datapoints where RTD is greater than 50
   microseconds. In this case, you can use these options: -c 100000
   --exclude="RTD > 50". The result will contain 100000 datapoints, all
   of them will have RTD bigger than 50 microseconds. But what if you do
   not want to simply discard the other datapoints, because they are
   also interesting? Well, add the '--keep-filtered' option. The result
   will contain, say, 150000 datapoints, 100000 of which will have RTD
   value greater than 50.

**--report**
   Generate an HTML report for collected results (same as calling
   'report' command with default arguments).

**--force**
   By default a network card is not accepted as a measurement device if
   it is used by a Linux network interface and the interface is in an
   active state, such as "up". Use '--force' to disable this safety
   mechanism. Use it with caution.

**--trash-cpu-cache**
   Trash CPU cache to make sure NIC accesses memory when measuring
   latency. Without this option, there is a change the data NIC accesses
   is in a CPU cache. With this option, ndl allocates a buffer and fills
   it with data every time a delayed packet is scheduled. Supposedly,
   this should push out cached data to the memory. By default, the CPU
   cache trashing buffer size a sum of sizes of all caches on all CPUs
   (includes all levels, excludes instruction cache).
