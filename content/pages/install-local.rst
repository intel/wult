.. -*- coding: utf-8 -*-
.. vim: ts=4 sw=4 tw=100 et ai si

=========================
Local usage install guide
=========================

:save_as: pages/install-local.html

.. contents:: Table of Contents

This page provides wult installation instruction for the
`local usage model <user-guide.html#local-usage-model>`_.

1 Update
========

Before describing the installation steps, here is a how you update an existing wult
installation. ::

 sudo pip3 install --upgrade git+https://github.com/intel/pepc.git@release
 sudo pip3 install --upgrade git+https://github.com/intel/wult.git@release
 sudo wult deploy

2 Install dependencies
======================

*Wult* has several dependencies. First of all, the sources of the running kernel must be installed
on the SUT. Not just kernel headers for user-space programs, but full kernel source code.

Wult also requires `pepc <https://github.com/intel/pepc>`_ to be installed.
You'll also need the tools necessary for compiling kernel drivers on the SUT: `gcc`, `make`, etc.

In addition to this, *wult* requires various python packages.

.. _kernel-sources:

2.1 Kernel sources
------------------

*Wult* comes with kernel drivers which have to be built for the kernel running on the SUT.

On Fedora and Ubuntu, the sources are typically located in ``/lib/modules/<kernel_version>/build``.
The `<kernel_version>` part must match the kernel running on the SUT. In other words, it has to be
the same as what the `uname -r` command prints when you run it on the SUT.

Unless you are an advanced user, you probably run a stock OS kernel. In this case, it is
enough to just install the kernel sources package provided by the OS, e.g.:

* Fedora: `kernel-devel` package
* Ubuntu: `linux-headers` package

Advanced users can provide custom kernel sources path via `wult deploy` command line options (see
the `wult man page <https://github.com/intel/wult/blob/master/docs/wult-man.rst>`_).

.. _os-packages:

2.2 OS packages
---------------

Here are the required OS packages.

**Fedora**

::

 sudo dnf install -y make gcc elfutils-libelf-devel rsync procps-ng libbpf-devel
 sudo dnf install -y libffi-devel redhat-rpm-config openssl-devel
 sudo dnf install -y kernel-devel
 sudo dnf install -y git python3 python3-devel python3-pip python3-numpy
 sudo dnf install -y python3-colorama python3-yaml python3-pandas
 sudo dnf install -y  python3-paramiko python3-argcomplete

**Ubuntu**

::

 sudo apt install -y make gcc libelf-dev libssl-dev libbpf-dev rsync
 sudo apt install -y linux-headers-$(uname -r)
 sudo apt install -y procps git python3-pip python3-numpy python3-plotly
 sudo apt install -y python3-colorama python3-yaml python3-pandas
 sudo apt install -y python3-paramiko python3-argcomplete

**Notes**

#. If you do not install some of the python projects installing the corresponding `python3-\*` OS
   packages, they will be pulled by the `pip` tool later when you install *wult*. However, we
   recommend installing `numpy` from OS packages, because it is optimized for the OS.
#. The `git` package is required to make it possible installing *wult* python projects directly from
   their git repository (see below). Otherwise it is not necessary.

3 Install wult and pepc
=======================

`Wult` and `pepc` are python version 3 projects, and we recommend using the `pip` tool for
installing them. Here is how to install them directly from the `release` branch of their git
repositories: ::

 sudo pip3 install --upgrade git+https://github.com/intel/pepc.git@release
 sudo pip3 install --upgrade git+https://github.com/intel/wult.git@release

Note, we do not suggest using the `--user` option, because in local usage model `wult` has to
be run with superuser (root) permissions, and `--user` will make this problematic.

4 Deploy wult drivers
=====================

The final step is to build and deploy wult drivers. Run this command on the SUT as "root". ::

 sudo wult deploy

**Important note**

The drivers are installed only for the currently running kernel. If you reboot the SUT to a
different kernel, you have to re-run `wult deploy`.

5 Tab completions
=================

`Wult` and `pepc` tools have bash tab completions support, but this will only work if you have
certain environment variables defined. The following commands will do it: ::

 eval $(register-python-argcomplete wult)
 eval $(register-python-argcomplete pepc)

You can put these lines to your `.bashrc` file in order to have `wult` and `pepc` tab completions
enabled by default.
