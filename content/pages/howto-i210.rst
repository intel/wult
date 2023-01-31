.. -*- coding: utf-8 -*-
.. vim: ts=4 sw=4 tw=100 et ai si

==============
Intel I210 NIC
==============

:slug: howto-i210

.. contents:: Table of Contents

How to use wult with Intel I210 NIC
-----------------------------------

First of all, read `a word of warning here <how-it-works.html#i210-warning>`_.

We recommend to stick with the *hrt* method, but if you have a specific reason to use the *nic*
method with Intel I210, here are some hints.

Make sure to install an Intel I210-based NIC to the SUT (System Under Test) by plugging it into an
appropriate PCIe slot. You do not need to connect the Intel I210 NIC to the network (no cable
needed).

The important thing, however, is that you should not use the I210 NIC for anything else, it has to
be dedicated to *wult*. It is OK to have multiple I210 adapters on your system, as long as one of
them is dedicated to *wult*. Here are two example SUT configurations.

.. image:: ../images/wult-hw-setup.jpg
    :alt: Example wult HW setup for the "nic" measurement method.

In the left picture the SUT has only one NIC dedicated to *wult*. The SUT is not connected to any
network and the user is logged in via a physically attached keyboard and monitor.

In the right picture the SUT is connected to a LAN with another NIC, but it has a separate NIC,
which is dedicated to *wult*. The user is logged in via SSH.

Which Intel I210 NIC to buy
---------------------------

Intel I210 is a 1GbE network chip, several vendors ship (or shipped) network cards based on the I210
chip.  For example, we used the HP I210-T1 Network Adapter (E0X95AA).

There are other adapters out there. If you successfully used some of them with *wult*, let us know
and we'll mention them here.
