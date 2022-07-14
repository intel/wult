# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module includes the "deploy" 'wult' command implementation.
"""

from wultlibs import Deploy, ToolsCommon

def deploy_command(args):
    """Implements the 'deploy' command."""

    with ToolsCommon.get_pman(args) as pman, \
         Deploy.Deploy(args.toolname, pman=pman, ksrc=args.ksrc,
                lbuild=args.lbuild, debug=args.debug) as depl:
        depl.deploy()
