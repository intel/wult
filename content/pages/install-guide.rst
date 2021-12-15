.. -*- coding: utf-8 -*-
.. vim: ts=4 sw=4 tw=100 et ai si

=============
Install Guide
=============

.. contents:: Table of Contents

*Wult* is a Python 3 project, but it comes with kernel drivers. Therefore, the basic installation
sequence is:

#. Install *wult* with its dependencies (kernel sources, `pepc`, OS packages)
#. Deploy *wult* drivers

**Important**: *Wult* is a research and debug tool, it loads its own drivers and requires root
privileges. Do not use it on a production system, use it only in a lab environment.

*Wult* installation procedure will vary a little bit depending on whether you prefer the local or
remote usage models (`details here <user-guide.html#usage-models>`_).

1 Standard case (local usage model)
===================================

In the (`local usage model <user-guide.html#local-usage-model>`_):

* *wult* is installed on the SUT (System Under Test)
* drivers are deployed to the SUT
* *wult* measures the SUT and stores the results on the SUT

1.1 Update
----------

Before describing the installation steps, here is a how you update an existing wult
installation. ::

 pip install --user --upgrade git+https://github.com/intel/pepc.git@release
 pip install --user --upgrade git+https://github.com/intel/wult.git@release
 sudo wult deploy

1.2 SUT root access
---------------------

Make sure you have root or `sudo` permissions on the SUT.

1.3 Install dependencies
------------------------

*Wult* has several dependencies. First of all, the sources of the running kernel must be installed
on the SUT. Not just kernel headers for user-space programs, but full kernel source code.

Wult also requires `pepc <https://github.com/intel/pepc>`_ to be installed.
You'll also need the tools necessary for compiling kernel drivers on the SUT: `gcc`, `make`, etc.

In addition to this, *wult* requires various python packages.

.. _kernel-sources:

1.3.1 Kernel sources
++++++++++++++++++++

*Wult* comes with kernel drivers which have to be built for the kernel running on the SUT.

On Fedora and Ubuntu, the sources are typically located in ``/lib/modules/<kernel_version>/build``.
The `<kernel_version>` part must match the kernel running on the SUT. In other words, it has to be
the same as what the `uname -r` command prints when you run it on the SUT.

Unless you are an advanced user, you probably run a stock OS kernel. In this case, it is
enough to just install the kernel sources package provided by the OS, e.g.:

* Fedora: `kernel-devel` package
* Ubuntu: `linux-source` package

Advance users can provide kernel sources path vial `wult deploy` command line options
(see the `wult man page <https://github.com/intel/wult/blob/master/docs/wult-man.rst>`_).

.. _os-packages:

1.3.2 OS packages
+++++++++++++++++

Here are the required OS packages.

**Fedora**

::

 sudo dnf install -y tar bison flex make gcc elfutils-libelf-devel rsync procps-ng
 sudo dnf install -y libffi-devel redhat-rpm-config openssl-devel
 sudo dnf install -y kernel-devel
 sudo dnf install -y git python3 python3-devel python3-pip python3-numpy
 sudo dnf install -y python3-colorama python3-yaml python3-pandas
 sudo dnf install -y  python3-paramiko python3-jinja2 python3-argcomplete

**Ubuntu**

::

 sudo apt install -y bison flex libelf-dev libssl-dev rsync procps
 sudo apt-get source linux-source
 sudo apt install -y git python3-pip python3-numpy python3-plotly
 sudo apt install -y python3-colorama python3-yaml python3-pandas
 sudo apt install -y python3-paramiko python3-jinja2 python3-argcomplete

**Notes**

#. If you do not install some of the python projects installing the corresponding `python3-\*` OS
   packages, they will be pulled by the `pip` tool later when you install *wult*. However, we
   recommend installing `numpy` from OS packages, because it is optimized for the OS.
#. The `git` package is required to make it possible installing *wult* python projects directly from
   their git repository (see below). Otherwise it is not necessary.

1.4 Install pepc
----------------

*Wult* requires another Python3 project to be installed: `pepc <https://github.com/intel/pepc>`.
The `pepc` installation steps are provided in the next section.

1.5 Install wult
----------------

`Wult` and `pepc` are python version 3 projects, and we recommend using the `pip` tool for
installing them. Here is how to install them directly from the `release` branch of their git
repositories: ::

 pip install --user --upgrade git+https://github.com/intel/pepc.git@release
 pip install --user --upgrade git+https://github.com/intel/wult.git@release

1.6 Deploy wult drivers
-----------------------

The final step is to build and deploy wult drivers. Run this command on the SUT as "root". ::

 sudo wult deploy

**Important note**

The drivers are installed only for the currently running kernel. If you reboot the SUT to a
different kernel, you have to re-run `wult deploy`.

1.7 Tab completions
-------------------

`Wult` and `pepc` tools have bash tab completions support, but this will only work if you have
certain environment variables defined. The following commands will do it: ::

 eval $(register-python-argcomplete wult)
 eval $(register-python-argcomplete pepc)

You can put these lines to your `.bashrc` file in order to have `wult` and `pepc` tab completions
enabled by default.


2 Non-standard case (remote usage model)
========================================

In the (`remote usage model <user-guide.html#remote-usage-model>`_):

* *wult* is installed on the controller
* drivers are deployed to the SUT
* *wult* measures the SUT and stores the results on the controller

2.1 Update
----------

Before describing the installation steps, here is a how you update an existing wult
installation. Run the following commands on the controller::

 pip install --user --upgrade git+https://github.com/intel/pepc.git@release
 pip install --user --upgrade git+https://github.com/intel/wult.git@release
 sudo wult deploy -H SUTNAME

.. _passwordless-ssh:

2.2 Passwordless SUT login
--------------------------

In case of the remote usage model, you need to configure passwordless root SSH login from the
controller to the SUT. You are going to run *wult* as a regular user on the controller, but it will
SSH into the SUT as `root`. Please, use online documentation to find out how to do this for your
Linux distribution, but here is one way of doing this (worked on Fedora and Ubuntu).

Configure the SSH server on the SUT to allow for root login by enabling the "PermitRootLogin"
option. Then restart the SSH server. ::

 sudo sh -c 'echo "PermitRootLogin yes" >> /etc/ssh/sshd_config'
 sudo systemctl restart sshd

You'll need user SSH keys on the controller. If you do not have them, generate a new SSH key pair on
the controller. For example, this command (executed as under your user on the controller) will
generate a pair of RSA keys - "sut" (private key) and "sut.pub" (public key): ::

 cd ~/.ssh
 ssh-keygen -t rsa -f sut

And the last step is to configure the controller to use the "~/.ssh/sut" private key when
authenticating to the SUT. You can run something like this on the controller: ::

 cat <<EOF >> ~/.ssh/config
 Host SUTNAME
     IdentityFile ~/.ssh/sut
 EOF

Now you should be able to log in to the SUT as root without typing the password. Test it by running
the following on the controller: ::

 ssh root@SUTNAME

If you still have issues, enable `sshd` debug level logs on the SUT, and check them out, they
usually give very good clues. Use `ssh -v` on the controller to get verbose messages, which also can
give some clues.

2.3 Install dependencies
------------------------

Everything is the same as in the local usage mode, but some of the dependencies should be installed
on the controller instead of the SUT.

2.3.1 Kernel sources
++++++++++++++++++++

Install them on the controller, same way as in the `local usage model case <#os-packages>`_.

2.3.2 OS packages
+++++++++++++++++

Here are the required OS packages.

**Fedora**

SUT: ::

 sudo dnf install -y tar bison flex make gcc elfutils-libelf-devel rsync
 sudo dnf install -y libffi-devel redhat-rpm-config openssl-devel
 sudo dnf install -y kernel-devel

Controller: ::

 sudo dnf install -y git python3 python3-devel python3-pip python3-numpy
 sudo dnf install -y python3-colorama python3-yaml python3-pandas
 sudo dnf install -y  python3-paramiko python3-jinja2 rsync

**Ubuntu**

SUT: ::

 sudo apt install -y bison flex libelf-dev libssl-dev
 sudo apt-get source linux-source

Controller: ::

 sudo apt install -y git python3-pip python3-numpy python3-plotly
 sudo apt install -y python3-colorama python3-yaml python3-pandas
 sudo apt install -y python3-paramiko python3-jinja2 rsync

**Notes**

Same as the `local usage model notes <#kernel-sources>`_.

2.4 Install pepc and wult
-------------------------

Install them on the controller, same way as `in the local usage model case <#install-pepc-wult>`_.

1.6 Deploy wult drivers
-----------------------

Make sure that `passwordless <#passwordless-ssh>`_ SUT access works, then run the following command
on the controller: ::

 sudo wult deploy -H SUTNAME

**Important note**

The drivers are installed only for the currently running kernel. If you reboot the SUT to a
different kernel, you have to re-run `wult deploy -H SUTNAME` on the controller.
