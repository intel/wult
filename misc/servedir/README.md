# Viewing Reports Locally
If you wish to view this report locally, such as by copying the report onto your machine and opening
index.html, you will need to host the report files locally. This is because modern browsers forbid
loading data from local file-systems for security reasons.

To facilitate this, we created a Python script:
* `serve_directory.py` - can be used to serve one or more report directories at the same time or in
                         quick succesion.

> Note that this script requires that Python 3.5 or higher is installed. See below for more
information on both.

## Serve a Directory (`serve_directory.py`)
This script can be found in the root directory of wult HTML reports and can be used to view multiple
reports at the same time. Intended usage is as follows:

1. Run the script (e.g. by double-clicking on it in Windows Explorer).
2. Select a directory containing multiple reports when prompted to select a directory. Following
   this, the script opens the default browser at 'localhost:8000'.
3. Once you have finished browsing the reports, make sure to stop the script you started in step 1.
   If a new terminal window was created when you ran the script in step 1, you can do this by
   closing this window.

## CLI-Usage
Note that the script mentioned above can be used on the command-line. Use the '-h' (help) option to
see a list of other options which can be used with each script.