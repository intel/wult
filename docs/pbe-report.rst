===
PBE
===

:Date: 2024-05-28

.. contents::
   :depth: 3
..

COMMAND *'pbe* report'
======================

usage: pbe report [-h] [-q] [-d] [-o OUTDIR] [--reportids REPORTIDS]
[--report-descr REPORT_DESCR] respaths [respaths ...]

Create an HTML report for one or multiple test results.

**respaths**
   One or multiple pbe test result paths.

OPTIONS *'pbe* report'
======================

**-h**
   Show this help message and exit.

**-q**
   Be quiet.

**-d**
   Print debugging information.

**-o** *OUTDIR*, **--outdir** *OUTDIR*
   Path to the directory to store the report at. By default the report
   is stored in the 'pbe-report-<reportid>' sub-directory of the test
   result directory. If there are multiple test results, the report is
   stored in the current directory. The '<reportid>' is report ID of pbe
   test result.

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
   description could be something like 'platform A vs B comparison'.
   This text will be included into the very beginning of the resulting
   HTML report.
