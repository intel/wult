# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2016-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module contains common bits and pieces shared between different modules in this package. Not
supposed to be imported directly by users.
"""

import re
import logging
from collections import namedtuple
from wultlibs.helperlibs import Human

_LOG = logging.getLogger()

# The default command timeout in seconds
TIMEOUT = 4 * 60 * 60

# Results of a the process execution.
ProcResult = namedtuple("proc_result", ["stdout", "stderr", "exitcode"])

def cmd_failed_msg(command, stdout, stderr, exitcode, hostname=None, startmsg=None, timeout=None):
    """
    This helper function formats an error message for a failed command 'command'. The 'stdout' and
    'stderr' arguments are what the command printed to the standard output and error streams, and
    'exitcode' is the exit status of the failed command. The 'hostname' parameter is ignored and it
    is here only for the sake of keeping the 'Procs' API look sililar to the 'SSH' API. The
    'startmsg' parameter can be used to specify the start of the error message. The 'timeout'
    argument specifies the command timeout.
    """

    if not isinstance(command, str):
        # Sometimes commands are represented by a list of command components - join it.
        command = " ".join(command)

    if timeout is None:
        timeout = TIMEOUT
    elif timeout == -1:
        timeout = None

    if exitcode is not None:
        exitcode_msg = "failed with exit code %s" % exitcode
    elif timeout is not None:
        exitcode_msg = "did not finish within %s seconds (%s)" \
                       % (timeout, Human.duration(timeout))
    else:
        exitcode_msg = "failed, but no exit code is available, this is a bug!"

    msg = ""
    for stream in (stdout, stderr):
        if not stream:
            continue
        if isinstance(stream, list):
            stream = "".join(stream)
        msg += "%s\n" % stream.strip()

    if not startmsg:
        if hostname:
            startmsg = "ran the following command on host '%s', but it %s" \
                        % (hostname, exitcode_msg)
        else:
            startmsg = "the following command %s:" % exitcode_msg

    result = "%s\n%s" % (startmsg, command)
    if msg:
        result += "\n\n%s" % msg.strip()
    return result

def extract_full_lines(text):
    """
    Extract full lines from string 'text'. Return a tuple containing 2 elements - the full lines and
    the last partial line.
    """

    full, partial = [], ""
    for line_match in re.finditer("(.*\n)|(.+$)", text):
        if line_match.group(2):
            partial = line_match.group(2)
            break
        full.append(line_match.group(1))

    return (full, partial)
