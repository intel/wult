# Viewing Reports Locally
If you wish to view this report locally, such as by copying the report onto your machine and opening
index.html, you will need to host the report files locally. This is because modern browsers forbid
loading data from local file-systems for security reasons.

To facilitate this, we created 2 Python scripts:
* `view_report.py` - used to view the report in the same directory as the script itself.
* `view_multiple_reports.py` - used to view multiple reports at the same time or in quick succesion.

> Note that both scripts require that Python 3.5 or higher is installed. See below for more
information on both.

## View one report (`view_report.py`)
The first script found in the root directory of wult HTML reports is 'view_report.py'. This script
can be used to quickly view the report contained in the same directory. Intended usage is as
follows:

1. Run the script (e.g. by double-clicking on it in Windows Explorer). Following this, the script
   opens the default browser at 'localhost:8000'.
2. Once you have finished browsing the report, make sure to stop the script you started in step 1.
   If a new terminal window was created when you ran the script in step 1, you can do this by closing
   this window.

## View multiple reports (`view_multiple_reports.py`)
The second script found in the root directory of wult HTML reports can be used to view multiple
reports at the same time. Intended usage is as follows:

1. Run the script (e.g. by double-clicking on it in Windows Explorer).
2. Select a directory containing multiple reports when prompted to select a directory. Following
   this, the script opens the default browser at 'localhost:8000'.
3. Once you have finished browsing the reports, make sure to stop the script you started in step 1.
   If a new terminal window was created when you ran the script in step 1, you can do this by
   closing this window.