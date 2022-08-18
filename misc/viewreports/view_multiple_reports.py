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
import webbrowser
from tkinter.filedialog import askdirectory

PORT = 8000

DIRECTORY = askdirectory()

class Handler(http.server.SimpleHTTPRequestHandler):
    """
    This class inherits from 'http.server.SimpleHTTPRequestHandler' and defines the directory to
    serve based on the directory chosen by the user.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def servedir():
    """Serve 'DIRECTORY' locally on 'PORT'."""

    server_address = ('', PORT,)
    httpd = http.server.HTTPServer(server_address, Handler)
    URL = "http://localhost:{port}/".format(port=PORT)

    print("Serving directory '{dir}' at '{url}'.".format(dir=DIRECTORY, url=URL))
    print("Opening in browser. Please close this window when you have finished viewing reports.\n")
    print("Web server logs:")

    # Open the user's web browser with the directory open.
    webbrowser.open(URL)
    httpd.serve_forever()


if __name__ == "__main__":
    servedir()
