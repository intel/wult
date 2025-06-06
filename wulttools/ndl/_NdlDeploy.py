# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module includes the "deploy" 'ndl' command implementation.
"""

from wulttools import _Common
from wultlibs.deploy import _Deploy

def deploy_command(args):
    """Implements the 'deploy' command."""

    with _Common.get_pman(args) as pman:
        drv_make_opts = getattr(args, "drv_make_opts", None)

        with _Deploy.Deploy(args.toolname, args.deploy_info, pman=pman, ksrc=args.ksrc,
                            lbuild=args.lbuild, tmpdir_path=args.tmpdir_path,
                            drv_make_opts=drv_make_opts, keep_tmpdir=args.keep_tmpdir,
                            debug=args.debug) as depl:
            depl.deploy()

        _Common.run_stats_collect_deploy(args, pman)
