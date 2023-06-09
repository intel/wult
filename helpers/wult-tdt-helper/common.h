/* SPDX-License-Identifier: GPL-2.0 */
/*
 * Copyright(c) 2022 Intel Corporation.
 * Author: Tero Kristo <tero.kristo@linux.intel.com>
 */

/*
 * This file includes the bits shared between userspace and eBPF parts of
 * 'wult-tdt-helper'.
 */

#ifndef __WULT_TDT_HELPER_COMMON_H__
#define __WULT_TDT_HELPER_COMMON_H__

#define WULT_TDT_HELPER_NUM_PERF_COUNTERS 16

/**
 * tdt_bpf_event - info about bpf events
 * @type: type of event
 * @ldist: launch distance (in ns)
 * @ltimec: launch time (TSC counter)
 * @tbi: time before idle(ns)
 * @tbi2: time before idle (ns) #2
 * @bic: cycles before idle
 * @bic2: cycles before idle #2
 * @aic: cycles after idle
 * @aic2: cycles after idle #2
 * @intrc: cycles at interrupt handler
 * @intrc2: cycles at interrupt handler #2
 * @aiaperf: APERF count after idle
 * @intraperf: APERF count at interrupt handler
 * @aimperf: MPERF count after idle
 * @intrmperf: MPERF count at interrupt handler
 * @swirqc: swirq count
 * @nmic: NMI count
 * @req_cstate: requested cstate
 * @perf_counters: contents of requested perf counters
 */
struct tdt_bpf_event {
	u8 type;
	u32 ldist;
	u64 ltimec;
	u64 tbi;
	u64 tbi2;
	u64 bic;
	u64 bic2;
	u64 aic;
	u64 aic2;
	u64 intrc;
	u64 intrc2;
	u64 aiaperf;
	u64 intraperf;
	u64 aimperf;
	u64 intrmperf;
	u32 swirqc;
	u32 nmic;
	int req_cstate;
	u64 perf_counters[WULT_TDT_HELPER_NUM_PERF_COUNTERS];
};

struct tdt_bpf_args {
	int debug;
	u32 min_ldist;
	u32 max_ldist;
	u32 tsc_khz;
	int perf_ev_amt;
};

enum {
	TDT_EVENT_DATA,
	TDT_EVENT_PING,
};

enum {
	MSR_TSC,
	MSR_MPERF,
	MSR_APERF,
	MSR_SMI,
	MSR_EVENT_COUNT
};

#endif /* __WULT_TDT_HELPER_COMMON_H__ */
