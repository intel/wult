// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2020, Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#ifndef _WULT_TRACER_H_
#define _WULT_TRACER_H_

#include <linux/tracepoint.h>
#include <linux/trace_events.h>
#include "compat.h"
#include "cstates.h"

/* Name of the tracepoint we hook to. */
#define TRACEPOINT_NAME "cpu_idle"

#ifdef COMPAT_USE_TRACE_PRINTK
/* Format string for the common part of trace output. */
#define COMMON_TRACE_FMT "SilentTime=%llu WakeLatency=%llu IntrLatency=%llu " \
			 "LDist=%llu ReqCState=%u TotCyc=%llu CC0Cyc=%llu " \
			 "SMIWake=%llu NMIWake=%llu SMIIntr=%llu NMIIntr=%llu"

/* Size of the measurement data output buffer. */
#define OUTBUF_SIZE 4096
#else
/*
 * Name of the wult synthetic event which is used for sending measurement data
 * to user-space.
 */
#define WULT_TRACE_EVENT_NAME "wult_cpu_idle"
#endif

struct wult_info;

/*
 * Wult tracer information.
 */
struct wult_tracer_info {
	/* C-state information. */
	struct wult_cstates_info csinfo;
	/* Time before idle and after idle in cycles or nanoseconds. */
	u64 tbi, tai;
	/* Interrupt time. */
	u64 tintr;
	/* Launch time. */
	u64 ltime;
	/* Launch distance. */
	u64 ldist;
	/* The requested C-state index. */
	int req_cstate;
	/* The tracepoint we hook to. */
	struct tracepoint *tp;
	/* SMI and NMI counters before idle. */
	u32 smi_bi, nmi_bi;
	/* SMI and NMI counters after idle. */
	u32 smi_ai, nmi_ai;
	/* SMI and NMI counters in the interrupt handler. */
	u32 smi_intr, nmi_intr;
	/* The overhead of taking measurements after we woke up. */
	u64 ai_overhead;
	/* Whether the tracer have new any measurement data. */
	bool got_measurements;
#ifdef COMPAT_USE_TRACE_PRINTK
	/* The measurement data output buffer. */
	char *outbuf;
#else
	/* The wult trace event file. */
	struct trace_event_file *event_file;
#endif
};

int wult_tracer_init(struct wult_info *wi);
void wult_tracer_exit(struct wult_info *wi);

int wult_tracer_enable(struct wult_info *wi);
void wult_tracer_disable(struct wult_info *wi);

int wult_tracer_arm_event(struct wult_info *wi, u64 *ldist);
int wult_tracer_send_data(struct wult_info *wi);

void wult_tracer_interrupt(struct wult_info *wi, u64 tintr);
#endif
