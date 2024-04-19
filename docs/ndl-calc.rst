===
NDL
===

:Date: 2024-03-08

.. contents::
   :depth: 3
..

=====================
COMMAND *'ndl* calc'
====================

usage: ndl calc [-h] [-q] [-d] [--exclude EXCLUDE] [--include INCLUDE]
[--exclude-metrics MEXCLUDE] [--include-metrics MINCLUDE] [-f FUNCS]
[--list-funcs] [--list-metrics] [respath]

Calculates various summary functions for a ndl test result (e.g., the
median value for one of the CSV columns).

**respath**
   The ndl test result path to calculate summary functions for.

OPTIONS *'ndl* calc'
====================

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
