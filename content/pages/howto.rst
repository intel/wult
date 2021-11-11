.. -*- coding: utf-8 -*-
.. vim: ts=4 sw=4 tw=100 et ai si

=====
Howto
=====

.. contents:: Table of Contents

.. _wult-report:

Wult report
===========

Include only CC6 datapoints
---------------------------

Suppose you have a raw *wult* result for a Xeon platform, and you want to include only datapoints
with core C6 (CC6) residency in an HTML report. Supposed you do not want to include datapoints with
package C2 (PC2) and package C6 (PC6) residency. Here is how to do this: ::

 wult report --rsel 'CC6% > 0 & PC6% == 0 & PC2% == 0' <raw_result>

This command specifies the "row selector" (`--rsel`) option which says that *wult* should only
select datapoints with CC6 residency greater than zero and zero PC6/PC2 residency.

Fewer datapoints in the HTML report
-----------------------------------

Suppose you have two raw *wult* results: ::

 $ ls
 ivt-nic-c6-hfm-noaspm  ivt-tdt-c6-hfm-noaspm

Suppose the raw results contained 1000000 datapoints and you've generated a diff for them: ::

 $ wult report -o ivt-c6-hfm-nic-vs-tdt ivt-nic-c6-hfm-noaspm ivt-tdt-c6-hfm-noaspm

 $ du -sh ivt-c6-hfm-nic-vs-tdt/
 406M	ivt-c6-hfm-nic-vs-tdt/

Suppose the diff is too large for your purposes (406M), and you want a diff that takes less storage.

One option for you is to include fewer datapoints in the report, for example 10000 instead of
1000000. You can use the `--rsel` option to select only the first 10000 datapoints. ::

 $ wult report -o ivt-c6-hfm-nic-vs-tdt --rsel 'index < 10000' ivt-nic-c6-hfm-noaspm ivt-tdt-c6-hfm-noaspm

 $ du -sh ivt-c6-hfm-nic-vs-tdt
 11M	ivt-c6-hfm-nic-vs-tdt


.. _intel-i210:

Intel I210 NIC
==============

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
