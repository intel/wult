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
[-T TIMEOUT] [-w WAKEPERIOD] [-S WAKEPERIOD_STEP] [--span SPAN]
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

**-w** *WAKEPERIOD*, **--wakeperiod** *WAKEPERIOD*
   The wake period range to go through. The default range is
   [10us,10ms], but you can override it with this option by specifying a
   comma- separated range. The default unit is microseconds, but you can
   use the following specifiers as well: ms - milliseconds, us -
   microseconds, ns - nanoseconds. For example, '--wakeperiod 20us,1ms'
   would be a [20,1000] microseconds range.

**-S** *WAKEPERIOD_STEP*, **--wakeperiod-step** *WAKEPERIOD_STEP*
   The wake period step. By default it is 1%. You can specify a percent
   value or an absolute time value. In the latter case, you can use one
   of the following specifiers: ms - milliseconds, us - microseconds, ns
   - nanoseconds. For example, '--wakeperiod-step=1ms' means that wake
   period will be incremented by 1 millisecond on every iteration. If no
   unit was specified, microseconds are assumed.

**--span** *SPAN*
   For how long a single wake period value should be measured. By
   default, it is 1 minute. Specify time value in minutes, or use one of
   the following specifiers: d - days, h - hours, m - minutes, s -
   seconds.

**--warmup** *WARMUP*
   When this tool starts measuring a new wake period value, first it
   lets the system "warm up" for some amount of time, and starts
   collecting the data (e.g., power) only after the warm up period. This
   allows the system to get into the "steady state" (e.g., fans speed
   and CPU temperature stabilizes). By default, the warm up period is 1
   minute. Specify a value in minutes, or use one of the following
   specifiers: d - days, h - hours, m - minutes, s - seconds.

**-o** *OUTDIR*, **--outdir** *OUTDIR*
   Path to the directory to store the results at.

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
