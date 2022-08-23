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

    with ToolsCommon.get_pman(args) as pman:
        ksrc = getattr(args, "ksrc", None)
        rebuild_bpf = getattr(args, "rebuild_bpf", None)
        with Deploy.Deploy(args.toolname, args.deploy_info, pman=pman, ksrc=ksrc,
                           lbuild=args.lbuild, rebuild_bpf=rebuild_bpf,
                           tmpdir_path=args.tmpdir_path, keep_tmpdir=args.keep_tmpdir,
                           debug=args.debug) as depl:
            depl.deploy()
