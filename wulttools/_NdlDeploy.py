# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module includes the "deploy" 'ndl' command implementation.
"""

import logging
from pepclibs.helperlibs.Exceptions import Error
from wulttools import _Common
from wultlibs.deploylibs import _Deploy

_LOG = logging.getLogger()

def deploy_command(args):
    """Implements the 'deploy' command."""

    try:
        _Common.run_stats_collect_deploy(args)
    except Error as err:
        _LOG.warning(err)
        _LOG.notice(f"the statistics collection capability will not be available for "
                    f"'{args.toolname}'")

    with _Common.get_pman(args) as pman:
        with _Deploy.Deploy(args.toolname, args.deploy_info, pman=pman, ksrc=args.ksrc,
                            lbuild=args.lbuild, tmpdir_path=args.tmpdir_path,
                            keep_tmpdir=args.keep_tmpdir, debug=args.debug) as depl:
            depl.deploy()
