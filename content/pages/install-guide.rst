.. -*- coding: utf-8 -*-
.. vim: ts=4 sw=4 tw=100 et ai si

=============
Install Guide
=============

1 Install
=========

.. contents:: Table of Contents

*Wult* is a Python 3 project, but it comes with kernel drivers. Therefore, the basic installation
sequence is:

#. Install *wult* using *pip* (standard Python project installation tool).
#. Install the drivers.

**Important**: *Wult* is a research and debug tool, it loads its own drivers and requires root
privileges. Do not use it on a production system, use it only in a lab environment.

*Wult* installation procedure will vary a little bit depending on whether you prefer the local or
remote usage models (`details here <../index.html#usage-models>`_). In the former case, you install *wult* on the
SUT (System Under Test). In the latter case you install it on the controller. The drivers are
deployed to the SUT. It is also OK to have both setups at the same time.

From now on assume the remote usage model. In case of local usage model the "SUT" and "controller"
are the same system. Here are the main installation steps.

#. Configure the systems (SUT and controller).
#. Install the dependencies on the SUT and the controller.
#. Install *wult* project using *pip* to the controller.
#. Deploy *wult* drivers to the SUT.

1.1 Configure the systems
-------------------------

First of all, make sure you have root or '*sudo*' permissions on both the SUT and the controller.

.. _passwordless-ssh:

1.1.1 Passwordless SUT login
++++++++++++++++++++++++++++

This is only needed for the remote usage model. Skip this step in case of the local usage model

In case of the remote usage model, you need to configure passwordless root SSH login from the
controller to the SUT. You are going to run *wult* as a regular user on the controller, but it will
SSH into the SUT as 'root'. Please, use online documentation to find out how to do this for your
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

1.2 Install dependencies
------------------------

*Wult* has several dependencies. First of all, you'll need the sources of the running kernel sources
must be installed on the SUT. You'll also need the tools necessary for compiling kernel drivers on
the SUT: gcc, make, etc. The controller must have python version 3.6 or higher installed.

1.2.1 Kernel sources
++++++++++++++++++++

*Wult* comes with kernel drivers which have to be built for the kernel running on the SUT. The
drivers are built on the SUT, therefore you should install kernel sources on the SUT. Note, just
user-space headers is not enough, you should install the actual kernel sources.

On Fedora and Ubuntu, the sources are typically located in "/lib/modules/<kernel_version>/build".
The "<kernel_version>" part must match the kernel running on the SUT. In other words, it has to be
the same as what the "uname -r" command prints when you run it on the SUT.

Unless you are an advanced user, you probably run a stock OS kernel on the SUT. In this case, it is
enough to just install the kernel sources package provided by the OS, e.g.:
* Fedora: 'kernel-devel' package
* Ubuntu: 'linux-source' package

If you are an advanced user, you can provide the sources path to the 'wult deploy' command when you
actually build the kernel modules.

1.2.2 OS packages
+++++++++++++++++

There are bunch of other packages that will be needed when using *wult*.

**Fedora**

Here are the packages that will be needed on the SUT (tested in Fedora 28-32). ::

 sudo dnf install -y tar bison flex make gcc elfutils-libelf-devel rsync
 sudo dnf install -y libffi-devel redhat-rpm-config openssl-devel
 sudo dnf install -y kernel-devel

Here are the packages that will be needed on the controller. ::

 sudo dnf install -y git python3 python3-devel python3-pip python3-numpy
 sudo dnf install -y python3-colorama python3-yaml python3-pandas
 sudo dnf install -y  python3-paramiko python3-jinja2 rsync

**Ubuntu**

Here are the packages that will be needed on the SUT. ::

 sudo apt install -y bison flex libelf-dev libssl-dev
 sudo apt-get source linux-source

Here are the packages that will be needed on the controller. ::

 sudo apt install -y git python3-pip python3-numpy python3-plotly
 sudo apt install -y python3-colorama python3-yaml python3-pandas
 sudo apt install -y python3-paramiko python3-jinja2 rsync

**Notes**

#. If you do not install python projects like "numpy" by installing the corresponding "python3-\*" OS
   packages, they will be pulled by the "pip" tool later when you install *wult*.
#. The "git" package is required to make it possible installing *wult* python projects directly from
   their git repository (see below). Otherwise it is not necessary.

1.3 Install wult
----------------

*Wult* is written in python version 3 and the easiest way of installing it is by using the "pip" tool.
Advanced users can chose any other way of using/installing python code, e.g., just clone the git
repositories and configure "PYTHONPATH". But there will be more caveats in this case, and it is
only recommended for advanced users.

Here is how to install *wult* directly from the git repository using the "pip" tool. To install to
your home directory, run: ::

 pip install --user --upgrade git+https://github.com/intel/wult.git@release

This will install *wult* from the "release" branch of the git repository. The "release" branch
contains more stable code. To install the latest code, use the "master" branch instead.

If you prefer installing to the system, remove the '--user' option.

1.4 Deploy wult drivers
-----------------------

When you install *wult*, you will also install the sources of *wult* driver. The next, and final step
is to build and deploy these drivers to the SUT. Use the "wult deploy" command to do this.

In case of the local usage model, run the "wult deploy" command on the SUT as "root". ::

 sudo wult deploy

In case of the remote usage model, run the following command on the controller (as a user, no as
root). ::

 wult deploy -H SUTNAME

If you configured passwordless SSH authentication correctly (see above), this command will SSH to
the SUT (network host name is 'SUTNAME'), copy *wult* driver sources from the controller to the SUT,
build them on the SUT, then deploy them to the SUT.

Please, check 'wult deploy -h' for advanced usage options.

***Note***

The "wult deploy" command installs drivers only to the currently running kernel. If you reboot
your system to a different kernel, you have to re-run "wult deploy". It is on per-kernel basis.


2 Update
--------

If you installed *wult* using the 'pip' tool, you can use 'pip' to update it as well.
Here is how to update *wult* in case you installed it to your home directory. ::

 pip install --user --upgrade git+https://github.com/intel/wult.git@release

And in case you installed it to the system. ::

 sudo -H pip install --upgrade git+https://github.com/intel/wult.git@release

**Important**: you have to re-deploy wult drivers after the update.
`Local usage model <../index.html#local-usage-model>`_: ::

 sudo wult deploy

`Remote usage model <../index.html#remote-usage-model>`_: ::

 wult deploy -H SUTNAME
