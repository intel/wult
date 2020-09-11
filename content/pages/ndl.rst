.. -*- coding: utf-8 -*-
.. vim: ts=4 sw=4 tw=100 et ai si

===
Ndl
===

.. contents:: Table of Contents

Overview
========

*Ndl* is a very specific tool and we did not document it that much. But from the usage perspective
it is very similar to *wult* - supports similar commands and provides similar data analysis
capabilities. It also comes with a man page and the help text. Please, feel free to ask questions by
filing GitHub issues or e-mailing Artem Bityutskiy <dedekind1@gmail.com>.

Principle of operation
======================

Consider a system with a PCIe NIC (Network Interface Card) connected to network. Suppose the CPU is
sitting in a deep C-state, and the NIC starts receiving network packets at high rate. The NIC has
internal buffers to store the incoming network packets, but the buffer is relatively small. The NIC
must start moving the incoming packets from internal buffers to the main memory in parallel with
receiving the packets, otherwise the buffers overflow and some of the packets get lost.

On a typical x86 computer system the main memory is connected to the CPU, and when the CPU is in a
deep enough C-state, the memory is not available to the NIC. Therefore, the NIC must first wake up
the CPU from the deep C-state, which takes some time, and only then it can start offloading
the packets from the internal buffer to the main memory.

Note, in this case CPU does not have to wake up all the way to C0 (executing instruction), it is
enough to wake up to a state where the memory subsystem becomes available. For example, on many
Intel Xeon systems this it is enough to transition to package C2 state (PC2).

The longer it takes to wake up the CPU, the larger internal buffers the NIC should have in order
prevent packets from being lost (dropped). Obviously, the internal buffer size also depends on the
incoming packets rate. But the buffer is going to have some size, and this size will define the
longest tolerable wake up delay. If the CPU is too slow, the NIC has to start dropping incoming
packets.

NDL stands for "Network Drop Latency", and this is the longest memory availability delay the NIC can
tolerate. It is going to be different for different NICs.

The *ndl* tool does not measure the NDL, despite the name. But it measures something similar - the
longest memory availability delay observed by the NIC. We call this metric "RTD", which stands for
"Round-Trip Delay". RTD is basically the time it takes for NIC's memory access request to finish.
The "round-trip" part comes from the fact that NIC's memory access request first leaves the NIC,
travels all the way to the memory, and then the result comes back to the NIC.

Note, *ndl* supports only the Intel i210-based NICs today, so it is a highly specialized tool.

Here is now *ndl* works today.

#. Schedule a delayed network packet to be sent by the NIC in the future (Intel I210 has such a
   capability).
#. Let the system be idle, the CPU enters a deep C-state.
#. When the NIC starts sending the delayed packet, it will first fetch packet data from the main
   memory.
#. The NIC will measure every DMA read transaction and remember the longest one, which is going to
   be the first transaction that woke up the CPU. The longest transaction time is the RTD.
#. *Ndl* reads the measured NDL from the NIC, and saves it in a CSV file.

This process may be repeated tens or hundreds of thousands times. The data are collected in
a CSV file. Ndl provides a capability for analyzing the CSV file (finding the median, percentiles,
etc) as well as a capability for visualizing the test results (scatter plots, histograms).
