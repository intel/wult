.. -*- coding: utf-8 -*-
.. vim: ts=4 sw=4 tw=100 et ai si

=====================
Creating wult reports
=====================

:save_as: pages/howto-create-reports.html

.. contents:: Table of Contents

Include only CC6 datapoints
---------------------------

Suppose you have a raw *wult* result for a Xeon platform, and you want to include only datapoints
with core C6 (CC6) residency in an HTML report. Supposed you do not want to include datapoints with
package C2 (PC2) and package C6 (PC6) residency. Here is how to do this: ::

 wult report --include 'CC6% > 0 & PC6% == 0 & PC2% == 0' <raw_result>

This command specifies the `--include` option which says that *wult* should only select datapoints
with CC6 residency greater than zero and zero PC6/PC2 residency.

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
1000000. You can use the `--include` option to select only the first 10000 datapoints. ::

 $ wult report -o ivt-c6-hfm-nic-vs-tdt --include 'index < 10000' ivt-nic-c6-hfm-noaspm ivt-tdt-c6-hfm-noaspm

 $ du -sh ivt-c6-hfm-nic-vs-tdt
 11M	ivt-c6-hfm-nic-vs-tdt
