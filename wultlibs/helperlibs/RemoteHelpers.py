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

def time_time(pman=None):
    """
    Same as standard pytohn 'time.time()' function - returns time since epoch on the host defined by
    'pman' (local host by default).
    """

    if not pman or not pman.is_remote:
        return time.time()
    return float(pman.run_verify("date +%s")[0].strip())

def get_free_port(port_type=None, pman=None):
    """
    Returns afree TCP port. The 'port_type' parameter can be used to specify port type, the default
    is a 'SOCK_STREAM' (TCP) port. The 'pman' argument defines the system to get the free port
    number on.
    """


    if not port_type:
        port_type = socket.SOCK_STREAM

    if pman:
        python_path = pman.get_python_path()
        cmd = f"{python_path} -c 'import socket;" \
              f"sock = socket.socket({socket.AF_INET}, {port_type});" \
              f"sock.bind((\"\", 0));" \
              f"port = sock.getsockname()[1];" \
              f"sock.close();" \
              f"print(port)'"
        return int(pman.run_verify(cmd, capture_output=True)[0])

    sock = socket.socket(socket.AF_INET, port_type)
    sock.bind(("", 0))
    port = sock.getsockname()[1]
    sock.close()

    return port
