============
EXERCISE-SUT
============

:Date: 2024-03-08

.. contents::
   :depth: 3
..

===============================
COMMAND *'exercise-sut* report'
===============================

usage: exercise-sut report [-h] [-q] [-d] [--diffs DIFFS] [--include
INCLUDE] [--exclude EXCLUDE] [--jobs JOBS] [--toolpath TOOLPATH]
[--toolopts TOOLOPTS] [--outdir OUTDIR] [--stop-on-failure] [--dry-run]
[--list-monikers] [respaths ...]

Generate reports from collected data.

**respaths**
   One or multiple paths to be searched for test results.

OPTIONS *'exercise-sut* report'
===============================

**-h**
   Show this help message and exit.

**-q**
   Be quiet.

**-d**
   Print debugging information.

**--diffs** *DIFFS*
   Collected data is stored in directories, and each directory name is
   constructed from multiple monikers separated by dashes, e.g.
   'hrt-c6-uf_max-autoc1e_off'. This option can be used to create diff
   reports by including multiple results in one report. Comma-separated
   list of monikers to select results to include in the diff report.
   This option can be used multiple times. If this option is not
   provided, reports with single result are generated.

**--include** *INCLUDE*
   Comma-separated list of monikers that must be found from the result
   path name.

**--exclude** *EXCLUDE*
   Comma-separated list of monikers that must not be found from the
   result path name.

**--jobs** *JOBS*, **-j** *JOBS*
   Number of threads to use for generating reports with.

**--toolpath** *TOOLPATH*
   By default, name of the report tool is resolved from the results.
   This option can be used to override the tool.

**--toolopts** *TOOLOPTS*
   Additional options to use for running the tool. String "{REPORTID}"
   in TOOLOPTS will be replaced with the report ID.

**--outdir** *OUTDIR*, **-o** *OUTDIR*
   Path to directory to store the results at. Default is
   <toolname-date-time>.

**--stop-on-failure**
   Stop if any of the steps fail, instead of continuing (default).

**--dry-run**
   Do not run any commands, only print them.

**--list-monikers**
   A moniker is an abbreviation for a setting. The 'exercise-sut' uses
   monikers to create directory names and report IDs for collected
   results. Use this option to list monikers assosiated with each
   settings, if any, and exit.
