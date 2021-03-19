# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2014-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module contains helpers related to parsing command-line arguments.
"""

import types
import argparse
from wultlibs.helperlibs import DamerauLevenshtein, Trivial
from wultlibs.helperlibs.Exceptions import Error # pylint: disable=unused-import

class OrderedArg(argparse.Action):
    """
    This action implements ordered arguments support. Sometimes the command line arguments order
    matter, and this action can be used to preserve the order. It simply stores all the ordered
    arguments in the 'oargs' attribute, which is a list of '(option, value)' tuples.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        """Append the ordered argument to the 'oargs' attribute."""

        if not getattr(namespace, 'oargs', None):
            setattr(namespace, 'oargs', [])

        # Also add the standard attribute for compatibility.
        setattr(namespace, self.dest, values)

        namespace.oargs.append((self.dest, values))

def _add_parser(subparsers, *args, **kwargs):
    """
    This function overrides the 'add_parser()' method of the 'subparsers' object. The 'subparsers'
    object the action object returned by 'add_subparsers()'. The goal of this function is to remove
    all newlines and extra white-spaces from the "description" keyword argument. Here is an example.

    descr = "Long description\n   With newlines and white-spaces and possibly tabs."
    subpars = subparsers.add_parser("subcommand", help="help", description=descr)

    By default 'argparse' removes those newlines when the help is displayed. However, for some
    reason when we generate man pages out of help text using the 'argparse-manpage' tool, the
    newlines are not removed and the man page looks untidy.

    So basically this is a workaround for that problem. We just override the 'add_parser()' method,
    remove newlines and extra spaces from the description, and call the original 'add_parser()'
    method.
    """

    if "description" in kwargs:
        kwargs["description"] = " ".join(kwargs["description"].split())
    return subparsers.__orig_add_parser(*args, **kwargs) # pylint: disable=protected-access

class ArgsParser(argparse.ArgumentParser):
    """
    This class re-defines the 'error()' method of the 'argparse.ArgumentParser' class in order to
    make it always print a hint about the '-h' option. It also overrides the 'add_argument()' method
    to include the standard options like '-q' and '-d'.
    """

    def __init__(self, *args, **kwargs):
        """
        We assume all tools using this module support the '-q' and '-d' options. This helper adds
        them to the 'parser' argument parser object.
        """

        if "ver" in kwargs:
            version = kwargs["ver"]
            del kwargs["ver"]
        else:
            version = None

        kwargs["add_help"] = False
        super().__init__(*args, **kwargs)

        text = "Show this help message and exit."
        self.add_argument("-h", dest="help", action="help", help=text)
        text = "Be quiet."
        self.add_argument("-q", dest="quiet", action="store_true", help=text)
        text = "Print debugging information."
        self.add_argument("-d", dest="debug", action="store_true", help=text)
        if version:
            text = "Print version and exit."
            self.add_argument("--version", action="version", help=text, version=version)

    def parse_args(self, *args, **kwargs): # pylint: disable=signature-differs
        """Verify that '-d' and '-q' are not used at the same time."""

        args = super().parse_args(*args, **kwargs)

        if args.quiet and args.debug:
            raise Error("-q and -d cannot be used together")

        return args

    def add_subparsers(self, *args, **kwargs):
        """
        Create and return the subparsers action object with a customized 'add_parser()' method.
        Refer to '_add_parser()' for details.
        """

        subparsers = super().add_subparsers(*args, **kwargs)
        setattr(subparsers, "__orig_add_parser", subparsers.add_parser)
        subparsers.add_parser = types.MethodType(_add_parser, subparsers)

        return subparsers

    def error(self, message):
        """Print the error message and exit."""

        # Check if the user only made a minor typo, and improve the message if they did.
        if "invalid choice: " not in message:
            message += "\nUse -h for help."
        else:
            offending, opts = message.split(" (choose from ")
            offending = offending.split("invalid choice: ")[1].strip("'")
            opts = [opt.strip(")'") for opt in opts.split(", ")]
            suggestion = DamerauLevenshtein.closest_match(offending, opts)
            if suggestion:
                message = "bad argument '%s', use '%s -h'.\n\nThe most similar argument is\n" \
                          "        %s" % (offending, self.prog, suggestion)

        super().error(message)

def parse_int_list(nums, ints=False, dedup=False, sort=False):
    """
    Turn a string contaning a comma-separated list of numbers and ranges into a list of numbers and
    return it. For example, a string like "0,1-3,7" would become ["0", "1", "2", "3", "7"].
    Optional arguments are:
      * ints - controls whether the resulting list should contain strings or integers.
      * dedup - controls whether returned list should include dublicate values or not.
      * sort - controls whether returned list is sorted or not.
    """

    if nums is None:
        return None

    if isinstance(nums, int):
        nums = str(nums)
    if isinstance(nums, str):
        nums = Trivial.split_csv_line(nums)
    if not Trivial.is_iterable(nums):
        nums = [nums]

    result = []
    for elts in nums:
        elts = str(elts)
        if "-" in elts:
            elts = Trivial.split_csv_line(elts, sep="-")
            if len(elts) != 2:
                raise Error("bad range '%s', should be two integers separated by '-'" % elts)
        else:
            elts = [elts]

        for elt in elts:
            if not Trivial.is_int(elt):
                raise Error("bad number '%s', should be an integer" % elt)

        elts = [int(elt) for elt in elts]
        if len(elts) > 1:
            if elts[0] > elts[1]:
                raise Error("bad range %d-%d, the first number should be smaller than thesecond"
                            % (elts[0], elts[1]))
            result += range(elts[0], elts[1] + 1)
        else:
            result += elts

    if dedup:
        result = Trivial.list_dedup(result)
    if sort:
        result = sorted(result)
    if not ints:
        result = [str(num) for num in result]
    return result
