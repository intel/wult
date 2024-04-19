===
NDL
===

:Date: 2024-03-08

.. contents::
   :depth: 3
..

====================
COMMAND *'ndl* scan'
====================

usage: ndl scan [-h] [-q] [-d] [--all] [-H HOSTNAME] [-U USERNAME] [-K
PRIVKEY] [-T TIMEOUT]

Scan for available devices.

OPTIONS *'ndl* scan'
====================

**-h**
   Show this help message and exit.

**-q**
   Be quiet.

**-d**
   Print debugging information.

**--all**
   By default this command prints only the compatible devices which are
   supported by current ndl installation. This option makes this command
   print about all the compatible devices.

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
