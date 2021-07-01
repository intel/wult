# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2014-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides helpful API for communicating and working with remote hosts over SSH.

SECURITY NOTICE: this module and any part of it should only be used for debugging and development
purposes. No security audit had been done. Not for production use.
"""

# pylint: disable=no-member
# pylint: disable=protected-access

import os
import pwd
import glob
import time
import stat
import types
import queue
import codecs
import socket
import logging
import threading
from pathlib import Path
import contextlib
import paramiko
from wultlibs.helperlibs import _Common, Procs, WrapExceptions
from wultlibs.helperlibs._Common import ProcResult, cmd_failed_msg # pylint: disable=unused-import
from wultlibs.helperlibs._Common import TIMEOUT
from wultlibs.helperlibs.Exceptions import Error, ErrorPermissionDenied, ErrorTimeOut, ErrorConnect

_LOG = logging.getLogger()

# Paramiko is a bit too noisy, lower its log level.
logging.getLogger("paramiko").setLevel(logging.WARNING)

# The exceptions to handle when dealing with paramiko.
_PARAMIKO_EXCEPTIONS = (OSError, IOError, paramiko.SSHException, socket.error)

def _get_username(uid=None):
    """Return username of the current process or UID 'uid'."""

    try:
        if uid is None:
            uid = os.getuid()
    except OSError as err:
        raise Error("failed to detect user name of the current process:\n%s" % err) from None

    try:
        return pwd.getpwuid(uid).pw_name
    except KeyError as err:
        raise Error("failed to get user name for UID %d:\n%s" % (uid, err)) from None

def _stream_fetcher(streamid, chan, by_line):
    """
    This function runs in a separate thread. All it does is it fetches one of the output streams
    of the executed program (either stdout or stderr) and puts the result into the queue.
    """

    partial = ""
    read_func = chan._streams_[streamid]
    decoder = codecs.getincrementaldecoder('utf8')(errors="surrogateescape")
    try:
        while not chan._threads_exit_:
            if not read_func:
                chan._dbg_("stream %d: stream is closed", streamid)
                break

            data = None
            try:
                data = read_func(4096)
            except socket.timeout:
                chan._dbg_("stream %d: read timeout", streamid)
                continue

            if not data:
                chan._dbg_("stream %d: no more data", streamid)
                break

            data = decoder.decode(data)
            if not data:
                chan._dbg_("stream %d: read more data", streamid)
                continue

            chan._dbg_("stream %d: read data: %s", streamid, data)

            if by_line:
                data, partial = _Common.extract_full_lines(partial + data)
            if chan._debug_:
                if data:
                    chan._dbg_("stream %d: full line: %s", streamid, data[-1])
                if partial:
                    chan._dbg_("stream %d: partial line: %s", streamid, partial)
            for line in data:
                chan._queue_.put((streamid, line))
    except BaseException as err: # pylint: disable=broad-except
        _LOG.error(err)

    if partial:
        chan._queue_.put((streamid, partial))

    # The end of stream marker.
    chan._queue_.put((streamid, None))
    chan._dbg_("stream %d: thread exists", streamid)

def _recv_exit_status_timeout(chan, timeout):
    """
    This is a version of paramiko channel's 'recv_exit_status()' which supports a timeout.
    Returns the exit status or 'None' in case of 'timeout'.
    """

    chan._dbg_("_recv_exit_status_timeout: waiting for exit status, timeout %s sec", timeout)

#    This is non-hacky, but polling implementation.
#    if timeout:
#        start_time = time.time()
#        while not chan.exit_status_ready():
#            if time.time() - start_time > timeout:
#                chan._dbg_("exit status not ready for %s seconds", timeout)
#                return None
#            time.sleep(1)
#    exitcode = chan.recv_exit_status()

    # This is hacky, but non-polling implementation.
    if not chan.status_event.wait(timeout=timeout):
        chan._dbg_("_recv_exit_status_timeout: exit status not ready for %s seconds", timeout)
        return None

    exitcode = chan.exit_status
    chan._dbg_("_recv_exit_status_timeout: exit status %d", exitcode)
    return exitcode

def _consume_queue(chan, timeout):
    """Read out the entire queue."""

    contents = []
    with contextlib.suppress(queue.Empty):
        if timeout:
            item = chan._queue_.get(timeout=timeout)
        else:
            item = chan._queue_.get(block=False)
        contents.append(item)
        # Consume the rest of the queue.
        while not chan._queue_.empty():
            contents.append(chan._queue_.get())
    return contents

def _do_wait_for_cmd(chan, timeout=None, capture_output=True, output_fobjs=(None, None),
                     wait_for_exit=True, join=True):
    """Implements '_wait_for_cmd()'."""

    output = ([], [])
    exitcode = None
    start_time = time.time()

    while True:
        for streamid, data in _consume_queue(chan, timeout):
            if data is not None:
                chan._dbg_("_do_wait_for_cmd: got data from stream %d: %s", streamid, data)
                if capture_output:
                    output[streamid].append(data)
                if output_fobjs[streamid]:
                    output_fobjs[streamid].write(data)
            else:
                chan._dbg_("_do_wait_for_cmd: stream %d closed", streamid)
                # One of the output streams closed.
                chan._threads_[streamid].join()
                chan._threads_[streamid] = chan._streams_[streamid] = None

        if (output[0] or output[1]) and not wait_for_exit:
            chan._dbg_("_do_wait_for_cmd: got some output, stop waiting for more")
            break

        if timeout and time.time() - start_time > timeout:
            chan._dbg_("_do_wait_for_cmd: stop waiting for the command - timeout")
            break

        if not chan._streams_[0] and not chan._streams_[1]:
            chan._dbg_("_do_wait_for_cmd: both streams closed")
            chan._queue_ = None
            exitcode = _recv_exit_status_timeout(chan, timeout)
            break

        if not timeout:
            chan._dbg_(f"_do_wait_for_cmd: timeout is {timeout}, exit immediately")
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

    chan._dbg_("_do_wait_for_cmd: returning, exitcode %s", exitcode)
    chan._exitcode_ = exitcode
    return ProcResult(stdout=stdout, stderr=stderr, exitcode=exitcode)

def _wait_for_cmd(chan, timeout=None, capture_output=True, output_fobjs=(None, None),
                  wait_for_exit=True, by_line=True, join=True):
    """
    This function waits for a command executed with the 'SSH.run_async()' function to finish or
    print something to stdout or stderr.

    The optional 'timeout' argument specifies the longest time in seconds this function will wait
    for the command to finish. If the command does not finish, this function exits and returns
    'None' as the exit code of the command. The timeout must be a positive floating point number. By
    default it is 1 hour. If 'timeout' is '0', then this function will just check process status,
    grab its output, if any, and return immediately.

    Note, this function saves the used timeout in 'chan.timeout' attribute upon exit.

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
    chan.timeout = timeout

    chan._dbg_("wait_for_cmd: timeout %s, capture_output %s, wait_for_exit %s, by_line %s, "
               "join: %s:", timeout, capture_output, wait_for_exit, by_line, join)

    if chan._threads_exit_:
        raise Error("this SSH channel has '_threads_exit_ flag set and it cannot be used")

    if chan._exitcode_:
        # This command has already exited.
        return ("", "", chan._exitcode_)

    if not chan._queue_:
        chan._queue_ = queue.Queue()
        for streamid in (0, 1):
            if chan._streams_[streamid]:
                assert chan._threads_[streamid] is None
                chan._threads_[streamid] = threading.Thread(target=_stream_fetcher,
                                                            name='SSH-stream-fetcher',
                                                            args=(streamid, chan, by_line),
                                                            daemon=True)
                chan._threads_[streamid].start()

    return _do_wait_for_cmd(chan, timeout=timeout, capture_output=capture_output,
                            output_fobjs=output_fobjs, wait_for_exit=wait_for_exit, join=join)

def _poll(chan):
    """
    Check if the process is still running. If it is, return 'None', else return exit status.
    """

    if chan.exit_status_ready():
        return chan.recv_exit_status()
    return None

def _cmd_failed_msg(chan, stdout, stderr, exitcode, startmsg=None, timeout=None):
    """
    A wrapper over '_Common.cmd_failed_msg()'. The optional 'timeout' argument specifies the
    timeout that was used for the command.
    """

    if timeout is None:
        timeout = chan.timeout
    return _Common.cmd_failed_msg(chan.cmd, stdout, stderr, exitcode, hostname=chan.hostname,
                                  startmsg=startmsg, timeout=timeout)

def _close(chan):
    """The channel close method that will signal the threads to exit."""

    chan._dbg_("_close()")
    if hasattr(chan, "_threads_exit_"):
        chan._threads_exit_ = True
    if hasattr(chan, "_ssh_"):
        chan._ssh_ = None
    chan._orig_close_()

def _del(chan):
    """The channel object destructor which makes all threads to exit."""

    chan._dbg_("_del_()")
    chan._close()
    chan._orig_del_()

def _get_err_prefix(fobj, method):
    """Return the error message prefix."""
    return f"method '{method}()' failed for file '{fobj._stream_name_}'"

def _dbg(chan, fmt, *args):
    """Print a debugging message related to the 'chan' channel handling."""
    if chan._debug_:
        _LOG.debug("%s: " + fmt, chan._id_, *args)

def _add_custom_fields(chan, ssh, cmd, pid):
    """Add a couple of custom fields to the paramiko channel object."""

    for name, mode in (("stdin", "wb"), ("stdout", "rb"), ("stderr", "rb")):
        try:
            if name != "stderr":
                fobj = chan.makefile(mode, 0)
            else:
                fobj = chan.makefile_stderr(mode, 0)
        except _PARAMIKO_EXCEPTIONS as err:
            raise Error(f"failed to create a file for '{name}': {err}") from err

        setattr(fobj, "_stream_name_", name)
        wrapped_fobj = WrapExceptions.WrapExceptions(fobj, exceptions=_PARAMIKO_EXCEPTIONS,
                                                     get_err_prefix=_get_err_prefix)
        wrapped_fobj.name = name
        setattr(chan, name, wrapped_fobj)

    chan._queue_ = None
    chan._streams_ = [chan.recv, chan.recv_stderr]
    chan._threads_ = [None, None]
    chan._threads_exit_ = False
    chan._exitcode_ = None
    chan._orig_close_ = chan.close
    chan._orig_del_ = chan.__del__

    # Debugging prints.
    chan._debug_ = False
    chan._id_ = "stream"

    # The below attributes are added to make the channel object look similar to the Popen object
    # which the 'Procs' module uses.
    chan.hostname = ssh.hostname
    chan.cmd = cmd
    chan.timeout = TIMEOUT
    if pid is not None:
        chan.pid = pid
    chan.close = types.MethodType(_close, chan)

    chan._ssh_ = ssh
    chan._dbg_ = types.MethodType(_dbg, chan)
    chan.poll = types.MethodType(_poll, chan)
    chan.cmd_failed_msg = types.MethodType(_cmd_failed_msg, chan)
    chan.wait_for_cmd = types.MethodType(_wait_for_cmd, chan)
    chan.__del__ = types.MethodType(_del, chan)

    return chan

class SSH:
    """
    This class provides API for communicating with remote hosts over SSH.

    SECURITY NOTICE: this class and any part of it should only be used for debugging and development
    purposes. No security audit had been done. Not for production use.
    """

    Error = Error

    def _run_in_new_session(self, command):
        """Run command 'command' in a new session."""

        try:
            chan = self.ssh.get_transport().open_session(timeout=self.connection_timeout)
            chan.exec_command(command)
        except (paramiko.SSHException, socket.error) as err:
            raise Error(f"cannot execute the following command in new SSH session{self.hostmsg}:\n"
                        "{command}\nReason: {err}") from err

        return chan

    def _run_async_noshell(self, command):
        """
        Runs a command in a new session in case usage of shell was prohibited. In most cases the SSH
        server will run the command in some user shell, but the point is that we are not allowed to
        use shell.
        """

        chan = self._run_in_new_session(command)
        return _add_custom_fields(chan, self, command, None)

    def _read_pid(self, chan, command):
        """Return PID of the just executed command."""

        pid = []
        pid_timeout = 10
        time_before = time.time()
        decoder = codecs.getincrementaldecoder('utf8')(errors="surrogateescape")
        while time.time() - time_before < pid_timeout:
            buf = chan.recv(1)
            if not buf:
                # No data received, which means that the channel is closed.
                status = chan.recv_exit_status()
                raise Error(f"cannot execute the following command{self.hostmsg}:\n{command}\n"
                            f"The process exited with status {status}")

            buf = decoder.decode(buf)
            if not buf:
                continue
            if buf == "\n":
                return int("".join(pid))
            pid.append(buf)
            if len(pid) > 128:
                raise Error(f"received the following {len(pid)} PID characters without "
                            f"newline:\n{''.join(pid)}")

        raise Error(f"failed to read PID for the following command:\n{command}\nWaited for "
                    f"{pid_timeout} seconds, but the PID did not show up in stdout")

    def _run_async(self, command, cwd=None, shell=True):
        """Implements 'run_async()'."""

        # Allow for 'command' to be a 'pathlib.Path' object which Paramiko does not accept.
        command = str(command)

        if not shell:
            return self._run_async_noshell(command)

        # Prepend the command with a shell statement which prints the PID of the shell where the
        # command will be run. Then use 'exec' to make sure that the command inherits the PID.
        prefix = r'printf "%s\n" "$$";'
        if cwd:
            prefix += f""" cd "{cwd}" &&"""
        # Force unbuffered I/O to be consistent with the 'shell=False' case.
        command = prefix + " exec stdbuf -i0 -o0 -e0 -- " + command

        try:
            chan = self.ssh.get_transport().open_session(timeout=self.connection_timeout)
            chan.exec_command(command)
        except (paramiko.SSHException, socket.error) as err:
            raise Error(f"cannot execute the following command{self.hostmsg}:\n{command}\nReason: "
                        f"{err}") from err

        # The first line of the output should contain the PID - extract it.
        pid = self._read_pid(chan, command)
        return _add_custom_fields(chan, self, command, pid)

    def run_async(self, command, cwd=None, shell=True):
        """
        Run command 'command' on a remote host and return immediately without waiting for the
        command to complete.

        The 'cwd' argument is the same as in case of the 'run()' method.

        The 'shell' argument tells whether it is safe to assume that the SSH daemon on the target
        system runs some sort of Unix shell for the SSH session. Usually this is the case, but not
        always. E.g., Dell's iDRACs do not run a shell when you log into them. The reason this
        function may want to assume that the 'command' command runs in a shell is to get the PID of
        the process on the remote system. So if you do not really need to know the PID, leave the
        'shell' parameter to be 'False'.

        Returns the paramiko session channel object. The object will contain an additional 'pid'
        attribute, and depending on the 'shell' parameter, the attribute will have value 'None'
        ('shell' is 'False') or the integer PID of the executed process on the remote host ('shell'
        is 'True').
        """

        if cwd:
            if not shell:
                raise Error("cannot set working directory to '{cwd}' - using shell is disallowed")
            cwd_msg = f"\nWorking directory: {cwd}"
        else:
            cwd_msg = ""
        _LOG.debug("running the following command asynchronously%s:\n%s%s",
                   self.hostmsg, command, cwd_msg)
        return self._run_async(str(command), cwd=cwd, shell=shell)

    def run(self, command, timeout=None, capture_output=True, mix_output=False, join=True,
            output_fobjs=(None, None), cwd=None, shell=True): # pylint: disable=unused-argument
        """
        Run command 'command' on the remote host and block until it finishes. The 'command' argument
        should be a string.

        The 'timeout' parameter specifies the longest time for this method to block. If the command
        takes longer, this function will raise the 'ErrorTimeOut' exception. The default is 1h.

        If the 'capture_output' argument is 'True', this function intercept the output of the
        executed program, otherwise it doesn't and the output is dropped (default) or printed to
        'output_fobjs'.

        If the 'mix_output' argument is 'True', the standard output and error streams will be mixed
        together.

        The 'output_fobjs' is a tuple which may provide 2 file-like objects where the standard
        output and error streams of the executed program should be echoed to. If 'mix_output' is
        'True', the 'output_fobjs[1]' file-like object, which corresponds to the standard error
        stream, will be ignored and all the output will be echoed to 'output_fobjs[0]'. By default
        the command output is not echoed anywhere.

        Note, 'capture_output' and 'output_fobjs' arguments can be used at the same time. It is OK
        to echo the output to some files and capture it at the same time.

        The 'join' argument controls whether the captured output is returned as a single string or a
        list of lines (trailing newline is not stripped).

        The 'cwd' argument may be used to specify the working directory of the command.

        The 'shell' argument controlls whether the command should be run via a shell on the remote
        host. Most SSH servers will use user shell to run the command anyway. But there are rare
        cases when this is not the case, and 'shell=False' may be handy.

        This function returns an named tuple of (exitcode, stdout, stderr), where
          o 'stdout' is the output of the executed command to stdout
          o 'stderr' is the output of the executed command to stderr
          o 'exitcode' is the integer exit code of the executed command

        If the 'mix_output' argument is 'True', the 'stderr' part of the returned tuple will be an
        empty string.

        If the 'capture_output' argument is not 'True', the 'stdout' and 'stderr' parts of the
        returned tuple will be an empty string.
        """

        msg = f"running the following command{self.hostmsg}:\n{command}"
        if cwd:
            msg += f"\nWorking directory: {cwd}"
        _LOG.debug(msg)

        # Execute the command on the remote host.
        chan = self._run_async(command, cwd=cwd, shell=shell)
        if mix_output:
            chan.set_combine_stderr(True)

        # Wait for the command to finish and handle the time-out situation.
        if join:
            by_line = False
        else:
            by_line = True
        result = chan.wait_for_cmd(timeout=timeout, capture_output=capture_output,
                                   output_fobjs=output_fobjs, by_line=by_line, join=join)

        if result.exitcode is None:
            msg = self.cmd_failed_msg(command, *tuple(result), timeout=timeout)
            raise ErrorTimeOut(msg)

        if output_fobjs[0]:
            output_fobjs[0].flush()
        if output_fobjs[1]:
            output_fobjs[1].flush()

        return result

    def run_verify(self, command, timeout=None, capture_output=True, mix_output=False,
                   join=True, output_fobjs=(None, None), cwd=None, shell=True):
        """
        Same as the "run()" method, but also verifies the exit status and if the command failed,
        raises the "Error" exception.
        """

        result = self.run(command, timeout=timeout, capture_output=capture_output,
                          mix_output=mix_output, join=join, output_fobjs=output_fobjs, cwd=cwd,
                          shell=shell)
        if result.exitcode == 0:
            return (result.stdout, result.stderr)

        msg = self.cmd_failed_msg(command, *tuple(result), timeout=timeout)
        raise Error(msg)

    def get_ssh_opts(self):
        """
        Returns 'ssh' command-line tool options that are necessary to establish an SSH connection
        similar to the current connection.
        """

        ssh_opts = f"-o \"Port={self.port}\" -o \"User={self.username}\""
        if self.privkeypath:
            ssh_opts += f" -o \"IdentityFile={self.privkeypath}\""
        return ssh_opts

    def rsync(self, src, dst, opts="rlptD", remotesrc=True, remotedst=True):
        """
        Copy data from path 'src' to path 'dst' using 'rsync' with options specified in 'opts'. By
        default the 'src' and 'dst' path is assumed to be on the remote host, but the 'rmotesrc' and
        'remotedst' arguments can be set to 'False' to specify local source and/or destination
        paths.
        """

        cmd = f"rsync -{opts}"
        if remotesrc and remotedst:
            proc = self
        else:
            proc = Procs.Proc()

            cmd += f" -e 'ssh {self.get_ssh_opts()}'"

            if remotesrc:
                src = f"{self.hostname}:{src}"
            if remotedst:
                dst = f"{self.hostname}:{dst}"

        try:
            proc.run_verify(f"{cmd} -- '{src}' '{dst}'")
        except proc.Error as err:
            raise Error(f"failed to copy files '{src}' to '{dst}':\n{err}") from err

    def _scp(self, src, dst):
        """
        Helper that copies 'src' to 'dst' using 'scp'. File names should be already quoted. The
        remote path should use double quoting, otherwise 'scp' fails if path contains symbols like
        ')'.
        """

        opts = f"-o \"Port={self.port}\" -o \"User={self.username}\""
        if self.privkeypath:
            opts += f" -o \"IdentityFile={self.privkeypath}\""
        cmd = f"scp -r {opts}"

        try:
            Procs.run_verify(f"{cmd} -- {src} {dst}")
        except Procs.Error as err:
            raise Error(f"failed to copy files '{src}' to '{dst}':\n{err}") from err

    def get(self, remote_path, local_path):
        """
        Copy a file or directory 'remote_path' from the remote host to 'local_path' on the local
        machine.
        """

        self._scp(f"{self.hostname}:'\"{remote_path}\"'", f"\"{local_path}\"")

    def put(self, local_path, remote_path):
        """
        Copy local file or directory defined by 'local_path' to 'remote_path' on the remote host.
        """

        self._scp(f"\"{local_path}\"", f"{self.hostname}:'\"{remote_path}\"'")

    def cmd_failed_msg(self, command, stdout, stderr, exitcode, startmsg=None, timeout=None):
        """A simple wrapper around '_Common.cmd_failed_msg()'."""

        return _Common.cmd_failed_msg(command, stdout, stderr, exitcode, hostname=self.hostname,
                                      startmsg=startmsg, timeout=timeout)

    def __new__(cls, *_, **kwargs):
        """
        This method makes sure that when users creates an 'SSH' object with 'None' 'hostname', we
        create an instance of 'Proc' class instead of an instance of 'SSH' class. The two classes
        have similar API.
        """

        if "hostname" not in kwargs or kwargs["hostname"] is None:
            return Procs.Proc()
        return super().__new__(cls)

    def _cfg_lookup(self, optname, hostname, username, cfgfiles=None):
        """
        Search for option 'optname' in SSH configuration files. Only consider host 'hostname'
        options.
        """

        old_username = None
        try:
            old_username = os.getenv("USER")
            os.environ["USER"] = username

            if not cfgfiles:
                cfgfiles = []
                for cfgfile in ["/etc/ssh/ssh_config", os.path.expanduser('~/.ssh/config')]:
                    if os.path.exists(cfgfile):
                        cfgfiles.append(cfgfile)

            config = paramiko.SSHConfig()
            for cfgfile in cfgfiles:
                with open(cfgfile, "r") as fobj:
                    config.parse(fobj)

            cfg = config.lookup(hostname)
            if optname in cfg:
                return cfg[optname]
            if "include" in cfg:
                cfgfiles = glob.glob(cfg['include'])
                return self._cfg_lookup(optname, hostname, username, cfgfiles=cfgfiles)
            return None
        finally:
            os.environ["USER"] = old_username

    def _lookup_privkey(self, hostname, username, cfgfiles=None):
        """Lookup for private SSH authentication keys for host 'hostname'."""

        privkeypath = self._cfg_lookup("identityfile", hostname, username, cfgfiles=cfgfiles)
        if isinstance(privkeypath, list):
            privkeypath = privkeypath[0]
        return privkeypath

    def __init__(self, hostname=None, ipaddr=None, port=None, username=None, password="",
                 privkeypath=None, timeout=None):
        """
        Initialize a class instance and establish SSH connection to host 'hostname'. The arguments
        are:
          o hostname - name of the host to connect to
          o ipaddr - optional IP address of the host to connect to. If specified, then it is used
            instead of hostname, otherwise hostname is used.
          o port - optional port number to connect to, default is 22
          o username - optional user name to use when connecting
          o password - optional password to authenticate the 'username' user (not secure!)
          o privkeypath - optional public key path to use for authentication
          o timeout - optional SSH connection timeout value in seconds

        The 'hostname' argument being 'None' is a special case - this module falls-back to using the
        'Procs' module and runs all all operations locally without actually involving SSH or
        networking. This is different to using 'localhost', which does involve SSH.

        SECURITY NOTICE: this class and any part of it should only be used for debugging and
        development purposes. No security audit had been done. Not for production use.
        """

        self.ssh = None
        self.is_remote = True
        self.hostname = hostname
        self.hostmsg = f" on host '{hostname}'"
        self.connection_timeout = timeout
        if port is None:
            port = 22
        self.port = port
        look_for_keys = False
        self.username = username
        self.password = password
        self.privkeypath = privkeypath

        self._sftp = None

        if not self.username:
            self.username = os.getenv("USER")
            if not self.username:
                self.username = _get_username()

        if ipaddr:
            connhost = ipaddr
            printhost = f"{hostname} ({ipaddr})"
        else:
            connhost = self._cfg_lookup("hostname", hostname, self.username)
            if connhost:
                printhost = f"{hostname} ({connhost})"
            else:
                printhost = connhost = hostname

        timeoutstr = str(timeout)
        if not self.connection_timeout:
            timeoutstr = "(default)"

        if not self.privkeypath:
            # Try finding the key filename from the SSH configuration files.
            look_for_keys = True
            with contextlib.suppress(Exception):
                self.privkeypath = Path(self._lookup_privkey(hostname, self.username))

        key_filename = str(self.privkeypath) if self.privkeypath else None

        if key_filename:
            # Private SSH key sanity checks.
            try:
                mode = os.stat(key_filename).st_mode
            except OSError:
                raise Error(f"'stat()' failed for private SSH key at '{key_filename}'") from None

            if not stat.S_ISREG(mode):
                raise Error(f"private SSH key at '{key_filename}' is not a regular file")

            if mode & (stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH):
                raise Error(f"private SSH key at '{key_filename}' permissions are too wide: make "
                            f" sure 'others' cannot read/write/execute it")

        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # We expect to be authenticated either with the key or an empty password.
            self.ssh.connect(username=self.username, hostname=connhost, port=port,
                             key_filename=key_filename, timeout=self.connection_timeout,
                             password=self.password, allow_agent=False, look_for_keys=look_for_keys)
        except paramiko.AuthenticationException as err:
            raise ErrorConnect(f"SSH authentication failed when connecting to {printhost} as "
                               f"'{self.username}':\n{err}") from err
        except Exception as err:
            raise ErrorConnect(f"cannot establish TCP connection to {printhost} with {timeoutstr} "
                               f"secs time-out:\n{err}") from err

        _LOG.debug("established SSH connection to %s, port %d, username '%s', timeout '%s', "
                   "priv. key '%s'", printhost, port, self.username, timeoutstr, self.privkeypath)

    def close(self):
        """Close the SSH connection."""

        if self._sftp:
            sftp = self._sftp
            self._sftp = None
            sftp.close()

        if self.ssh:
            ssh = self.ssh
            self.ssh = None
            ssh.close()

    def _get_sftp(self):
        """Get an SFTP server object."""

        if self._sftp:
            return self._sftp

        try:
            self._sftp = self.ssh.open_sftp()
        except _PARAMIKO_EXCEPTIONS as err:
            raise Error(f"failed to establish SFTP session with {self.hostname}:\n{err}") from err

        return self._sftp

    def open(self, path, mode):
        """
        Open a file on the remote host at 'path' using mode 'mode' (the arguments are the same as in
        the builtin Python 'open()' function).
        """

        def _read_(fobj, size=None):
            """
            SFTP file objects support only binary mode. This wrapper adds basic text mode support.
            """

            try:
                data = fobj._orig_fread_(size=size)
            except BaseException as err:
                raise Error(f"failed to read from '{fobj._orig_fpath_}': {err}") from err

            if "b" not in fobj._orig_fmode_:
                try:
                    data = data.decode("utf8")
                except UnicodeError as err:
                    raise Error(f"failed to decode data read from '{fobj._orig_fpath_}':\n{err}") \
                          from None

            return data

        def _write_(fobj, data):
            """
            SFTP file objects support only binary mode. This wrapper adds basic text mode support.
            """

            if "b" not in fobj._orig_fmode_:
                try:
                    data = data.encode("utf8")
                except UnicodeError as err:
                    raise Error(f"failed to encode data before writing to "
                                f"'{fobj._orig_fpath_}':\n{err}") from None

            errmsg = f"failed to write to '{fobj._orig_fpath_}': "
            try:
                return fobj._orig_fwrite_(data)
            except PermissionError as err:
                raise ErrorPermissionDenied(f"{errmsg}{err}") from None
            except BaseException as err:
                raise Error(f"{errmsg}{err}") from err

        def get_err_prefix(fobj, method):
            """Return the error message prefix."""
            return f"method '{method}()' failed for file '{fobj._orig_fpath_}'"

        path = str(path) # In case it is a pathlib.Path() object.
        sftp = self._get_sftp()

        try:
            fobj = sftp.file(path, mode)
        except _PARAMIKO_EXCEPTIONS as err:
            raise Error(f"failed to open file '{path}' on {self.hostname} via SFTP:\n{err}") \
                  from err

        # Save the path and the mode in the object.
        fobj._orig_fpath_ = path
        fobj._orig_fmode_ = mode

        # Redefine the 'read()' and 'write()' methods to do decoding on the fly, because all files
        # are binary in case of SFTP.
        if "b" not in mode:
            fobj._orig_fread_ = fobj.read
            fobj.read = types.MethodType(_read_, fobj)
            fobj._orig_fwrite_ = fobj.write
            fobj.write = types.MethodType(_write_, fobj)

        # Make sure methods of 'fobj' always raise the 'Error' exception.
        fobj = WrapExceptions.WrapExceptions(fobj, exceptions=_PARAMIKO_EXCEPTIONS,
                                             get_err_prefix=get_err_prefix)
        return fobj

    def __enter__(self):
        """Enter the runtime context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context."""
        self.close()
