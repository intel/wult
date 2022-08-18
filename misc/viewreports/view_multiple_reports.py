# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""
Serve a local directory on localhost.

Wult HTML reports can't be viewed locally due to restrictions imposed by web-browsers which prevent
them from reading report files. To solve this issue, the files must be hosted as a web-server.
Hence, this script was created so that it can be used to view wult HTML reports. Intended usage:
 1. Run this script.
 2. Select the report directory or a directory containing multiple reports when prompted to select
    one. Following this, the script opens the default browser at 'localhost:8000'.
"""

import http.server
import os
import webbrowser
from tkinter.filedialog import askdirectory

PORT = 8000

DIRECTORY = askdirectory()

def servedir():
    """Serve 'DIRECTORY' locally on 'PORT'."""

    server_address = ('', PORT,)

    # Providing a directory to 'SimpleHTTPRequestHandler' was not supported until Python 3.7.
    # To make this script compatible with Python 3.5+, use 'os.chdir()' as a workaround.
    os.chdir(DIRECTORY)

    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    URL = "http://localhost:{port}/".format(port=PORT)

    print("Serving directory '{dir}' at '{url}'.".format(dir=DIRECTORY, url=URL))
    print("Opening in browser. Please close this window when you have finished viewing reports.\n")
    print("Web server logs:")

    # Open the user's web browser with the directory open.
    webbrowser.open(URL)
    httpd.serve_forever()


if __name__ == "__main__":
    servedir()
