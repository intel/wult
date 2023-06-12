.. -*- coding: utf-8 -*-
.. vim: ts=4 sw=4 tw=100 et ai si

==========================
Remote usage install guide
==========================

:slug: install-remote

.. contents:: Table of Contents

In the `remote usage model <user-guide.html#remote-usage-model>`_:

* *wult* is installed on the controller
* drivers are deployed to the SUT
* *wult* measures the SUT and stores the results on the controller

In general, following the `local usage install guide <install-local.html>`_ and install *wult* to
the controller. This page provides the delta (what should be done differently or additional
aspects).

1 Update
=========

Update the packages using the same method as described for `local installation
<install-local.html#installation_instructions>`_ but run the `wult deploy` command with `-H SUTNAME`
to deploy `wult` to the SUT and not locally, i.e::

 wult deploy -H SUTNAME

2 OS packages
=============

Everything is the same as in the local usage mode, but some of the dependencies should be installed
on the SUT instead of the controller.

**Fedora**

SUT: ::

 sudo dnf install -y make gcc elfutils-libelf-devel rsync libbpf-devel
 sudo dnf install -y libffi-devel redhat-rpm-config openssl-devel
 sudo dnf install -y kernel-devel

Controller: ::

 sudo dnf install -y git python3 python3-devel python3-pip python3-numpy
 sudo dnf install -y python3-colorama python3-yaml python3-pandas
 sudo dnf install -y python3-paramiko rsync

**Ubuntu**

SUT: ::

 sudo apt install -y make gcc libelf-dev libssl-dev libbpf-dev
 sudo apt install -y linux-headers-$(uname -r)

Controller: ::

 sudo apt install -y git python3-pip python3-numpy python3-plotly
 sudo apt install -y python3-colorama python3-yaml python3-pandas
 sudo apt install -y python3-paramiko rsync

3 Install wult, stats-collect and pepc
======================================

Install them on the controller using the same method described for `local installation
<install-local.html#installation_instructions>`_.

4 Deploy wult drivers
=====================

Make sure that `passwordless <#passwordless-ssh>`_ SUT access works, then run the following command
on the controller: ::

 wult deploy -H SUTNAME

**Important note**

The drivers are installed only for the currently running kernel. If you reboot the SUT to a
different kernel, you have to re-run `wult deploy -H SUTNAME` on the controller.

.. _passwordless-ssh:

4.1 Passwordless SUT login
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
