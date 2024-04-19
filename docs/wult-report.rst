====
WULT
====

:Date: 2024-03-08
:Title: REPORT

.. contents::
   :depth: 3
..

=======================
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
