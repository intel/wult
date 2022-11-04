/* SPDX-License-Identifier: GPL-2.0 */
/*
 * Copyright(c) 2022 Intel Corporation.
 * Author: Tero Kristo <tero.kristo@linux.intel.com>
 */

/*
 * This file includes the bits shared between userspace and eBPF parts of
 * 'wult-hrt-helper'.
 */

#ifndef __WULTRUNNER_COMMON_H__
#define __WULTRUNNER_COMMON_H__

#define WULTRUNNER_NUM_PERF_COUNTERS 16

/**
 * hrt_bpf_event - info about bpf events
 * @type: type of event
 * @ldist: launch distance (in ns)
 * @ltime: launch time (ktime_ns time)
 * @tbi: time before idle (ns)
 * @tai: time after idle (ns)
 * @tintr: time for interrupt execution start
 * @bic: cycles before idle
 * @aic: cycles after idle
 * @intrc: cycles at interrupt handler
 * @aits1: time after idle #1
 * @aits2: time after idle #2
 * @intrts1: time at hrtimer interrupt #1
 * @intrts2: time at hrtimer interrupt #2
 * @swirqc: swirq count
 * @nmic: NMI count
 * @req_cstate: requested cstate
 * @perf_counters: contents of requested perf counters
 */
struct hrt_bpf_event {
	u8 type;
	u32 ldist;
	u64 ltime;
	u64 tbi;
	u64 tai;
	u64 tintr;
	u64 bic;
	u64 aic;
	u64 intrc;
	u64 aits1;
	u64 aits2;
	u64 intrts1;
	u64 intrts2;
	u32 swirqc;
	u32 nmic;
	int req_cstate;
	u64 perf_counters[WULTRUNNER_NUM_PERF_COUNTERS];
};

struct hrt_bpf_args {
	int debug;
	u32 min_t;
	u32 max_t;
};

enum {
	HRT_EVENT_DATA,
	HRT_EVENT_PING,
};

enum {
	MSR_TSC,
	MSR_MPERF,
	MSR_SMI,
	MSR_EVENT_COUNT
};

#endif /* __WULTRUNNER_COMMON_H__ */
