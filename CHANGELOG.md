# Changelog

Changelog practices: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning practices: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [ADD NEW VERSION HERE] - ADD DATE HERE
### Fixed
 - Fix AC Power plot generation failing because of 'inf' values in raw AC Power
   statistic files.
 - Fix 'stats-collect report' crashing on on raw acpower statistic files with
   bad headers.
 - Fix several metrics missing 'min/max' summary functions in 'wult' HTML
   reports.
### Added
 - Add 'tool information' and 'collection date' to 'stats-collect' report intro
   tables.
### Removed
### Changed

## [1.11.5] - 2023-03-16
### Fixed
 - Fix 'stats-collect report' crashing on 'inf' acpower values.
### Changed
 - Change 'stats-collect', 'wult' and 'ndl' to collect 'turbostat' and 'sysinfo'
   statistics by default.

## [1.11.4] - 2023-03-10
### Added
 - Add command used in 'stats-collect start' to 'stats-collect' reports.

## [1.11.3] - 2023-03-03
### Fixed
 - Fix a regression in v1.11.2 where 'sysinfo' tabs would fail to generate
   diffs.

## [1.11.2] - 2023-03-03
### Added
 - Add '--cpunum' option for ndl.

## [1.11.1] - 2023-02-24
### Fixed
 - Fix pepc dependency, allow for pepc versions greater than 1.3.x.

## [1.11.0] - 2023-02-21
### Fixed
 - Fix 'hrt' method failing on AMD systems.
### Added
 - Add module C-state support to turbostat collection and reporting.
 - Add fullscreen view to diagrams in wult HTML reports.
 - Add a button to hide report header in wult HTML reports.

## [1.10.59] - 2023-02-15
### Changed
 - Improve 'tdt' method to be more accurate.
 - Improve 'tdt' method to also work for 'POLL' state.

## [1.10.58] - 2023-02-13
### Added
 - Add basic module C-states support.

## [1.10.57] - 2023-02-10
### Fixed
 - Fix 'wult report' crashing when generating diffs where the first result
   contains different metrics to the rest.
 - Fix 'wult report' crashing when custom axes are provided which result in
   empty tabs.
### Added
 - Add 'pepc topology info' output to 'sysinfo' statistics collection.
 - Add 'pepc topology info' output to 'sysinfo pepc' tab in wult reports.
### Changed
 - Moved the 'Busy%' turbostat tab from 'Misc' to 'C-states,Hardware' in wult
   reports.

## [1.10.56] - 2023-02-02
### Changed
 - Renamed the 'stats-collect-components' JavaScript package to
   '@intc/stats-collect'.

## [1.10.55] - 2023-02-02
### Fixed
 - Fix 'ndl deploy --tmpdir-path' option.
 - Fix 'ndl start' command.
 - Do not crash if the 'systemctl' tool is not available.

## [1.10.54] - 2023-01-13
### Fixed
 - Fix reports generated with 'stats-collect start --report' having no title.
 - Fix 'stats-collect' not maintaining reportid between 'start' and 'report'
   commands.
### Changed
 - Reports generated with 'stats-collect start --report' will now appear in an
   'html-report' sub-directory if no output directory is specified.

## [1.10.53] - 2023-01-12
### Fixed
 - Fix 'wult deploy' crashing (regression in release 1.10.51).

## [1.10.52] - 2023-01-12
### Fixed
 - Fix report generation crashing when a summary table contains more than one
   'N/A' value.
 - Fix 'ndl' manual pages: we mistakingly documented 'wult' tool in 'ndl' man
   page.
### Changed
 - Update 'npm' packages used in wult HTML reports.
 - Generate tabs in wult HTML reports even when one or more results will be
   excluded.

## [1.10.51] - 2023-01-09
### Fixed
 - Fix turbostat totals tabs being unopenable in wult HTML reports.
### Added
 - Add statistics collection support to the 'ndl' tool ('--stats' and
   '--stats-intervals' options).
 - Add 'stats-collect' tool. It is not very useful yet, but it will get more
   functionality later.
 - Add warnings to wult HTML reports when a diagram has been skipped because all
   results contain a single value for a given metric.

## [1.10.50] - 2022-12-23
### Fixed
 - Fix 'wult report' crashing when used on a dataset with very few datapoints.
 - Fix the 'wult start --no-unload' debugging option.
### Changed
 - Improve 'IntrLatency' accuracy for 'hrt' and 'tdt' methods'.

## [1.10.49] - 2022-12-19
### Fixed
 - Fix strange units on the axis of diagrams with 'CPUFreq' data in wult
   reports.
 - Fix regression which caused 'wult deploy' to error when '-H' option was not
   used.

## [1.10.48] - 2022-12-16
### Changed
 - Adjust to 'pepc' project changes again (no functional changes).

## [1.10.47] - 2022-12-16
### Changed
 - Adjust to 'pepc' project changes (no functional changes).

## [1.10.46] - 2022-12-16
### Fixed
 - Fix some statistics being collected for longer than others when 'SysInfo'
   statistics are also collected.

## [1.10.45] - 2022-12-14
### Fixed
 - Fix 'CC0%' calculations in the 'tdt_bpf' method.

## [1.10.44] - 2022-12-10
### Added
 - Add new 'tdt_bpf' method.
### Changed
 - Fix SVOS debianization (missed dependency added).

## [1.10.43] - 2022-12-09
### Changed
 - Stop NTP service when measuring.

## [1.10.42] - 2022-12-09
### Changed
 - Rename the 'hrt-bpf' method to 'hrt_bpf'.
 - Improve precision of the 'hrt' method.

## [1.10.41] - 2022-12-02
### Added
 - Add CPU frequency metric, which now appears as "CPUFreq" in hover text of
   scatter plots.

## [1.10.40] - 2022-11-24
### Fixed
 - Fix 'ndl deploy' command failure.
 - Fix 'wult report' failing if a metric in a summary table contains all zeros.

## [1.10.39] - 2022-11-23
### Added
 - Add "POLL requested %" turbostat tabs to reports.
### Changed
 - The eBPF-based 'hrtimer' method was renamed to 'hrt-bpf'.
 - Fixed and renamed '--title-descr' option to '--report-descr'.

## [1.10.38] - 2022-11-07
### Fixed
 - Fix 'wult start' failing without specifying '--stats none'. This is a regression
   introduced in 1.10.35.

## [1.10.37] - 2022-11-02
### Fixed
 - Fix '--stats all' so that it also collects the "sysinfo" data. This is a regression introduced
   in version 1.10.34.
 - Fix '--stats acpower' - it failed, due to a regression in version 1.10.34.

## [1.10.36] - 2022-10-31
### Changed
 - Debianization: include drivers' sources into the package.

## [1.10.35] - 2022-10-28
### Added
 - Add support for sharing URLs to specific tabs in wult reports.
### Changed
 - Change the wult report layout from nested tabs to use tabs and a tree for
   navigating sub-tabs.

## [1.10.34] - 2022-10-12
### Fixed
 - Fix the 'ipmi' statistics collection.

## [1.10.33] - 2022-09-05
### Fixed
 - Fix 'hrtimer' method's pre-compiled eBPF program.

## [1.10.32] - 2022-09-30
### Fixed
 - Fix 'hrtimer' method's outliers problem by filtering out datapoints that
   included unrelated SW interrupts and NMIs.

## [1.10.31] - 2022-09-22
### Removed
 - Do not collect 'journalctl -b' output as part of the 'sysinfo' statistics.

## [1.10.30] - 2022-09-20
### Removed
 - Remove '--headless' option from 'view_multiple_reports.py'.
 - Remove 'view_report.py' from report directories.
### Changed
 - Increase max. launch distance to 50 milliseconds (tdt, hrt, i210).
 - Rename 'view_multiple_reports.py' to 'serve_directory.py'.
 - Change 'serve_directory.py' so that it does not try to open a web-browser by
   default.

## [1.10.29] - 2022-09-16
### Fixed
 - Do not check for 'stc-agent' and do not complain about its possible absence
   if statistics do not need to be collected.
 - Do not check for kernel sources and do not complain about them missing when
   deploying with the '--skip-drivers' option.
 - Fix missing package C-state tabs in reports
### Added
 - Add the ability to upload a wult report directory if viewing the report
   locally.
 - Add 'RAMWatt' tab to wult reports in the turbostat totals power/temperature
   tab.
### Changed
 - Improve the warning about viewing wult reports locally.

## [1.10.28] - 2022-09-08
### Fixed
 - Minor fix for the 'i210' method: restore network interface operational state
   correctly.
### Added
 - Add '--dir' option to 'view_multiple_reports.py'.
### Changed
 - Wult report viewing scripts now tries multiple ports before failing.

## [1.10.27] - 2022-09-07
### Fixed
 - Wult mistakenly required the 'ip' tool to be installed, this is fixed now.
### Added
 - New 'wult scan --all' option to print unsupported devices.
### Changed
 - 'wult deploy --skip-drivers' does not require kernel sources any longer.
 - Merge and simplify the 'SilentTime' and 'LDist' tabs in wult reports.
 - 'wult scan' does not print unsupported devices by default.

## [1.10.26] - 2022-09-05
### Fixed
 - Do not error out when CC0 cycles is greater than total cycles. Just warn
   instead. We observe this with 'POLL' C-state on some platforms.
 - Fix for the problem of extremely slow data rate when measuring the 'POLL'
   state using the 'hrt' method.
### Added
 - Add '--host', '--port' and '--headless' options to report viewing scripts.
### Removed
 - Remove the '--size=medium' report option.

## [1.10.25] - 2022-08-31
### Changed
 - Reworked the deployment code to better support RPM packaging.

## [1.10.24] - 2022-08-29
### Fixed
 - Fix regression introduced in 1.10.23: we failed to find helpers when they
   were not in '$PATH'.

## [1.10.23] - 2022-08-29
### Changed
 - Change 'wult' to not expect driver/helper sources be available - they are
   not available when installed from an OS package, such as an RPM package.
 - Change the way 'wult' tool looks for installed drivers and helpers in order
   to support RPM packaging.

## [1.10.22] - 2022-08-28
### Fixed
 - Fix C-state tabs being excluded from wult HTML reports generated with
   '--size=large'.
### Added
 - Add 'wult deploy --skip-drivers' option, useful for debug and development.

## [1.10.21] - 2022-08-22
### Fixed
 - Fix the problem of progress line for 'tdt': it always printed 0 max. latency.

## [1.10.20] - 2022-08-19
### Fixed
 - Fix wult deploy regression where 'stc-agent' failed to deploy.
### Added
 - Always deploy eBPF helpers, making the new "hrtimer" method available by
   default.

## [1.10.19] - 2022-08-19
### Fixed
 - Fix compatibility of wult report viewing scripts for Python 3.5+.
 - Fix wult report failing because it can't find scripts for viewing reports.
### Changed
 - wult now restores i210 network interface state after the measurement.

## [1.10.18] - 2022-08-17
### Fixed
 - Fix nic method-only regression introduced in 1.10.0: 'WarmupDelay' and
   'LatchDelay' metrics were not saved in the CSV file.

## [1.10.17] - 2022-08-16
### Added
 - Add local viewing scripts to each wult HTML report.

## [1.10.16] - 2022-08-16
### Fixed
 - Fix occasional crash: KeyError: 'IntrLatencyRaw'.
### Added
 - Added new 'hrtimer' method, which is based on eBPF and does not require
   kernel drivers. This method is considered to be experimental for now, and
   eBPF helpers are not deployed by default. Use 'wult deploy --deploy-bpf' to
   deploy them.
### Removed
 - Remove the "hrtimer" alias for the "hrt" method.
 - Remove the "tsc-deadline-timer" alias for the "tdt" method.
### Changed

## [1.10.15] - 2022-08-10
### Fixed
 - Fix failure when setting large launch distance (>4ms).
### Changed
 - Max. launch distance changed from 10ms to 20ms.

## [1.10.14] - 2022-08-05
### Changed
 - Move scripts for local reports viewing to 'misc/servedir'.

## [1.10.13] - 2022-08-05
### Added
 - Add turbostat data to the "Info" tab.
 - Add misc. scripts for viewing wult reports locally.

## [1.10.12] - 2022-08-01
### Fixed
 - Fix crash related to 'IntrLatency' (regression in v1.10.11).
### Changed
 - Change 'wult start --list-stats' to not require device id.

## [1.10.11] - 2022-07-18
### Fixed
 - Fix the 'wult start --early-intr' option.
 - Fix 'wult report' generating broken HTML reports for reports with no
   common IPMI metrics.
 - Fix HTML report screen tearing which appeared after switching tabs many
   times.
### Added
 - Add 'dmesg', 'lspci', 'cpuidle' and 'cpufreq' to the "SysInfo" tabs in
   HTML reports.
 - Add buttons to the "SysInfo" tab to open raw files in a separate tab.
### Removed
 - Remove the 'wult start --intr-focus' option.
### Changed
 - Changed 'wult report' so that reports will be generated with logs by default.

## [1.10.10] - 2022-07-15
### Fixed
 - Fix crashes with kernels version 5.18+ on C-states entered with interrupts
   enabled.
 - Remove bogus 'IntrLatency' data when using the 'tdt' method.
### Added
 - wult report: add "SysInfo" tab with various system info about SUTs.
### Changed
 - Optimization: spend time calculating TSC rate only in case of the TDT method.
  Skip this step for the HRT/NIC methods.

## [1.10.9] - 2022-07-06
### Changed
 - Minor improvements required for RPM packaging

## [1.10.8] - 2022-06-29
### Fixed
 - Fix regression in v1.10.7: turbostat statistics collector was crashing.

## [1.10.7] - 2022-06-28
### Fixed
 - Fix regression in v1.10.1: generated scatter plots were too large.
### Changed
 - Add 'UncMHz' (uncore frequency) turbostat metric support.
 - Improve Turbostat metrics description by specifying the aggregation method
   (whether it is max or average of values for all CPUs).

## [1.10.6] - 2022-06-24
### Changed
 - wult: add package C-states to turbostat statistics.
 - wult: add current and voltage to IPMI statistics.
 - Add RPM packaging support.

## [1.10.5] - 2022-06-09
### Changed
 - wult: fix crashes on systems that do not have 'python' in PATH.

## [1.10.4] - 2022-06-06
### Changed
 - wult: fix crash with when unknown method is given (regression in 1.10.0).

## [1.10.3] - 2022-06-03
### Changed
 - wult/ndl: rename the '--list-columns' option to '--list-metrics'.
 - wult/ndl: rename the '--rsel' option '--include'.
 - wult/ndl: rename the '--rfil' option '--exclude'.
 - wult/ndl: rename the '--csel' option '--include-metrics'.
 - wult/ndl: rename the '--cfil' option '--exclude-metrics'.
 - wult: do not check for 'bpftool' and 'clang' dependency unnecessarily.
 - ndl: fail gracefully on 'ndl start tdt'.

## [1.10.2] - 2022-05-31
### Changed
 - wult: fix missing C-states residencies (regression in 1.10.0).
 - wult report: fix '--size large'.

## [1.10.1] - 2022-05-30
### Changed
 - wult deploy: fix deploying from sources.
 - wult start --stats: fix statistics collection when run from sources.
 - wult stats: fix standalone stats-collect dependencies.

## [1.10.0] - 2022-05-25
### Changed
 - wult report: removed symbolic links to raw result files.
 - wult report: changed '--relocatable' to be a binary option.
 - wult report: added turbostat statistics tab.
 - wult: removed 'start --dirty-cpu-cache' option/capability.
 - wult: removed 'wult load' debug command.
 - wult/ndl deploy: fix '--kernel-src' option which did not work.
 - wult/ndl deploy: add '--local-build' option.

## [1.9.20] - 2022-04-06
### Changed
 - Fix crash when using 'wult calc --rsel'.

## [1.9.19] - 2022-03-22
### Changed
 - wult report: fix crash introduced in version 1.9.18.

## [1.9.18] - 2022-03-18
### Changed
 - wult report: added AC power and IPMI statistics visualization.

## [1.9.17] - 2022-03-11
### Changed
 - wult: bugfix release: suggest users how to view local HTML reports.

## [1.9.16] - 2022-02-15
### Changed
 - wult: bugfix release: improve TDT driver skipping datapoints error diagnostic.

## [1.9.15] - 2022-02-11
### Changed
 - wult: bugfix release: fix HTML report summary table hover text.

## [1.9.14] - 2022-02-11
### Changed
 - wult: removed 'start --offline' option.
 - wult: browsers now load wult HTML reports faster.

## [1.9.13] - 2022-02-01
### Changed
 - wult: bugfix release: fix raw filters on system with older pandas/numexpr.

## [1.9.12] - 2022-01-30
### Changed
 - wult: bugfix release: fix crash when running 'wult report --list-columns'.

## [1.9.11] - 2022-02-28
### Changed
 - wult: bugfix release: fix 'ndl start' not finding the driver.
 - wult: bugfix release: fix 'wult scan' not resolving network name.

## [1.9.10] - 2021-12-14
### Changed
 - wult: bugfix release: fix occasional missing 'WakeLatencyRaw' crash.

## [1.9.9] - 2021-11-12
### Changed
 - wult: bugfix release: fixed data rate, requires pepc 1.1.2.

## [1.9.8] - 2021-10-08
### Changed
 - wult: add 'start --dirty-cpu-cache' option/capability.
 - wult/ndl: use modules from the 'pepc' project (new dependency).
 - wult: calculate TSC rate and improve measurements accuracy.
 - wult: this version requres pepc v1.1.1.

## [1.9.7] - 2021-09-09
### Changed
 - wult: add 'start --early-intr' option/capability.
 - wult/ndl: add 'report --relocatable=noraw' support.

## [1.9.6] - 2021-09-09
### Changed
 - wult: improve driver error diagnostics.
 - wult: stop supporing kernels older than v5.6.
 - wult: add 'start --intr-focus' option/capability.
 - wult: add 'start --keep-raw-data' option.
 - wult: add 'start --offline' option/capability.
 - wult: add 'filter --human-readable' option.
 - wult/ndl: removed '--post-trigger' option/capability.

## [1.9.5] - 2021-07-30
### Changed
 - wult: many fixes for small, but annoying problems

## [1.9.4] - 2021-07-19
### Changed
 - wult/ndl: speed up measuring remote SUTs.

## [1.9.3] - 2021-06-29
### Changed
 - wult: add new driver: hrtimer.
 - wult: add POLL idle state support.
 - wult/ndl: add '--keep-filtered' option for start command.
 - wult/ndl: remove broken "advanced" options.
 - wult: fix 'stats-collect' deployment.

## [1.9.2] - 2021-05-28
### Changed
 - wult: add statistics collection capability.
 - wult: include less diagrams into report by default.
 - wult: change default launch distance range from 0-8ms to 0-4ms.
 - wult: fix false warning about C-state prewake setting.
 - wult: add row filter and selector options '--rfilt' and '--rsel'.

## [1.9.1] - 2021-04-09
### Changed
 - wult: fix regression and do not fail with pre-v5.6 kernels.
 - wult: fix warnings for old kernels (pre-v5.3).
 - wult: improve Icelake-D support.
 - wult: fix a failure acception an i210 NIC by its PCI ID.
 - wult: fix interrupt latency figures.

## [1.9.0] - 2021-03-25
### Changed
 - wult: add new 'CStates%' metric for combined C-state residency.
 - wult: print helpful message about settings possibly affecting results.
 - wult/ndl: deprecate '--continue' and add '--start-over' instead.
 - man: generate man pages using 'argparse-manpage' tool.
 - wult: add support to configure dynamic load line feature.
 - wult: add the 'IntrLatency' metric (interrupt latency).
 - wult: add the 'NMIWake' and 'NMIIntr' metrics (NMI counts).
 - wult: add the 'IntrDelay' metric (interrupt delay).
 - wult: fix starting by NIC PCI ID

## [1.8.14] - 2021-03-09
### Changed
 - wult/ndl: print helpful message if ASPM is enabled.
 - wult/ndl: fix permission issues for copied raw results.
 - wult: fix '--ldist' option, it did not work in local mode.
 - wult: change default launch distance range from 0-4ms to 0-8ms.
 - wult/ndl: optimize remote MSR access.
 - wult/ndl: suggest OS package names for tools that should be installed.
 - wult/ndl: improve error message when opening wult result with ndl.
 - wult/ndl: check if we already have enough datapoints earlier.

## [1.8.13] - 2021-03-09
### Changed
 - Same as 1.8.12, we messed up verion numbers a bit.

## [1.8.12] - 2021-02-11
### Changed
 - ndl: add --xases, --yaxes, --hist and --chist options to 'ndl report' command.
 - wult: include 'ReqCState' metric to the HTML report.
 - ndl: add 'ndl scan' command.
 - wult: fix bug in diff report with old results.

## [1.8.11] - 2021-01-13
### Changed
 - wult/ndl: add the '--time-limit' option.
 - wult/ndl: support specifiers in '--ldist'.
 - wult: support specifiers in '--post-trigger-range'.
 - wult: support 0 in '--ldist'.
 - ndl: removed the '--cstate-stats' option.
 - ndl: fix parsing the 'tc' tool version number.
 - wult/ndl: rename the 'stats' command into 'calc'.
 - wult: add SilentTime vs LDist diagram.
 - wult: do not fail when events are lost.
 - ndl: replace '--post-trigger-threshold' with '--post-trigger-range'.

## [1.8.10] - 2020-11-30
### Changed
 - wult/ndl: distinguish between CC1% (HW) and DerivedCC1% (SW).

## [1.8.9] - 2020-11-30
### Changed
 - wult/ndl: add '--reportids' command-line option.

## [1.8.8] - 2020-10-30
### Changed
 - wult: add '--hist none' and '--chist none' support.
 - wult: improve 'wult scan' to print aliases.
 - wult: renamed 'tsc-deadline-timer' method to shorted 'tdt'.

## [1.8.7] - 2020-10-21
### Changed
 - wult: first release.
