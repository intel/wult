# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module includes the "deploy" 'pbe' command implementation.
"""

from wultlibs.deploy import _Deploy
from wulttools import _Common

def deploy_command(args):
    """Implements the 'deploy' command."""

    with _Common.get_pman(args) as pman:
        ksrc = getattr(args, "ksrc", None)
        drv_make_opts = getattr(args, "drv_make_opts", None)
        with _Deploy.Deploy(args.toolname, args.deploy_info, pman=pman, ksrc=ksrc,
                            lbuild=args.lbuild, drv_make_opts=drv_make_opts,
                            tmpdir_path=args.tmpdir_path, keep_tmpdir=args.keep_tmpdir,
                            debug=args.debug) as depl:
            depl.deploy()
