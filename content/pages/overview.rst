.. -*- coding: utf-8 -*-
.. vim: ts=4 sw=4 tw=100 et ai si

========
Overview
========

:save_as: index.html
:url: index.html

**Important note**: both *wult* and *ndl* are research, debugging and tracing tools which require
superuser privileges and must not be used in production environment.

.. contents:: Table of Contents

1 Introduction
==============

*Wult* stands for "Wake Up Latency Tracer", and this is a project providing tools for measuring
C-state latency in Linux. The project provides 2 tools:

* *wult* - measures CPU C-state exit latency in Linux. This is the main deliverable of the project.
* *ndl* - measures the memory access latency observed by a PCIe network card when the CPU is is
  in a C-state. However, this tool is rarely used, and it is documented separately
  `here <pages/ndl.html>`_.

2 Documentation
===============

These web pages are the primary source of *wult* and *ndl*. In addition to this, man pages include many
details:

* `Wult man page <https://github.com/intel/wult/blob/master/docs/wult-man.rst>`_.
* `Ndl man page <https://github.com/intel/wult/blob/master/docs/ndl-man.rst>`_.

Here is an `old wult presentation video recording <https://youtu.be/Opk92aQyvt0?t=8270>`_
by Artem Bityutskiy at Linux Plumbers Conference in 2019. The presentation begins at "2:17:50" and
it gives a high level *wult* introduction.

The presentation focuses on *wult* kernel drivers, but some of the details are out of date.

* The presentation is focused around the I210 NIC measurement method, but nowadays *wult* supports the
  *hrt* method, which is the recommended method. This method does not require any special hardware,
  such as a NIC. Use *hrt* unless you have a good reason using the NIC method.
* Nowadays we measure both wake latency (*WakeLatency*) and (*IntrLatency*). The latter is the time
  it takes to the CPU to exit the C-state and execute the interrupt handler.

And finally, if you do not find the information you are looking for, feel free to ask questions by
filing GitHub issues or sending an e-mail to Artem Bityutskiy <dedekind1@gmail.com>.
