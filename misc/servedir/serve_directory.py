# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Adam Hawley <adam.james.hawley@intel.com>

"""
Serve a directory as a web-server.

This script exists so that users can serve report directories as web-servers as to make them easier
to navigate and browse.
"""

# pylint: disable=wrong-import-position
import sys

if sys.version_info < (3,5):
    raise Exception("This script requires Python 3.5 or higher.")

import argparse
import http.server
import os

failed_tk_import = False
try:
    import tkinter
    from tkinter.filedialog import askdirectory
except ModuleNotFoundError:
    failed_tk_import = True

# This script is intended to work with Python 3.5 and higher. F-strings were introduced in
# Python 3.6, therefore we do not want to use them to maintain the compatibility.
# pylint: disable=consider-using-f-string

def parseargs():
    """Configure an argument parser and parse user arguments."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", nargs="?", default="localhost",
                        help="Host to serve the report on. Defaults to 'localhost'.")
    parser.add_argument("--port", nargs="?", default=8000, type=int,
                        help="Port to serve the report on. Defaults to '8080'.")
    parser.add_argument("--dir", nargs="?", default=None,
                        help="Specify a directory to host. If one is not specified, the user will "
                             "be prompted for one using a GUI.")
    _args = parser.parse_args()

    if failed_tk_import and _args.dir is None:
        raise Exception("failed to import tkinter. Use the '--dir' option to specify a directory "
                        "or install tkinter.")

    return _args

def _init_server(host, port, portcount=10):
    """
    Tries to initialise an 'http.server.HTTPServer' on 'host':'port'. If unsuccessful on 'port',
    cycles through 'portcount' other ports until it succeeds or raises an error.

    Returns a tuple in the format '(httpd, port)' where 'httpd' is a 'http.server.HTTPServer'
    instance and 'port' is the integer representation of the successful port.
    """

    serverinit = False
    initport = port

    while not serverinit:
        try:
            server_address = (host, port)
            httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
            serverinit = True
        except OSError as err:
            print("Failed to create HTTP server at port '{port}': {err}".format(port=port, err=err))
            port += 1

            if port - initport >= portcount:
                raise Exception("unable to create HTTP server, tried ports in range "
                                "{iport}-{port}.".format(iport=initport, port=port-1)) from None

            print("Trying again with port '{port}'.".format(port=port))

    return httpd, port

def servedir(host="localhost", port=8000, directory=None):
    """
    Serve 'directory' on 'host:port'. Default behaviour is as follows:
     1. Prompts the user for a directory using a GUI.
     2. Tries to serve this directory on 'localhost:8000'.
    """

    if directory is None:
        try:
            directory = askdirectory()
        except tkinter.TclError as err:
            raise Exception("unable to create GUI for directory selection. You can specify the "
                            "directory with '--dir' to avoid the graphical interface.") from err

    # Providing a directory to 'SimpleHTTPRequestHandler' was not supported until Python 3.7.
    # To make this script compatible with Python 3.5+, use 'os.chdir()' as a workaround.
    os.chdir(directory)

    httpd, port = _init_server(host, port)
    URL = "http://{host}:{port}/".format(host=host, port=port)

    print("Serving directory '{dir}' at '{url}'.".format(dir=directory, url=URL))
    print("Please close this window when you have finished viewing reports.\n")
    print("Web server logs:")

    httpd.serve_forever()


if __name__ == "__main__":
    args = parseargs()
    servedir(args.host, args.port, args.dir)
