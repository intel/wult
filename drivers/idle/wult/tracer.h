// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2020, Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#ifndef _WULT_TRACER_H_
#define _WULT_TRACER_H_

#include <linux/tracepoint.h>
#include "compat.h"
#include "cstates.h"

/* Format string for the common part of trace output. */
#define COMMON_TRACE_FMT DRIVER_NAME ": SilentTime=%llu WakeLatency=%llu " \
	                 "LDist=%llu ReqCState=%u TotCyc=%llu CC0Cyc=%llu"

/* Size of the measurement data output buffer */
#define OUTBUF_SIZE 4096

/* Name of the tracepoint we hook to. */
#define TRACEPOINT_NAME "cpu_idle"

struct wult_info;

/*
 * Wult tracer information.
 */
struct wult_tracer_info {
	/* C-state information. */
	struct wult_cstates_info csinfo;
	/* Time before idle and after idle in cycles or nanoseconds. */
	u64 ts1, ts2;
	/* Launch time. */
	u64 ltime;
	/* Launch distance. */
	u64 ldist;
	/* The requested C-state index. */
	int req_cstate;
	/* The tracepoint we hook to. */
	struct tracepoint *tp;
	/* NMI and SMI interrupt counters. */
	u32 nmi, smi;
	/* Whether the last measurement data is valid. */
	bool data_valid;
	/* The measurement data output buffer. */
	char *outbuf;
};

int wult_tracer_init(struct wult_info *wi);
void wult_tracer_exit(struct wult_info *wi);

int wult_tracer_enable(struct wult_info *wi);
void wult_tracer_disable(struct wult_info *wi);

int wult_tracer_arm_event(struct wult_info *wi, u64 *ldist);
int wult_tracer_send_data(struct wult_info *wi);

#endif
