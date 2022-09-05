# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""
Serve a report directory on localhost.

Wult HTML reports can't be viewed locally due to restrictions imposed by web-browsers which prevent
them from reading report files. To solve this issue, the files must be hosted as a web-server.
Hence, this script was created so that it can be used to view wult HTML reports. Intended usage:
 1. Place this script in the same directory as a report.
 2. Run this script. Following this, the script opens the default browser at 'localhost:8000'.
"""

# pylint: disable=wrong-import-position
import sys

if sys.version_info < (3,5):
    raise Exception("This script requires Python 3.5 or higher.")

import argparse
import http.server
import os
import webbrowser

# Serve the directory containing the report and this script.
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

def parseargs():
    """Configure an argument parser and parse user arguments."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", nargs="?", default=8000, type=int,
        help="Port to serve the report on. Defaults to '8080'.")
    return parser.parse_args()

def servedir(port=8000):
    """Serve 'DIRECTORY' locally on 'PORT'."""

    # Providing a directory to 'SimpleHTTPRequestHandler' was not supported until Python 3.7.
    # To make this script compatible with Python 3.5+, use 'os.chdir()' as a workaround.
    os.chdir(DIRECTORY)

    server_address = ('', port)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    URL = "http://localhost:{port}/".format(port=port)

    print("Serving directory '{dir}' at '{url}'.".format(dir=DIRECTORY, url=URL))
    print("Opening in browser. Please close this window when you have finished viewing reports.\n")
    print("Web server logs:")

    # Open the user's web browser with the directory open.
    webbrowser.open(URL)
    httpd.serve_forever()


if __name__ == "__main__":
    args = parseargs()
    servedir(args.port)
