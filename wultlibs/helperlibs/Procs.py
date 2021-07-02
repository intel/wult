# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2014-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module contains helper function to run and manage external processes.
"""

# pylint: disable=no-member
# pylint: disable=protected-access

import sys
import time
import shlex
import types
import queue
import errno
import codecs
import logging
import threading
import contextlib
import subprocess
from wultlibs.helperlibs import _Common, WrapExceptions
from wultlibs.helperlibs._Common import ProcResult, cmd_failed_msg # pylint: disable=unused-import
from wultlibs.helperlibs._Common import TIMEOUT
from wultlibs.helperlibs.Exceptions import Error, ErrorTimeOut, ErrorPermissionDenied

_LOG = logging.getLogger()

# This attribute helps making the API of this module similar to the API of the 'SSH' module.
hostname = "localhost"

# The exceptions to handle when dealing with file I/O.
_EXCEPTIONS = (OSError, IOError, BrokenPipeError)

def _stream_fetcher(streamid, proc, by_line):
    """
    This function runs in a separate thread. All it does is it fetches one of the output streams
    of the executed program (either stdout or stderr) and puts the result into the queue.
    """

    ppd = proc._ppd_
    partial = ""
    stream = ppd.streams[streamid]
    try:
        decoder = codecs.getincrementaldecoder('utf8')(errors="surrogateescape")
        while not ppd.threads_exit:
            if not stream:
                proc._dbg_("stream %d: stream is closed", streamid)
                break

            data = None
            try:
                data = stream.read(4096)
            except Error as err:
                if err.errno == errno.EAGAIN:
                    continue
                raise

            if not data:
                proc._dbg_("stream %d: no more data", streamid)
                break

            data = decoder.decode(data)
            if not data:
                proc._dbg_("stream %d: read more data", streamid)
                continue

            if by_line:
                data, partial = _Common.extract_full_lines(partial + data)
            if ppd.debug:
                if data:
                    proc._dbg_("stream %d: full line: %s", streamid, data[-1])
                if partial:
                    proc._dbg_("stream %d: partial line: %s", streamid, partial)
            for line in data:
                ppd.queue.put((streamid, line))
    except BaseException as err: # pylint: disable=broad-except
        _LOG.error(err)

    if partial:
        ppd.queue.put((streamid, partial))

    ppd.queue.put((streamid, None))
    proc._dbg_("stream %d: thread exists", streamid)

def _wait_timeout(proc, timeout):
    """Wait for the process to finish with a timeout."""

    proc._dbg_("_wait_timeout: waiting for exit status, timeout %s sec", timeout)
    try:
        exitcode = proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc._dbg_("_wait_timeout: exit status not ready for %s seconds", timeout)
        return None

    proc._dbg_("_wait_timeout: exit status %d", exitcode)
    return exitcode

def _consume_queue(proc, timeout):
    """Read out the entire queue."""

    ppd = proc._ppd_
    contents = []
    with contextlib.suppress(queue.Empty):
        if timeout:
            item = ppd.queue.get(timeout=timeout)
        else:
            item = ppd.queue.get(block=False)
        contents.append(item)
        # Consume the rest of the queue.
        while not ppd.queue.empty():
            contents.append(ppd.queue.get())
    return contents

def _wait_for_cmd(proc, timeout=None, capture_output=True, output_fobjs=(None, None),
                  wait_for_exit=True, by_line=True, join=True):
    """
    This function waits for a command executed with the run_async()' function to finish or print
    something to stdout or stderr.

    The optional 'timeout' argument specifies the longest time in seconds this function will wait
    for the command to finish. If the command does not finish, this function exits and returns
    'None' as the exit code of the command. The timeout must be a positive floating point number. By
    default it is 1 hour. If 'timeout' is '0', then this function will just check process status,
    grab its output, if any, and return immediately.

    Note, this function saves the used timeout in 'proc.timeout' attribute upon exit.

    The 'capture_output' parameter controls whether the output of the command should be collected or
    not. If it is not 'True', the output will simply be discarded and this function will return
    empty strings instead of command's stdout and stderr.

    The 'output_fobjs' parameter is a tuple with two file-like objects where the stdout and stderr
    of the command will be echoed, in addition to being captured and returned. If not specified,
    then the the command output will not be echoed anywhere.

    The 'wait_for_exit' parameter controls whether this function will return when the command
    exits/times-out, or immediately after the command prints something to stdout or stderr.

    The 'by_line' parameter controls whether this function should capture output on a line-by-line
    basis, or if it does not need to care about lines.

    The 'join' argument controls whether the captured output lines should be joined and returned as
    a single string, or no joining is needed and the output should be returned as a list of strings.
    In the latter case if if 'by_line' is 'True, the output will be a list of full lines, otherwise
    it may be a list of partial lines. Newlines are not stripped in any case.

    This function returns a named tuple similar to what the 'run()' function returns.
    """

    if timeout is None:
        timeout = TIMEOUT
    if timeout < 0:
        raise Error(f"bad timeout value {timeout}, must be > 0")
    proc.timeout = timeout

    proc._dbg_("wait_for_cmd: timeout %s, capture_output %s, wait_for_exit %s, by_line %s, "
               "join: %s:", timeout, capture_output, wait_for_exit, by_line, join)

    ppd = proc._ppd_
    if ppd.exitcode:
        # This command has already exited.
        return ("", "", ppd.exitcode)

    if not proc.stdout and not proc.stderr:
        return ("", "", _wait_timeout(proc, timeout))

    if not ppd.queue:
        ppd.queue = queue.Queue()
        for streamid in (0, 1):
            if ppd.streams[streamid]:
                assert ppd.threads[streamid] is None
                ppd.threads[streamid] = threading.Thread(target=_stream_fetcher,
                                                         name='Procs-stream-fetcher',
                                                         args=(streamid, proc, by_line),
                                                         daemon=True)
                ppd.threads[streamid].start()

    output = ([], [])
    exitcode = None
    start_time = time.time()

    while True:
        for streamid, data in _consume_queue(proc, timeout):
            if data is not None:
                proc._dbg_("wait_for_cmd: got data from stream %d: %s", streamid, data)
                if capture_output:
                    output[streamid].append(data)
                if output_fobjs[streamid]:
                    output_fobjs[streamid].write(data)
            else:
                proc._dbg_("wait_for_cmd: stream %d closed", streamid)
                ppd.threads[streamid].join()
                ppd.threads[streamid] = ppd.streams[streamid] = None

        if (output[0] or output[1]) and not wait_for_exit:
            proc._dbg_("wait_for_cmd: got some output, stop waiting for more")
            break

        if timeout is not None and time.time() - start_time >= timeout:
            proc._dbg_("wait_for_cmd: stop waiting for the command - timeout")
            break

        if not ppd.streams[0] and not ppd.streams[1]:
            proc._dbg_("wait_for_cmd: both streams closed")
            ppd.queue = None
            exitcode = _wait_timeout(proc, timeout)
            break

        if not timeout:
            proc._dbg_(f"wait_for_cmd: timeout is {timeout}, exit immediately")
            break

    stdout = stderr = ""
    if output[0]:
        stdout = output[0]
        if join:
            stdout = "".join(stdout)
    if output[1]:
        stderr = output[1]
        if join:
            stderr = "".join(stderr)

    proc._dbg_("wait_for_cmd: returning, exitcode %s", exitcode)
    ppd.exitcode = exitcode
    return ProcResult(stdout=stdout, stderr=stderr, exitcode=exitcode)

def _cmd_failed_msg(proc, stdout, stderr, exitcode, startmsg=None, timeout=None):
    """
    A wrapper over '_Common.cmd_failed_msg()'. The optional 'timeout' argument specifies the
    timeout that was used for the command.
    """

    if timeout is None:
        timeout = proc.timeout
    return _Common.cmd_failed_msg(proc.cmd, stdout, stderr, exitcode, hostname=proc.hostname,
                                  startmsg=startmsg, timeout=timeout)

def _close(proc):
    """The process close method that will signal the threads to exit."""

    if hasattr(proc, "_ppd_"):
        proc._dbg_("_close_()")
        proc._ppd_.threads_exit = True

def _del(proc):
    """The process object destructor which makes all threads to exit."""

    if hasattr(proc, "_ppd_"):
        proc._dbg_("_del_()")
        ppd = proc._ppd_
        ppd.threads_exit = True
        ppd.orig_del()

def _get_err_prefix(fobj, method):
    """Return the error message prefix."""
    return "method '%s()' failed for %s" % (method, fobj.name)

def _dbg(proc, fmt, *args):
    """Print a debugging message related to the 'proc' process handling."""
    if proc._ppd_.debug:
        _LOG.debug("%s: " + fmt, proc._ppd_.debug_id, *args)

class _ProcessPrivateData:
    """
    We need to attach additional data to the Popen object. This class represents that data.
    """

    def __init__(self):
        """The constructor."""

        # The 2 output streams of the command's process (stdout, stderr).
        self.streams = []
        # The queue which is used for passing commands output from stream fetcher threads.
        self.queue = None
        # The threds fetching data from the output streams and placing them to the queue.
        self.threads = [None, None]
        # The threads have to exit if the 'threads_exit' flag becomes 'True'.
        self.threads_exit = False
        # Exit code of the command ('None' if it is still running).
        self.exitcode = None
        # The original '__del__()' methods of the Popen object.
        self.orig_del = None
        # Print debugging messages if 'True'.
        self.debug = False
        # Prefix debugging messages with this string. Can be useful to distinguish between debugging
        # message related to different processes.
        self.debug_id = "stream"

def _add_custom_fields(proc, cmd):
    """Add a couple of custom fields to the process object returned by 'subprocess.Popen()'."""

    for name in ("stdin", "stdout", "stderr"):
        if getattr(proc, name):
            wrapped_fobj = WrapExceptions.WrapExceptions(getattr(proc, name),
                                                         exceptions=_EXCEPTIONS,
                                                         get_err_prefix=_get_err_prefix)
            setattr(proc, name, wrapped_fobj)

    ppd = proc._ppd_ = _ProcessPrivateData()

    ppd.streams = [proc.stdout, proc.stderr]
    ppd.orig_del = proc.__del__

    # The below attributes are added to the Popen object look similar to the channel object which
    # the 'SSH' module uses.
    proc.hostname = "localhost"
    proc.cmd = cmd
    proc.timeout = TIMEOUT
    proc.close = types.MethodType(_close, proc)
    proc._dbg_ = types.MethodType(_dbg, proc)
    proc.cmd_failed_msg = types.MethodType(_cmd_failed_msg, proc)
    proc.wait_for_cmd = types.MethodType(_wait_for_cmd, proc)
    proc.__del__ = types.MethodType(_del, proc)
    return proc

def _do_run_async(command, stdin=None, stdout=None, stderr=None, bufsize=0, cwd=None, env=None,
                  shell=False, newgrp=False):
    """Implements 'run_async()'."""

    try:
        if stdin and isinstance(stdin, str):
            fname = stdin
            stdin = open(fname, "r")

        if stdout and isinstance(stdout, str):
            fname = stdout
            stdout = open(fname, "w+")

        if stderr and isinstance(stderr, str):
            fname = stderr
            stderr = open(fname, "w+")
    except OSError as err:
        raise Error("cannot open file '%s': %s" % (fname, err)) from None

    if shell:
        cmd = command = " exec stdbuf -i0 -o0 -e0 -- " + command
    elif isinstance(command, str):
        cmd = shlex.split(command)
    else:
        cmd = command

    try:
        proc = subprocess.Popen(cmd, stdin=stdin, stdout=stdout, stderr=stderr, bufsize=bufsize,
                                cwd=cwd, env=env, shell=shell, start_new_session=newgrp)
    except OSError as err:
        raise Error("the following command failed with error '%s':\n%s" % (err, command)) from err

    return _add_custom_fields(proc, cmd)

def run_async(command, stdin=None, stdout=None, stderr=None, bufsize=0, cwd=None, env=None,
              shell=False, newgrp=False):
    """
    A helper function to run an external command asynchronously. The 'command' argument should be a
    string containing the command to run. The 'stdin', 'stdout', and 'stderr' parameters can be one
    of:
        * an open file descriptor (a positive integer)
        * a file object
        * file path (in case of stdout and stderr the file will be created if it does not exist)

    The 'bufsize', 'cwd','env' and 'shell' arguments are the same as in 'Popen()'.

    If the 'newgrp' argument is 'True', then new process gets new session ID.

    Returns the 'Popen' object of the executed process.
    """

    if cwd:
        cwd_msg = "\nWorking directory: %s" % cwd
    else:
        cwd_msg = ""
    _LOG.debug("running the following local command asynchronously:\n%s%s", command, cwd_msg)

    return _do_run_async(command, stdin=stdin, stdout=stdout, stderr=stderr, bufsize=bufsize,
                         cwd=cwd, env=env, shell=shell, newgrp=newgrp)

def run(command, timeout=None, capture_output=True, mix_output=False, join=True,
        output_fobjs=(None, None), bufsize=0, cwd=None, env=None, shell=False, newgrp=False):
    """
    Run command 'command' on the remote host and block until it finishes. The 'command' argument
    should be a string.

    The 'timeout' parameter specifies the longest time for this method to block. If the command
    takes longer, this function will raise the 'ErrorTimeOut' exception. The default is 1h.

    If the 'capture_output' argument is 'True', this function intercept the output of the executed
    program, otherwise it doesn't and the output is dropped (default) or printed to 'output_fobjs'.

    If the 'mix_output' argument is 'True', the standard output and error streams will be mixed
    together.

    The 'join' argument controls whether the captured output is returned as a single string or a
    list of lines (trailing newline is not stripped).

    The 'bufsize', 'cwd','env' and 'shell' arguments are the same as in 'Popen()'.

    If the 'newgrp' argument is 'True', then new process gets new session ID.

    The 'output_fobjs' is a tuple which may provide 2 file-like objects where the standard output
    and error streams of the executed program should be echoed to. If 'mix_output' is 'True', the
    'output_fobjs[1]' file-like object, which corresponds to the standard error stream, will be
    ignored and all the output will be echoed to 'output_fobjs[0]'. By default the command output is
    not echoed anywhere.

    Note, 'capture_output' and 'output_fobjs' arguments can be used at the same time. It is OK to
    echo the output to some files and capture it at the same time.

    This function returns an named tuple of (stdout, stderr, exitcode), where
      o 'stdout' is the output of the executed command to stdout
      o 'stderr' is the output of the executed command to stderr
      o 'exitcode' is the integer exit code of the executed command

    If the 'mix_output' argument is 'True', the 'stderr' part of the returned tuple will be an
    empty string.

    If the 'capture_output' argument is not 'True', the 'stdout' and 'stderr' parts of the returned
    tuple will be an empty string.
    """

    if cwd:
        cwd_msg = "\nWorking directory: %s" % cwd
    else:
        cwd_msg = ""
    _LOG.debug("running the following local command:\n%s%s", command, cwd_msg)

    stdout = subprocess.PIPE
    if mix_output:
        stderr = subprocess.STDOUT
    else:
        stderr = subprocess.PIPE

    proc = _do_run_async(command, stdout=stdout, stderr=stderr, bufsize=bufsize, cwd=cwd, env=env,
                         shell=shell, newgrp=newgrp)

    if join:
        by_line = False
    else:
        by_line = True
    result = proc.wait_for_cmd(capture_output=capture_output, output_fobjs=output_fobjs,
                               timeout=timeout, by_line=by_line, join=join)

    if result.exitcode is None:
        msg = _Common.cmd_failed_msg(command, *tuple(result), timeout=timeout)
        raise ErrorTimeOut(msg)

    if output_fobjs[0]:
        output_fobjs[0].flush()
    if output_fobjs[1]:
        output_fobjs[1].flush()

    return result

def run_verify(command, timeout=None, capture_output=True, mix_output=False, join=True,
               output_fobjs=(None, None), bufsize=0, cwd=None, env=None, shell=False,
               newgrp=False):
    """
    Same as 'run()' but verifies the command's exit code and raises an exception if it is not 0.
    """

    result = run(command, timeout=timeout, capture_output=capture_output, mix_output=mix_output,
                 join=join, output_fobjs=output_fobjs, bufsize=bufsize, cwd=cwd, env=env,
                 shell=shell, newgrp=newgrp)
    if result.exitcode == 0:
        return (result.stdout, result.stderr)

    raise Error(_Common.cmd_failed_msg(command, *tuple(result), timeout=timeout))

def rsync(src, dst, opts="rlptD", remotesrc=False, remotedst=True):
    # pylint: disable=unused-argument
    """
    Copy data from path 'src' to path 'dst' using 'rsync' with options specified in 'opts'. The
    'remotesrc' and 'remotedst' arguments are ignored. They only exist for compatibility with
    'SSH.rsync()'.
    """

    cmd = "rsync -%s -- '%s' '%s'" % (opts, src, dst)
    try:
        run_verify(cmd)
    except Error as err:
        raise Error("failed to copy files '%s' to '%s':\n%s" % (src, dst, err)) from err

class Proc:
    """This class provides API similar to the 'SSH' class API."""

    Error = Error

    @staticmethod
    def run_async(command, cwd=None, shell=False):
        """A version of 'run_async()' compatible with 'SSH.run_async()'."""

        return run_async(command, cwd=cwd, shell=shell, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def __init__(self):
        """Initialize a class instance."""
        self.is_remote = False
        self.hostname = "localhost"
        self.hostmsg = ""

    def close(self):
        """Fake version of 'SSH.close()'."""

    @staticmethod
    def open(path, mode):
        """
        Open a file at 'path' using mode 'mode' (the arguments are the same as in the builtin Python
        'open()' function).
        """

        errmsg = f"cannot open file '{path}' with mode '{mode}': "
        try:
            fobj = open(path, mode)
        except PermissionError as err:
            raise ErrorPermissionDenied(f"{errmsg}{err}") from None
        except OSError as err:
            raise Error(f"{errmsg}{err}") from None

        # Make sure methods of 'fobj' always raise the 'Error' exceptions.
        fobj = WrapExceptions.WrapExceptions(fobj, exceptions=_EXCEPTIONS,
                                             get_err_prefix=_get_err_prefix)
        return fobj

    def __enter__(self):
        """Enter the runtime context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()

    def __getattr__(self, name):
        """Map unknown attribute to the module symbol if possible."""

        module = sys.modules[__name__]
        if hasattr(module, name):
            return getattr(module, name)
        raise AttributeError("class 'Proc' has no attribute '%s'" % name)
