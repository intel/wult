# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Miscellaneous helper functions shared by various tools and modules.
"""

import logging
from collections import OrderedDict
from pathlib import Path
from wultlibs.helperlibs import Procs, SSH, Trivial
from wultlibs.helperlibs.Exceptions import Error

_LOG = logging.getLogger("main")

def get_proc(args, hostname):
    """
    Returns and "SSH" object or the 'Procs' object depending on 'hostname'.
    """

    if hostname == "localhost":
        return Procs.Proc()

    return SSH.SSH(hostname=hostname, username=args.username, privkeypath=args.privkey,
                   timeout=args.timeout)

def add_ssh_options(parser, argcomplete=None):
    """
    Add the '--host', '--timeout' and other SSH-related options to argument parser object 'parser'.
    """

    text = "Name of the host to run on (default is the local host)."
    parser.add_argument("-H", "--host", help=text, default="localhost", dest="hostname")
    text = """Name of the user to use for logging into the remote host over SSH. The default user
              name is 'root'."""
    parser.add_argument("-U", "--username", dest="username", default="root", metavar="USERNAME",
                        help=text)
    text = """Path to the private SSH key that should be used for logging into the SUT. By default
              the key is automatically found from standard paths like '~/.ssh'."""
    arg = parser.add_argument("-K", "--priv-key", dest="privkey", type=Path, help=text)
    if argcomplete:
        arg.completer = argcomplete.completers.FilesCompleter()
    text = """SSH connect timeout in seconds, default is 8."""
    parser.add_argument("-T", "--timeout", default=8, help=text)

def get_dpcnt(res, dpcnt):
    """
    This helper function validates number of datapoints the user requested to collect ('dpcnt'). It
    also looks at how many datapoints are already present in the 'res' object (represents a raw test
    result) and returns the number datapoints to collect in order for 'rest' to end up with 'dpcnt'
    datapoints.
    """

    if not Trivial.is_int(dpcnt) or int(dpcnt) <= 0:
        raise Error(f"bad datapoints count '{dpcnt}', should be a positive integer")

    dpcnt = int(dpcnt) - res.csv.initial_rows_cnt
    if dpcnt <= 0:
        _LOG.info("Raw test result at '%s' already includes %d datapoints",
                  res.dirpath, res.csv.initial_rows_cnt)
        _LOG.info("Nothing to collect")
        return 0

    return dpcnt

def even_up_dpcnt(rsts):
    """
    This is a helper function for the '--even-up-datapoints' option. It takes a list of
    'RORawResult' objects ('rsts') and truncates them to the size of the smallest test result, where
    "size" is defined as the count of rows in the CSV file.
    """

    # Find test with the smallest CSV file. It should be a good approximation for the smallest test
    # result, ant it will be corrected as we go.
    min_size = min_res = None
    for res in rsts:
        size = res.dp_path.stat().st_size
        if min_size is None or size < min_size:
            min_size = size
            min_res = res

    min_res.load_df()
    min_dpcnt = len(min_res.df.index)

    # Load only 'min_dpcnt' datapoints for every test result, correcting 'min_dpcnt' as we go.
    for res in rsts:
        res.load_df(nrows=min_dpcnt)
        min_dpcnt = min(min_dpcnt, len(res.df.index))

    # And in case our initial 'min_dpcnt' estimation was incorrect, truncate all the results to the
    # final 'min_dpcnt'.
    for res in rsts:
        dpcnt = len(res.df.index)
        if dpcnt > min_dpcnt:
            res.df = res.df.truncate(after=min_dpcnt-1)

def apply_filters(args, res):
    """
    This is a helper function for the following command-line options: '--rsel', '--rfilt', '--csel',
    '--cfilt'. The 'args' argument should be an 'helperlibs.ArgParse' object, where all the above
    mentioned options are represented by the 'oargs' (ordered arguments) field. The 'res' argument
    is a 'RORawResult' object.
    """

    def do_filter(res, ops):
        """Apply the reduction operations in 'ops' to wult test result 'res'."""

        res.clear_filts()
        for name, expr in ops.items():
            if name.startswith("c"):
                expr = Trivial.split_csv_line(expr)
            getattr(res, f"set_{name}")(expr)
        res.load_df()

    if not getattr(args, "oargs", None):
        return

    ops = OrderedDict()
    for name, expr in args.oargs:
        if name in ops:
            do_filter(res, ops)
            ops = OrderedDict()
        ops[name] = expr

    if ops:
        do_filter(res, ops)
