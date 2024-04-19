====
WULT
====

:Date: 2024-03-08
:Title: DEPLOY

.. contents::
   :depth: 3
..

=======================
COMMAND '*wult* deploy'
=======================

usage: wult deploy [-h] [-q] [-d] [--kernel-src KSRC] [--rebuild-bpf]
[--local-build] [--tmpdir-path TMPDIR_PATH] [--keep-tmpdir] [-H
HOSTNAME] [-U USERNAME] [-K PRIVKEY] [-T TIMEOUT] [--skip-drivers]

Compile and deploy wult helpers and drivers to the SUT (System Under
Test), which can be can be either local or a remote host, depending on
the '-H' option. By default, everything is built on the SUT, but the
'--local-build' can be used for building on the local system. The
drivers are searched for in the following directories (and in the
following order) on the local host: ./drivers/idle,
$WULT_DATA_PATH/drivers/idle, $HOME/.local/share/wult/drivers/idle,
/usr/local/share/wult/drivers/idle, /usr/share/wult/drivers/idle. The
wult tool also depends on the following helpers: wult-freq-helper,
wult-hrt-helper, wult-tdt-helper. These helpers will be compiled on the
SUT and deployed to the SUT. The sources of the helpers are searched for
in the following paths (and in the following order) on the local host:
./helpers, $WULT_DATA_PATH/helpers, $HOME/.local/share/wult/helpers,
/usr/local/share/wult/helpers, /usr/share/wult/helpers. By default,
helpers are deployed to the path defined by the 'WULT_HELPERSPATH'
environment variable. If the variable is not defined, helpers are
deployed to '$HOME/.local/bin', where '$HOME' is the home directory of
user 'USERNAME' on host 'HOST' (see '--host' and '--username' options).

OPTIONS *'wult* deploy'
=======================

**-h**
   Show this help message and exit.

**-q**
   Be quiet.

**-d**
   Print debugging information.

**--kernel-src** *KSRC*
   Path to the Linux kernel sources to build drivers and eBPF helpers
   against. The default is '/lib/modules/$(uname -r)/build' on the SUT.
   If '--local-build' was used, then the path is considered to be on the
   local system, rather than the SUT.

**--rebuild-bpf**
   eBPF helpers sources consist of 2 components: the user-space
   component and the eBPF component. The user-space component is
   distributed as a source code, and must be compiled. The eBPF
   component is distributed as both source code and in binary (compiled)
   form. By default, the eBPF component is not re-compiled. This option
   is meant to be used by wult developers to re-compile the eBPF
   component if it was modified.

**--local-build**
   Build helpers and drivers locally, instead of building on HOSTNAME
   (the SUT).

**--tmpdir-path** *TMPDIR_PATH*
   When 'wult' is deployed, a random temporary directory is used. Use
   this option provide a custom path instead. It will be used as a
   temporary directory on both local and remote hosts. This option is
   meant for debugging purposes.

**--keep-tmpdir**
   Do not remove the temporary directories created while deploying
   'wult'. This option is meant for debugging purposes.

**-H** *HOSTNAME*, **--host** *HOSTNAME*
   Name of the host to run the command on.

**-U** *USERNAME*, **--username** *USERNAME*
   Name of the user to use for logging into the remote host over SSH.
   The default user name is 'root'.

**-K** *PRIVKEY*, **--priv-key** *PRIVKEY*
   Path to the private SSH key that should be used for logging into the
   remote host. By default the key is automatically found from standard
   paths like '~/.ssh'.

**-T** *TIMEOUT*, **--timeout** *TIMEOUT*
   SSH connect timeout in seconds, default is 8.

**--skip-drivers**
   Deploy the eBPF helper, but do not deploy the drivers. This is a
   debug and development option, do not use it for other purposes.
