# Viewing Reports Locally
If you wish to view this report locally, this can be done using two methods:
* `serve_directory.py` - a Python script found in the report directory which can be used to
                         serve one or more report directories (see usage details below).
* `index.html` - an HTML document found in the report directory which attempts to render the
                 report in a web browser. If it fails due to browser restrictions, you will be
                 prompted to upload the report directory.

## Serve a Directory (`serve_directory.py`)
> Note that this script requires that Python 3.5 or higher is installed.

This script can be found in the root directory of HTML reports and can be used to view one or
more reports at the same time.

### GUI Usage
Intended GUI usage is as follows:

1. Run the script (e.g. by double-clicking on it in Windows Explorer).
2. Select a directory containing one or more reports when prompted to select a directory. Following
   this, browse to the URL output by the script using a web-browser.
3. Once you have finished browsing the reports, make sure to stop the script you started in step 1.
   If a new terminal window was created when you ran the script in step 1, you can do this by
   closing this window.

### Command-Line (CLI) Usage
The script can also be used on the command line. Use the '--dir' option to specify the directory
which should be served.

> If the '--dir' option is not used, the script will attempt to open a graphical file browser so
that you can choose the directory. Therefore '--dir' is required if a graphical interface is not available.

Use the '-h' (help) option to see a list of other options which can be used.
