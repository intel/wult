# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2014-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module contains helper functions related to logging.
"""

import re
import sys
import json
import logging
import traceback
from pathlib import Path
try:
    # It is OK if 'colorama' is not available, we only lose message coloring.
    import colorama
except ImportError:
    colorama = None
from wultlibs.helperlibs.Exceptions import Error # pylint: disable=unused-import

INFO = logging.INFO
DEBUG = logging.DEBUG
WARNING = logging.WARNING
# Same as "WARNING", but adds a "notice:" prefix.
NOTICE = logging.WARNING + 1
ERROR = logging.ERROR
# Add the "ERRINFO" log lovel which is the same as "ERROR", but not prefixed.
ERRINFO = logging.ERROR + 1
CRITICAL = logging.CRITICAL

# The default logging object.
main_log = logging.getLogger("main")

def error_traceback(msgformat, *args):
    """Print an error message occurred along with the traceback."""

    tback = []

    if sys.exc_info()[0]:
        lines = traceback.format_exc().splitlines()
    else:
        lines = [line.strip() for line in traceback.format_stack()]

    idx = 0
    last_idx = len(lines) - 1
    while idx < len(lines):
        if lines[idx].startswith('  File "'):
            idx += 2
            last_idx = idx
        else:
            idx += 1

    tback = lines[0:last_idx]

    if tback:
        if colorama:
            dim = colorama.Style.RESET_ALL + colorama.Style.DIM
            undim = colorama.Style.RESET_ALL
        main_log.log(ERRINFO, "--- Debug trace starts here ---")
        tb = "\n".join(tback)
        main_log.log(ERRINFO, "%sAn error occurred, here is the traceback:\n%s%s", dim, tb, undim)
        main_log.log(ERRINFO, "--- Debug trace ends here ---\n")

    if args:
        errmsg = msgformat % args
    else:
        errmsg = str(msgformat)
    main_log.error(errmsg)

def error_out(msgformat, *args, print_tb=False):
    """
    Print an error message and terminate program execution. The optional 'print_tb' agument
    controls whether the stack trace should also be printed. Note, however, if debugging is enabled,
    the stack trace is printed out regardless of 'print_tb' value.
    """

    if print_tb or main_log.getEffectiveLevel() == DEBUG:
        error_traceback(str(msgformat) + "\n", *args)
    else:
        if args:
            errmsg = msgformat % args
        else:
            errmsg = str(msgformat)
        main_log.error(errmsg)

    raise SystemExit(1)

def json_dumps(data, *args, **kwargs):
    """
    Same as 'json.dumps()', but does not fail on 'pathlib.Path' types.
    """

    class _Encoder(json.JSONEncoder):
        """Json encoder class."""
        def default(self, obj): # pylint: disable=arguments-differ,method-hidden
            """Translate various types to string."""
            if isinstance(obj, Path):
                return str(obj)
            return super().default(obj)

    return json.dumps(data, *args, **kwargs, cls=_Encoder)

class _MyFormatter(logging.Formatter):
    """
    A custom formatter for logging messages. The reason we have it is to provide different message
    format for different log levels.
    """

    # pylint: disable=protected-access
    def __init__(self, prefix=None, colors=None):
        """
        The constructor. The arguments are as follows.
          * prefix' - the prefix for all non-info and non-debug messages. Default is no prefix. Info
                      messages come without any formating, debug messages have a prefix including
                      the time-stamp, module name, and line number.
          * colors - a dictionary containing colorama color codes for message time-staps and
                     prefixes.
        """

        def _start(level):
            """Return color code for log level 'level'."""
            return str(colors.get(level, ""))

        def _end(level):
            """Return the code for stopping coloring for log level 'level'."""
            if level in colors:
                return str(colorama.Style.RESET_ALL)
            return ""

        logging.Formatter.__init__(self, "%(levelname)s: %(message)s", "%H:%M:%S")

        if not prefix:
            prefix = ""
        self._prefix = prefix
        self._orig_fmt = self._style._fmt

        if not colors or not colorama:
            colors = {}

        self.myfmt = {}

        for lvl, pfx in ((WARNING, "warning"), (ERROR, "error"), (CRITICAL, "critical error"),
                         (NOTICE, "notice")):
            self.myfmt[lvl] = self._prefix + _start(lvl) + pfx + _end(lvl) + ": %(message)s"
        # Prefix debug messages with a green-colored time-stamp, module name and line number.
        lvl = DEBUG
        self.myfmt[lvl] = "[" + _start(lvl) + "%(asctime)s" + _end(lvl) + \
                          "] [%(module)s,%(lineno)d] " + self._style._fmt
        # Leave the info messages without any formatting.
        self.myfmt[ERRINFO] = self.myfmt[INFO] = "%(message)s"

    def format(self, record):
        """
        The formatter which which simply prefixes all debugging messages with a time-stamp and makes
        sure the info messages stay intact.
        """

        self._style._fmt = self.myfmt[record.levelno]
        return logging.Formatter.format(self, record)

class _MyFilter(logging.Filter):
    """A custom filter which allows only certain log levels to go through."""

    def __init__(self, let_go):
        """The constructor."""

        logging.Filter.__init__(self)
        self._let_go = let_go

    def filter(self, record):
        """Filter out all log levels except the ones user specified."""

        if record.levelno in self._let_go:
            return True
        return False

def _flush_stdout_stderr():
    """Flush the 'stdout' and 'stderr' streams."""

    sys.stdout.flush()
    sys.stderr.flush()

def setup_logger(name=None, prefix=None, loglevel=None, colored=None):
    """
    Setup and return a logger.
      * name - name of the logger to setup, default is "main" ('main_log').
      * prefix - usually the program name, but can be any prefix that will be used for "WARNING",
                 "ERROR" and "CRITICAL" log level messages. No prefix is used by default.
      * loglevel - the default log level. If not provided, this function initializes it depending on
                   the '-d' and '-q' command line options.
      * colored - whether the output should be colored or not. By default this function
                  automatically figures out the coloring by checking if the output file descriptors
                  are TTYs and whether the '--force-color" command line option is used.
    """

    if not name:
        name = "main"

    if not loglevel:
        # Change log level names.
        if "-q" in sys.argv:
            loglevel = WARNING
        elif "-d" in sys.argv:
            loglevel = DEBUG
        else:
            loglevel = INFO

    if colored is None:
        if not colorama:
            colored = False
        elif "--force-color" in sys.argv:
            colored = True
        else:
            colored = sys.stdout.isatty() and sys.stderr.isatty()

    logger = logging.getLogger(name)
    logger.colored = colored
    logger.setLevel(loglevel)

    colors = {}
    if colored:
        colors[DEBUG] = colorama.Fore.GREEN
        colors[WARNING] = colorama.Fore.YELLOW
        colors[ERROR] = colors[CRITICAL] = colors[NOTICE] = colorama.Fore.RED

    formatter = _MyFormatter(prefix=prefix, colors=colors)

    # Remove existing handlers.
    logger.handlers = []

    where = logging.StreamHandler(sys.stderr)
    where.setFormatter(formatter)
    where.addFilter(_MyFilter([DEBUG, WARNING, NOTICE, ERROR, ERRINFO, CRITICAL]))
    logger.addHandler(where)

    where = logging.StreamHandler(sys.stdout)
    where.setFormatter(formatter)
    where.addFilter(_MyFilter([INFO]))
    logger.addHandler(where)

    logger.flush = _flush_stdout_stderr
    return logger

def setup_loggers(owname=None):
    """
    Setup the default loggers. This function initializes the log level depending on the whether '-d'
    and '-q' command line options were used. It also forces color output if the '--force-color'
    command line option was used. The 'owname' argument should contain the name of the script.
    """

    setup_logger(name="main", prefix=owname + ": ")

class LoggingFileObject:
    """
    This class implements a "write-only" file-like object on top of the logging object.
    It buffers the data and sends full lines down to the logger.
    """

    def write(self, data):
        """
        Send full lines down to the logging object, and buffer the rest of the data which do not
        constitute a full line.
        """

        for line_match in re.finditer("(.*)\n|(.+$)", self._buf + data):
            if line_match.group(2):
                self._buf = line_match.group(2)
                return len(data)

            self._logger.log(self._level, self._prefix + line_match.group(1))

        self._buf = ""
        return 0

    def flush(self):
        """Send all the buffered data down to the logging object."""

        if self._buf:
            self._logger.log(self._level, self._buf)

    def __init__(self, level, name=None, prefix=""):
        """
        Initialize a class instance. The 'level' argument is the logging level to use when sending
        full lines down to the logging object. The 'name' argument is name of the logger to use.
        Default is "file_logger". The 'prefix' argument can be used to prefix all the lines written
        to this file object.
        """

        self._level = level
        self._prefix = prefix
        self._buf = ""
        if not name:
            name = "file_logger"
        self._logger = setup_logger(name=name)
