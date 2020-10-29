.. -*- coding: utf-8 -*-
.. vim: ts=4 sw=4 tw=100 et ai si

==========
User Guide
==========

.. contents:: Table of Contents

This user guide provides basic *wult* command-line usage instructions. However, there are advanced
commands and options which are not described in this guide. Please, use the '--help' option for more
information. Wult also comes with the man page, but generally, the '--help' contents tends to be
more verbose.

Feel free to ask questions by filing GitHub issues (preferred) or sending an e-mail to
Artem Bityutskiy <dedekind1@gmail.com>.

1. Local vs Remote usage
========================

In case of the `local usage model <../index.html#local-usage-model>`_, *wult* has to be run on the
SUT as 'root'. In case of `remote usage model <../index.html#remote-usage-model>`_, *wult* should be
run on the controller under unprivileged user, but the user should have passwordless root SSH login
from the controller to the SUT (more info in `this <install-guide.html#passwordless-ssh>`_ section).

The command line arguments for the both cases is the same, except for the '-H SUTNAME' option in the
remote usage case, which specifies the SUT host name to connect to.

2. Scan for supported devices
=============================

Start with scanning for supported delayed interrupt source devices. Run the following command on the
SUT in case of the local usage model: ::

 sudo wult scan

or the following command in case of the remote usage model: ::

 wult scan -H SUTNAME

From this point onward, we'll assume the reader already figured out the local vs remote usage mode
difference, and we'll just recommend to run: ::

 wult scan

Here is an example output of 'wult scan': ::

 Compatible device(s):
  * Device ID: tdt
    - Alias: timer
    - Description: TSC deadline timer on CPU0
  * Device ID: 0000:01:00.0
    - Alias: enp1s0
    - Description: Intel I210 (copper). PCI address 0000:01:00.0, Vendor ID 8086, Device ID 0000:01:00.0.
  * Device ID: 0000:31:00.0
    - Alias: enp2s0
    - Description: Intel I210 (copper). PCI address 0000:31:00.0, Vendor ID 8086, Device ID 0000:31:00.0.

The output lists 3 devices that can be used as delayed interrupt sources for *wult*:

* *tdt* - the TCS deadline timer. It was detected on CPU0, but usually if it is present on one CPU,
  then all CPUs have it. You can use both "tdt" and "timer" (alias) to specify this device.
* *0000:01:00.0* - this is the PCI address of the I210 NIC. This NIC is also available under the
  "enp1s0" name, which is actually the Linux network interface name.
* *0000:31:00.0* - another I210 NIC (the "enp2s0" network interface.

The "tdt" devices should always be OK to use for running *wult*. In case of the NIC, only an unused
NIC can be used for running *wult*. What does "unused" mean? Well, it means you do not use this
interface for networking and it is in the "down" state (you can bring it down using 'NetworkManager'
or the 'ip' command).

3. Start the measurements
=========================

Before you start *wult*, you should know which delayed interrupt device you are going to use (see
'wult scan'). Please, make sure to go through `this section <#irq-source>`_ so that you understand
various important settings like PCIe ASPM for the "nic" method.

The basic way to start *wult* is by running 'wult start DeviceID', and 'DeviceID's are provided by
'wult scan'. For example, to run *wult* with the TSC deadline timer, use: ::

 wult start tdt

This command will collect 1000000 datapoints and save them in current directory in a sub-directory
like "wult-tdt-<date>". Here are the main options you should probably use as well.

* '-c' - count of datapoints to collect.
* '--reportid' - report ID of the result. Use a short, but descriptive string to describe the test
  run.
* '-o' - the output directory path.
* '--cpunum' - the CPU to measure the C-state latency on.

There are more options, use 'wult start -h' for help. Here is an example: ::

 $ wult start -c 10000 --reportid all-cstates-enabled tdt
 Compatible device 'TSC deadline timer':
  * Device ID: tdt
    - TSC deadline timer on CPU0
 Binding device 'tdt' to driver 'wult_timer'
 Start measuring CPU 0, collecting 10000 datapoints
 Datapoints: 10000, max. latency: 407051 ns, rate: 472.15 datapoints/sec
 Finished measuring CPU 0

 $ ls all-cstates-enabled/
 datapoints.csv  info.yml

*Wult* collected 10000 datapoints and stored the result in 'all-cstates-enabled' (same as ReportID,
because '-o' was not used). The next step is to generate an HTML report out of the raw result in
'all-cstates-enabled' (or we could use the '--report' option with 'wult start', then it would also
generate the HTML report).

4. Generate HTML report
=======================

The 'wult start' command collects the measurement and saves them in the 'datapoints.csv' file, along
with some additional metadata in the 'info.yml' file. Now what you can do with these raw results?
Well, you can quickly inspect the results using 'wult stats', or generate an HTML report using
'wult report'. Here is how to generate an HTML report for the raw results in
'all-cstates-enabled': ::

 wult report all-cstates-enabled

The result will be in the 'wult-report-all-cstates-enabled' directory. Use '-o' option to specify
where you want the resulting HTML report to be stored.

Note, you can generate a diff - a single HTML report for multiple raw results. Diffs make it easier
to compare test results. Just give 'wult report' multiple test results to generate a diff.

4.1. Advanced example
---------------------

This section describes how `this diff <../results/ivt-c6-hfm-nic-vs-tdt/index.html>`_ was generated.
The diff compares *nic* and *tdt* results for the same system (details
`here <../index.html#_c-state-prewake>`_).

We had two raw test results: ::

 $ ls
 ivt-nic-c6-hfm-noaspm  ivt-tdt-c6-hfm-noaspm

First is for the *nic* method, second is for the *tdt* method. We started with a default
'wult report' options: ::

 $ wult report -o ivt-c6-hfm-nic-vs-tdt ivt-nic-c6-hfm-noaspm ivt-tdt-c6-hfm-noaspm

 $ du -sh ivt-c6-hfm-nic-vs-tdt/
 406M	ivt-c6-hfm-nic-vs-tdt/

This resulted in a 406M HTML report, which is too large to publish in GitHub web pages.

Each raw result contained 1000000 datapoints, which is quite a lot. So we decided to use only 10000
datapoints out of 1M. ::

 $ rm -r ivt-c6-hfm-nic-vs-tdt
 $ wult report -o ivt-c6-hfm-nic-vs-tdt --rsel 'index < 10000' ivt-nic-c6-hfm-noaspm ivt-tdt-c6-hfm-noaspm

 $ du -sh ivt-c6-hfm-nic-vs-tdt
 82M	ivt-c6-hfm-nic-vs-tdt

 $ ls ivt-c6-hfm-nic-vs-tdt/
 CC0_pcnt.html  CC1_pcnt.html  CC3_pcnt.html  CC6_pcnt.html  index.html  LDist.html
 PC2_pcnt.html  PC3_pcnt.html  PC6_pcnt.html  plots  raw-ivt-nic-c6-hfm-aspm
 raw-ivt-tdt-c6-hfm-noaspm  SilentTime.html  style.css

The new diff was 82M, still a little too big. Besides, it contained too many scatter-plots, which
could overwhelm a non-expert. So we decided to strip the C-state scatter-plots and leave only
the wake latency scatter-plot and histogram. ::

 $ wult report -o ivt-c6-hfm-nic-vs-tdt --rsel 'index < 10000' --yaxes WakeLatency \
               --hist WakeLatency --chist none ivt-nic-c6-hfm-noaspm ivt-tdt-c6-hfm-noaspm

 $ du -sh ivt-c6-hfm-nic-vs-tdt
 11M	ivt-c6-hfm-nic-vs-tdt

This 11M diff looked fine and we added it to the web site, as an example.
