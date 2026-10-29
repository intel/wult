<!--
-*- coding: utf-8 -*-
vim: ts=4 sw=4 tw=100 et ai si

# Copyright (C) 2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
-->

# Wult Data

## Table of Contents

- [Wult Data](#wult-data)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Data From the Driver](#data-from-the-driver)
    - [Methods](#methods)
    - [Core Metrics](#core-metrics)
    - [C-State Residency Metrics](#c-state-residency-metrics)
    - [i210-Specific Metrics](#i210-specific-metrics)
  - [Data From User-Space](#data-from-user-space)
    - [Time Metrics](#time-metrics)
    - [Other Metrics](#other-metrics)
  - [Overhead](#overhead)
    - [After-Idle Code and Interrupt Handler](#after-idle-code-and-interrupt-handler)
    - [The Problem](#the-problem)
    - [The Mitigation](#the-mitigation)
  - [C-State Residency](#c-state-residency)
  - [Interrupt Order Detection](#interrupt-order-detection)
  - [TSC Rate](#tsc-rate)
  - [CPU Frequency](#cpu-frequency)
  - [Adjustments (i210-only)](#adjustments-i210-only)
    - [How the NIC Time Is Read](#how-the-nic-time-is-read)
    - [The Problem](#the-problem-1)
    - [The Mitigation](#the-mitigation-1)

## Overview

This document describes the data that `wult` collects and stores.

The data is produced and stored in the following steps.

1. The `wult` kernel driver takes time-stamps and other statistics around idle state entry/exit
   points, and sends them to user-space via the `wult_cpu_idle` synthetic trace event.
2. User-space receives the driver data.
3. User-space calculates the final metrics based on the driver data.
4. User-space saves the metrics in the `datapoints.csv` file. Each row of the file is one datapoint.

By default, `wult start` strips the `datapoints.csv` file to keep it small. Most of the data
produced by the kernel driver, for example the raw time-stamps, are dropped, and only the processed
metrics are saved. To save all the driver data, use the `--keep-raw-data` option of `wult start`.

## Data From the Driver

### Methods

There are 3 measurement methods, each with its own driver.

- `tdt` (driver `wult_tdt`) - Uses TSC as the time source. Events are armed with an hrtimer, and the
  launch time is taken from the x86 TSC deadline timer register (`MSR_IA32_TSC_DEADLINE`, 0x6E0) for
  higher precision.
- `hrt` (driver `wult_hrt`) - Uses the Linux `CLOCK_MONOTONIC` clock as the time source and an
  hrtimer as the event.
- `i210` (driver `wult_igb`) - Uses the Intel I210 NIC clock as the time source and a NIC interrupt
  as the event.

The methods work similarly, but the data they generate differs slightly. The time metrics (`LTime`,
`TBI`, `TAI` and `TIntr`) have the following values:

- `tdt`: TSC counter value of the measured CPU, in TSC cycles.
- `hrt`: `CLOCK_MONOTONIC` value, in nanoseconds.
- `i210`: NIC clock value, in nanoseconds.

### Core Metrics

- `LDist`: Launch distance, the time in nanoseconds from arming the event to when it should fire.
- `LTime`: Launch time, the absolute time the event was scheduled for.
- `TBI`: Time before idle, read with interrupts disabled just before entering idle.
- `TAI`: Time after idle, read in the after-idle code that follows the `MWAIT` instruction. It is
  not read right after exiting idle if the interrupt handler runs first. See
  [After-Idle Code and Interrupt Handler](#after-idle-code-and-interrupt-handler).
- `TIntr`: Time read in the interrupt handler.

The picture below illustrates these metrics. It shows the most common case, when the after-idle code
runs before the interrupt handler. See
[After-Idle Code and Interrupt Handler](#after-idle-code-and-interrupt-handler) for details.

```text
    | set up |      CPU is in C-state       | C-state exit | after-idle code | interrupt handler |
    +--------+------------------------------+--------------+-----------------+-------------------+
    ^        ^                              ^               ^                 ^
    arm      TBI                            LTime           TAI               TIntr
    |<--------------- LDist --------------->|
```

- `ReqCState`: Index of the C-state requested by the idle governor. It is the `<index>` in the
  `/sys/devices/system/cpu/cpu*/cpuidle/state<index>` sysfs directory of the C-state.
- `AITS1`, `AITS2`: `CLOCK_MONOTONIC` time in nanoseconds at the start and at the end of the
  after-idle code. See [Overhead](#overhead).
- `IntrTS1`, `IntrTS2`: `CLOCK_MONOTONIC` time in nanoseconds at the start and at the end of the
  interrupt handler. See [Overhead](#overhead).
- `TotCyc`: Total TSC cycles in the measurement interval. See
  [C-State Residency](#c-state-residency).
- `CC0Cyc`: Cycles the CPU spent in C0, counted by `MPERF` in the measurement interval. `MPERF`
  ticks at a rate close to the TSC rate. See [C-State Residency](#c-state-residency).
- `SMICnt`: Number of SMIs that happened between before idle and the interrupt, read from
  `MSR_SMI_COUNT` (0x34). Intel only, zero on other CPUs.
- `NMICnt`: Number of NMIs that happened between before idle and the interrupt.
- `AIAperf`, `IntrAperf`: Raw `APERF` value after idle and in the interrupt handler. `APERF` ticks
  at the actual core clock rate. See [CPU Frequency](#cpu-frequency).
- `AIMperf`, `IntrMperf`: Raw `MPERF` value after idle and in the interrupt handler. `MPERF` ticks
  at a rate close to the TSC rate. See [CPU Frequency](#cpu-frequency).
- `BICyc`: TSC counter value of the measured CPU read before idle, taken close to `BIMonotonic`. See
  [TSC Rate](#tsc-rate).
- `BIMonotonic`: `CLOCK_MONOTONIC` time in nanoseconds read before idle. See [TSC Rate](#tsc-rate).

### C-State Residency Metrics

The driver provides a `<name>Cyc` metric for each C-state residency counter. The value is the
counter delta over the measurement interval, in cycles at a rate close to the TSC rate. See
[C-State Residency](#c-state-residency) for more info.

The metrics are present only for the counters that are readable and non-zero at driver
initialization time. The possible metrics are:

- Core C-states:
  - `CC1Cyc` (`MSR_CORE_C1_RES`, 0x660)
  - `CC3Cyc` (`MSR_CORE_C3_RESIDENCY`, 0x3FC)
  - `CC6Cyc` (`MSR_CORE_C6_RESIDENCY`, 0x3FD)
  - `CC7Cyc` (`MSR_CORE_C7_RESIDENCY`, 0x3FE)
- Module C-state:
  - `MC6Cyc` (`MSR_MODULE_C6_RES_MS`, 0x664)
- Package C-states:
  - `PC2Cyc` (`MSR_PKG_C2_RESIDENCY`, 0x60D)
  - `PC3Cyc` (`MSR_PKG_C3_RESIDENCY`, 0x3F8)
  - `PC6Cyc` (`MSR_PKG_C6_RESIDENCY`, 0x3F9)
  - `PC7Cyc` (`MSR_PKG_C7_RESIDENCY`, 0x3FA)
  - `PC8Cyc` (`MSR_PKG_C8_RESIDENCY`, 0x630)
  - `PC9Cyc` (`MSR_PKG_C9_RESIDENCY`, 0x631)
  - `PC10Cyc` (`MSR_PKG_C10_RESIDENCY`, 0x632)

### i210-Specific Metrics

These metrics are specific to the `i210` method. The other methods always set the `*Adj` metrics to
zero, and do not provide the other metrics. The `*Adj` metrics are described in
[Adjustments](#adjustments-i210-only).

- `TBIAdj`: Adjustment for the error of `TBI`, in nanoseconds.
- `TAIAdj`: Adjustment for the error of `TAI`, in nanoseconds.
- `TIntrAdj`: Adjustment for the error of `TIntr`, in nanoseconds.
- `WarmupDelay`: Duration of the PCI "warm up" read of the pending IRQ status (`ICS`, 0x1504) after
  idle, in `CLOCK_MONOTONIC` nanoseconds. See [The Mitigation](#the-mitigation-1).
- `LatchDelay`: Duration of the NIC time latch read (`SYSTIMR`, 0xB6F8) after idle, in
  `CLOCK_MONOTONIC` nanoseconds. See [How the NIC Time Is Read](#how-the-nic-time-is-read).

## Data From User-Space

User-space takes the raw datapoints from the driver, calculates the final metrics, and saves them in
`datapoints.csv`. The time metrics are saved in microseconds, even though the driver provides them
in nanoseconds or TSC cycles.

### Time Metrics

These metrics are calculated from the time-stamps provided by the driver.

- `WakeLatency`: The time from the event to the moment the CPU started executing instructions after
  the wake-up. It is `TAI` - `LTime`.
- `IntrLatency`: The time from the event to the moment the interrupt handler started running. It is
  `TIntr` - `LTime`.
- `SilentTime`: The time the CPU spent in the C-state before the event. It is `LTime` - `TBI`.

The picture below shows the metrics. It shows the most common case, when the after-idle code runs
before the interrupt handler. See
[After-Idle Code and Interrupt Handler](#after-idle-code-and-interrupt-handler). Time flows from
left to right.

```text
    |   CPU is in C-state   |      C-state exit      |    after-idle code    | interrupt handler |
    +-----------------------+------------------------+-----------------------+-------------------+
    ^                       ^                         ^                       ^
   TBI                     LTime                     TAI                     TIntr
    |<---- SilentTime ----->|
                            |<----- WakeLatency ----->|
                            |<----------------- IntrLatency ----------------->|
```

In reality, user-space applies 2 corrections to the metrics:

- Measurement overhead (all methods): One Wult code block delays the other, which inflates one of
  the latencies. See [Overhead](#overhead) for details.
- Time-stamp error (`i210` only): Reading the NIC time is slow, so `TBI`, `TAI` and `TIntr` are off.
  The driver estimates the errors in the `*Adj` metrics. See [Adjustments](#adjustments-i210-only).

The latencies before the corrections are also saved, in the metrics with the `Raw` suffix. Here are
the full formulas, where `IntrOff` tells which code block runs first. See
[Interrupt Order Detection](#interrupt-order-detection):

- `WakeLatencyRaw`: `TAI` - `LTime`
- `WakeLatency`:
  - `IntrOff` is true: `WakeLatencyRaw` - `TAIAdj`
  - `IntrOff` is false: `WakeLatencyRaw` - `TAIAdj` - (`IntrTS2` - `IntrTS1`)
- `IntrLatencyRaw`: `TIntr` - `LTime`
- `IntrLatency`:
  - `IntrOff` is true: `IntrLatencyRaw` - `TIntrAdj` - (`AITS2` - `AITS1`)
  - `IntrOff` is false: `IntrLatencyRaw` - `TIntrAdj`
- `SilentTime`: `LTime` - `TBI` - `TBIAdj`

The `*Adj` metrics are zero for all methods except `i210`. The formulas use nanoseconds. For `tdt`,
user-space first converts the TSC cycles to nanoseconds. See [TSC Rate](#tsc-rate). The results are
saved in `datapoints.csv` in microseconds.

### Other Metrics

- `IntrOff`: True if the after-idle code ran before the interrupt handler, false otherwise. See
  [Interrupt Order Detection](#interrupt-order-detection).
- `ReqCState`: Name of the C-state requested by the idle governor, for example `C1E`. The driver
  provides only the index of the C-state, and user-space converts it to the name.
- `CPUFreq`: CPU frequency after the wake-up, in MHz. See [CPU Frequency](#cpu-frequency).
- `CC0%`, `CC1%`, `PC6%` and similar: C-state residency percentages. See
  [C-State Residency](#c-state-residency).
- `CC1Derived%`: C1 residency derived from the other C-state residencies. See
  [C-State Residency](#c-state-residency).

The following metrics are passed from the driver as-is, except that the time metrics are converted
to microseconds: `LDist`, `SMICnt`, `NMICnt`, `WarmupDelay` and `LatchDelay`.

## Overhead

### After-Idle Code and Interrupt Handler

After the CPU wakes up, the driver takes measurements in two places:

- The after-idle code, which reads `TAI`.
- The interrupt handler, which reads `TIntr`.

They run one after the other, and the order depends on the C-state and the platform.

- `TAI`, then `TIntr` - The C-state is entered with interrupts disabled. This is the order in the
  vast majority of cases. The after-idle code runs first, and the interrupt handler runs after the
  kernel re-enables interrupts.
- `TIntr`, then `TAI` - The C-state is entered with interrupts enabled. This is rare. The examples
  are POLL on all platforms, and C1 on Ice Lake Xeon with current Linux kernels. The interrupt
  handler runs first, and the after-idle code runs after it.

**Note**: User-space records which case applies to every C-state in the `IntrOff` metric. See
[Interrupt Order Detection](#interrupt-order-detection).

The pictures below show where the measurements are in time. Time flows from left to right.

```text
TAI, then TIntr:

    LTime
    |    C-state exit    | after-idle code       | interrupt handler         |
    +--------------------+-----------------------+---------------------------+
                           ^                       ^
                           TAI                     TIntr

TIntr, then TAI:

    LTime
    |    C-state exit    | interrupt handler         | after-idle code       |
    +--------------------+---------------------------+-----------------------+
                           ^                           ^
                           TIntr                       TAI
```

Within the `wult` driver, each path does more than read its time-stamp. For example, both paths also
do the following:

- Read the `APERF` and `MPERF` counters, which are used for calculating the CPU frequency. See
  [CPU Frequency](#cpu-frequency).
- Check if the event has already happened. If it has, take the TSC and `MPERF` snapshots, which are
  used for the C-state residency metrics.

In the `i210` method, reading the time-stamp is relatively slow because it requires several PCI
register reads.

Linux also does work outside the `wult` driver that contributes to the latencies. For example:

- After-idle path: Before the after-idle code of the driver reads `TAI`, Linux may update a few
  per-CPU timing variables. This is lightweight software bookkeeping, not timer programming.
- Interrupt path: Every interrupt goes through Linux interrupt entry and dispatch before reaching
  Wult. For `i210`, measurements start in the NIC IRQ handler. The `hrt` method invokes the Wult
  hook at hrtimer expiry. The `tdt` method captures `TIntr` at local timer entry, then runs the rest
  of the measurement from the hrtimer callback.

This Linux work contributes to the latency observed on the system, so it is part of the actual
latency, not measurement overhead. Here, overhead means only the extra delay caused by the Wult
measurement code.

### The Problem

Wult-specific overhead occurs when one measurement block delays the other. This affects all methods.

- `TAI` first - The interrupt handler starts after the after-idle code ends, so `IntrLatency` is
  greater than `WakeLatency`. The measured `IntrLatency` includes the duration of the after-idle
  code, but that duration is not part of the actual interrupt latency.
- `TIntr` first - The after-idle code starts after the interrupt handler ends, so `WakeLatency` is
  greater than `IntrLatency`. The measured `WakeLatency` includes the duration of the interrupt
  handler, but that duration is not part of the actual wake latency.

The picture below shows the first, most common case in more detail.

```text
      LTime        CPU resumes
        |  C-state exit | after-idle code       | interrupt handler |
        +---------------+-----------------------+-------------------+
        |<-- actual intr. latency -->|<-- overhead -->|
        |<------ measured interrupt latency --------->|
```

### The Mitigation

The driver records these `CLOCK_MONOTONIC` time-stamps:

- `AITS1` and `AITS2`: Mark the start and end of the after-idle code. Their difference measures time
  spent in that code, including the `TAI` read.
- `IntrTS1` and `IntrTS2`: Mark the start and end of the Wult interrupt measurement. Their
  difference measures time spent in that code.

User-space uses `IntrOff` to determine which block ran first, then subtracts its measured duration
from the latency it delayed:

- `IntrOff` is true: The after-idle code runs first with interrupts disabled and delays the
  interrupt handler. Subtract `AITS2` - `AITS1` from `IntrLatency`.
- `IntrOff` is false: The interrupt handler runs first and delays the after-idle code. Subtract
  `IntrTS2` - `IntrTS1` from `WakeLatency`.

This removes the extra time spent in the first-running Wult code block from the affected latency.

**Note**: Before applying the correction, user-space converts `tdt` latency values from TSC cycles
to nanoseconds. `hrt` and `i210` latency values are already in nanoseconds. The overhead durations
are measured in nanoseconds with `CLOCK_MONOTONIC`. For `i210`, the NIC clock rate may differ
slightly from `CLOCK_MONOTONIC`, so the subtraction is approximate. User-space drops datapoints if
the estimated overhead is greater than the affected latency or if the correction produces an
inconsistent latency ordering.

## C-State Residency

For every datapoint, the driver takes snapshots of the TSC, `MPERF` and C-state residency counters
before idle, and again after the CPU wakes up.

There are 2 variants: the after-idle code runs first and the interrupt handler runs after it, or the
other way around. See
[After-Idle Code and Interrupt Handler](#after-idle-code-and-interrupt-handler).

The pictures below show where the snapshots are taken in both variants.

```text
After-idle code first:

    | idle | after-idle code | interrupt handler | send data |
    +------+-----------------+-------------------+-----------+
    ^        ^                                     ^
    1        2                                     3
    |<------>| measurement interval

Interrupt handler first:

    | idle | interrupt handler | after-idle code | send data |
    +------+-------------------+-----------------+-----------+
    ^        ^                                     ^
    1        2                                     3
    |<------>| measurement interval
```

The numbers mark the following snapshots:

1. TSC, `MPERF` and the C-state residency counters, taken before idle.
2. TSC and `MPERF`, taken in the code that runs first after the wake-up.
3. The C-state residency counters, taken later, after both the after-idle code and the interrupt
   handler have finished.

Wult uses the term **measurement interval** for the period of time between snapshots 1 and 2.

Here are the metrics that the `wult` driver sends to user-space.

- `TotCyc`: The length of the measurement interval in TSC cycles. It is the TSC value at snapshot 2
  minus the TSC value at snapshot 1.
- `CC0Cyc`: The number of cycles the CPU spent in C0. It is the `MPERF` value at snapshot 2 minus
  the `MPERF` value at snapshot 1. The `MPERF` counter ticks at a rate close to the TSC rate while
  the CPU is in C0, and does not tick while the CPU is in a C-state.
- `<name>Cyc`: The cycles the CPU spent in a C-state, for example `CC6Cyc` and `PC6Cyc`. It is the
  value of a C-state residency counter at snapshot 3 minus its value at snapshot 1. The values are
  in cycles at a rate close to the TSC rate. Each counter ticks only in the corresponding C-state,
  and does not tick in C0. See [C-State Residency Metrics](#c-state-residency-metrics).

**Note**: Since the C-state residency counters do not tick in C0, snapshot 3 can be taken later than
snapshot 2. The driver takes it when all the other measurements are done and it prepares the
datapoint for sending to user-space. This happens in the context of a separate kernel thread, the
armer thread, so it does not affect the measurements.

**Note**: The `MPERF` rate is close to the TSC rate, but not identical. `MPERF` is based on the bus
clock, while the TSC is based on the crystal clock. The difference is small (less than 1% on the
platforms measured), and `wult` ignores it. See
[TSC, APERF, and MPERF Counters](https://github.com/dedekind/dedekind-share/blob/master/2025/tsc-amperf.md)
for more details.

User-space calculates the C-state residency percentages by dividing the cycles by `TotCyc`. For
example, `CC6%` is `CC6Cyc` / `TotCyc` * 100. The results are in the `CC0%`, `CC1%`, `PC6%` and
similar metrics.

There are a few special cases:

- POLL - Only `CC0%` is calculated. The other percentages are set to zero.
- `CC1Derived%`: Not every Intel platform has a hardware CC1 counter, so user-space also derives the
  CC1 residency. It is `TotCyc` minus the cycles of all the other C-states, including C0, divided by
  `TotCyc`, in percent. Negative results are set to zero, and the value is zero for POLL.

The C-state residency counters are not always precise, especially for short sleeps. Because of that,
a calculated C-state residency percentage may be greater than 100%:

- If it is smaller than 300%, it is set to 100%.
- If it is 300% or greater, the datapoint is dropped.

## Interrupt Order Detection

There are 2 cases: the after-idle code runs before the interrupt handler, or the other way around.
User-space needs to distinguish them to do the [overhead](#overhead) math correctly.

User-space finds out the order from the incoming datapoints, separately for each C-state:

- It compares `TAI` and `TIntr` of each incoming datapoint, counts the datapoints for each order,
  and holds the datapoints back without processing them.
- There is no fixed window. It accumulates the statistics until one order outnumbers the other by a
  factor of 100. For example, 100 datapoints with one order and none with the other, or 200 and 1.
  Then it fixes the case for that C-state, processes the held datapoints that agree with the order,
  and drops the others.
- After the order is fixed, new datapoints of the C-state are no longer held back. They are
  processed as they come, and those that disagree with the order are dropped.
- The exception is POLL, which is always treated as interrupts enabled.

One datapoint is not enough. The driver tries to filter out the datapoints where the CPU was woken
up by something other than the event, but this is best effort. For example, the scheduler may write
to the memory address monitored by the `MWAIT` instruction just before the event fires. In this case
the after-idle code runs first even if interrupts were enabled.

User-space saves the result in the `IntrOff` metric of every datapoint. It is true when interrupts
were disabled (`TAI`, then `TIntr`), and false when they were enabled (`TIntr`, then `TAI`).

## TSC Rate

User-space needs the TSC rate to convert TSC cycles to nanoseconds. It measures the rate as follows:

- The driver reads the TSC and `CLOCK_MONOTONIC` one after the other with interrupts disabled before
  idle, and sends the values as `BICyc` and `BIMonotonic` with every datapoint.
- User-space takes these values from the first datapoint, and from the first datapoint that is at
  least the calibration time later. The default calibration time is 10 seconds, and the
  `--tsc-cal-time` option can be used to change it. A longer time makes the rate more accurate.
- The TSC rate in MHz is Δ`BICyc` * 1000 / Δ`BIMonotonic`, where Δ is the difference between the two
  datapoints, and `BIMonotonic` is in nanoseconds.
- User-space skips datapoints with SMIs or NMIs when it looks for the two datapoints. An SMI or NMI
  may happen between the `BICyc` and `BIMonotonic` reads and skew the rate.
- User-space holds the datapoints back until it knows the TSC rate, and then processes them.

## CPU Frequency

The `CPUFreq` metric is the CPU frequency after wake-up, in MHz. It is the average frequency between
the two measurement points after the wake-up: the after-idle code and the interrupt handler.

There are 2 variants: the after-idle code runs first and the interrupt handler runs after it, or the
other way around. See
[After-Idle Code and Interrupt Handler](#after-idle-code-and-interrupt-handler).

The driver reads the `APERF` and `MPERF` counters in both places. It sends the values of the
after-idle code as `AIAperf` and `AIMperf`, and the values of the interrupt handler as `IntrAperf`
and `IntrMperf`.

User-space calculates the counter deltas between the two measurement points. Which point comes first
depends on `IntrOff`. See [Interrupt Order Detection](#interrupt-order-detection).

- `IntrOff` is true: The after-idle code runs first. Δ`APERF` is `IntrAperf` - `AIAperf`, and
  Δ`MPERF` is `IntrMperf` - `AIMperf`.
- `IntrOff` is false: The interrupt handler runs first. Δ`APERF` is `AIAperf` - `IntrAperf`, and
  Δ`MPERF` is `AIMperf` - `IntrMperf`.

`APERF` ticks at the actual core clock rate, and `MPERF` ticks at a rate close to the TSC rate. So
Δ`APERF` / Δ`MPERF` is the actual frequency relative to the TSC rate. Multiplying it by the TSC rate
in MHz gives the frequency in MHz:

`CPUFreq` = TSC rate * Δ`APERF` / Δ`MPERF`

TSC rate is measured as described in [TSC Rate](#tsc-rate).

## Adjustments (i210-only)

The adjustment metrics (`TBIAdj`, `TAIAdj` and `TIntrAdj`) are used only by the `i210` method. The
other methods always set them to zero.

### How the NIC Time Is Read

The `i210` method reads the time from the NIC clock. The NIC is behind the PCI bus, so the driver
does it with a sequence of register reads in two steps:

1. Latch - Read the `SYSTIMR` register (0xB6F8). This latches the current NIC time, which means the
   NIC takes a snapshot of its running clock and saves it in the `SYSTIML` and `SYSTIMH` registers.
   The snapshot stays unchanged while the clock keeps running. The snapshot is taken at the moment
   the `SYSTIMR` read request reaches the NIC.
2. Read - Read the latched time from the `SYSTIML` register (0xB600, nanoseconds) and the `SYSTIMH`
   register (0xB604, seconds).

### The Problem

The problem is that the NIC is behind the PCI bus. Reading NIC registers is much slower than reading
a CPU-local clock like the TSC. The NIC time obtained by the driver corresponds to a moment that is
different from the moment the driver wants to measure, and the difference is a measurement error.

`TAI` (time after idle) is the time-stamp taken right after the CPU wakes up. It is needed for
calculating the wake latency (`WakeLatency`), which is `TAI` - `LTime`. Since `LTime` is the NIC
clock time of the event, `TAI` has to be the NIC clock time too.

Here is how the problem affects `TAI`. The CPU starts waking up at `LTime`, when the event fires.
Exiting the C-state takes some time. Only then the CPU starts executing instructions, and the driver
starts reading the NIC time to get the `TAI` time-stamp of that moment.

To read the NIC time, the driver first has to latch it by reading the `SYSTIMR` register. Since the
NIC is behind the PCI bus, it takes some time for the read request to reach the NIC, so the NIC
latches `TAI` with a delay. As a result, the measured wake latency (`TAI` - `LTime`) is longer than
the actual wake latency, which ends when the CPU started executing instructions. The picture below
demonstrates this. Time flows from left to right.

```text
      LTime             CPU starts executing
        |      C-state exit       |            SYSTIMR read             | SYSTIML, SYSTIMH  |
        +-------------------------+------------------+------------------+-------------------+
        |                                            ^
        |                                            TAI = NIC time at latch
        |<- actual wake latency ->|
        |<--------- measured wake latency ---------->|
                                  |<---- error ----->|
```

`TBI` (time before idle) is the time-stamp taken right before the CPU enters a C-state. It is needed
for calculating the silent time (`SilentTime`), which is `LTime` - `TBI`, the time the CPU spent in
the C-state before the event (`LTime`).

Here is how the problem affects `TBI`. The CPU reads `SYSTIMR`, and the NIC latches the time when
the read request reaches it. After that, the CPU still has to get the response and read the latched
time from `SYSTIML` and `SYSTIMH` before it enters the C-state. As a result, `TBI` is earlier than
the actual C-state entry, and the measured silent time (`LTime` - `TBI`) is longer than the actual
silent time. The picture below demonstrates this.

```text
                                                                                  LTime
    |        SYSTIMR read         | SYSTIML, SYSTIMH  |      CPU is in C-state      |
    +--------------+--------------+-------------------+-----------------------------+
                   ^                                  ^
                   TBI = NIC time at latch            Actual C-state entry
                                                      |<--- actual silent time ---->|
                   |<-------------------- measured silent time -------------------->|
                   |<------------ error ------------->|
```

`TIntr` is the time-stamp taken at the start of the interrupt handler of the event. It is needed for
calculating the interrupt latency (`IntrLatency`), which is `TIntr` - `LTime`. It is read the same
way as `TAI`, so it has the same problem: the NIC latches the time with a delay after the interrupt
handler starts, so the measured interrupt latency (`TIntr` - `LTime`) is longer than the actual
interrupt latency.

### The Mitigation

To mitigate this, the driver estimates the error and reports it in the `*Adj` metrics. All of them
are in nanoseconds, and user-space is expected to use them to correct the time-stamps:

- `TAIAdj`: The error of `TAI`. Subtract it from `TAI`.
- `TBIAdj`: The error of `TBI`. Add it to `TBI`.
- `TIntrAdj`: The error of `TIntr`. Subtract it from `TIntr`.

The sequence of reads in [How the NIC Time Is Read](#how-the-nic-time-is-read) is simplified. The
actual sequence has an additional warm-up read before the latch.

The reason is the assumption, explained below, that the NIC latches the time in the middle of the
`SYSTIMR` read. It holds only if the PCIe link(s) between the CPU and the NIC are awake. They may be
in a low-power state (for example L1 with ASPM), and a read that finds the link asleep is delayed on
its way to the NIC, so the latch does not happen in the middle of the read. So, before latching, the
driver does a warm-up read, which takes this delay instead of the `SYSTIMR` read.

The actual sequence of reads is:

- Before idle: `STATUS` register (warm-up), `SYSTIMR`, `SYSTIML`, `SYSTIMH`.
- After idle and in the interrupt handler: `ICS` register (warm-up), `SYSTIMR`, `SYSTIML`,
  `SYSTIMH`.

**Note**: The `WarmupDelay` and `LatchDelay` metrics show whether the warm-up read was really
needed. Both are single PCI register reads, so they take about the same time if the link was awake.
If `WarmupDelay` is much greater than `LatchDelay`, the link was asleep and the warm-up read took
the wake-up delay, as intended. The metrics cover only the after-idle and interrupt handler reads,
not the `STATUS` warm-up read before idle.

`TAIAdj` is the estimated time between the moment the CPU starts executing instructions after the
wake-up and the moment the NIC latches the time for `TAI`. `TAI` is too late by this amount, so
user-space should use `TAI` - `TAIAdj` as the corrected time after idle. The picture below
demonstrates this.

```text
      LTime             CPU starts executing
        |      C-state exit       |  ICS read   |       SYSTIMR read        | SYSTIML, SYSTIMH  |
        +-------------------------+-------------+-------------+-------------+-------------------+
                                  ^                           ^
                                  TAI - TAIAdj                TAI = NIC time at latch
                                  |<-------- TAIAdj --------->|
```

After the wake-up, the driver first does the warm-up read of the `ICS` register and then reads
`SYSTIMR`. The NIC latches the time when the `SYSTIMR` read request reaches it, but the driver does
not know exactly when that happens. It measures the duration of the reads with `ktime_get_ns()` and
assumes that the request and the response took equal time, so the latch happened in the middle of
the `SYSTIMR` read. Therefore, `TAIAdj` is the duration of the `ICS` read plus half of the duration
of the `SYSTIMR` read.

`TBIAdj` is the estimated time between the moment the NIC latches the time for `TBI` and the moment
the CPU enters the C-state. `TBI` is too early by this amount, so user-space should use `TBI` +
`TBIAdj` as the corrected time before idle. The picture below demonstrates this.

```text
    |        SYSTIMR read         | SYSTIML, SYSTIMH  |      CPU is in C-state      |
    +--------------+--------------+-------------------+-----------------------------+
                   ^                                  ^
                   TBI = NIC time at latch            TBI + TBIAdj
                   |<------------ TBIAdj ------------>|
```

Before entering the C-state, the driver reads `SYSTIMR` and then `SYSTIML` and `SYSTIMH`. With the
same assumption, `TBIAdj` is half of the duration of the `SYSTIMR` read plus the duration of the
`SYSTIML` and `SYSTIMH` reads. The warm-up read happens before the latch, so it is not a part of
`TBIAdj`.

`TIntrAdj` is the same as `TAIAdj`, but for `TIntr`. `TIntr` is too late by this amount, so
user-space should use `TIntr` - `TIntrAdj` as the corrected interrupt time.