# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module includes the "deploy" 'stats-collect' command implementation.
"""

from statscollectlibs import Deploy, ToolsCommon

def deploy_command(args):
    """Implements the 'deploy' command."""

    with ToolsCommon.get_pman(args) as pman:
        with Deploy.Deploy(args.toolname, args.deploy_info, pman, args.lbuild, args.tmpdir_path,
                           args.keep_tmpdir, args.debug) as depl:
            depl.deploy()
