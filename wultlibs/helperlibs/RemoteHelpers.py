# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module contains misc. helper functions that can be transparently used on local and remote
systems.
"""

import time
import socket

def time_time(proc=None):
    """
    Same as standard pytohn 'time.time()' function - returns time since epoch on the host defined by
    'proc' (local host by default).
    """

    if not proc or not proc.is_remote:
        return time.time()
    return float(proc.run_verify("date +%s")[0].strip())

def get_free_port(port_type=None, proc=None):
    """
    Return free TCP port. The 'port_type' parameter can be used to specify port type, the default
    is a 'SOCK_STREAM' (TCP) port. If 'proc' is specified, the given proc object will be used to
    fetch a free port number.

    By default this function operates on the local host, but the 'proc' argument can be used to pass
    a connected 'SSH' object in which case this function will operate on the remote host.
    """


    if not port_type:
        port_type = socket.SOCK_STREAM

    if proc:
        cmd = f"python -c 'import socket;" \
              f"sock = socket.socket({socket.AF_INET}, {port_type});" \
              f"sock.bind((\"\", 0));" \
              f"port = sock.getsockname()[1];" \
              f"sock.close();" \
              f"print(port)'"
        return int(proc.run_verify(cmd, capture_output=True)[0])

    sock = socket.socket(socket.AF_INET, port_type)
    sock.bind(("", 0))
    port = sock.getsockname()[1]
    sock.close()

    return port
