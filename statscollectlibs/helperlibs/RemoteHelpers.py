# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2020-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module contains misc. helper functions that can be transparently used on local and remote
systems.
"""

import socket

def get_free_port(port_type=None, pman=None):
    """
    Returns a free TCP port. The 'port_type' parameter can be used to specify port type, the default
    is a 'SOCK_STREAM' (TCP) port. The 'pman' argument defines the system to get the free port
    number on.
    """

    if not port_type:
        port_type = socket.SOCK_STREAM

    if pman:
        python_path = pman.get_python_path()
        cmd = f"{python_path} -c 'import socket;" \
              f"sock = socket.socket({socket.AF_INET}, {port_type});" \
              f"sock.bind((\"localhost\", 0));" \
              f"port = sock.getsockname()[1];" \
              f"sock.close();" \
              f"print(port)'"
        return int(pman.run_verify(cmd, capture_output=True)[0])

    sock = socket.socket(socket.AF_INET, port_type)
    sock.bind(("localhost", 0))
    port = sock.getsockname()[1]
    sock.close()

    return port
