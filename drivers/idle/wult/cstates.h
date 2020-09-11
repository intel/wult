// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2020, Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#ifndef _WULT_CSTATE_H_
#define _WULT_CSTATE_H_

/* Iterate over every valid C-state. */
#define for_each_cstate(csinfo, csi)                \
        for (csi = (csinfo)->cstates; csi->name; csi++) \
		if (csi->absent) {} else

/* Iterate over every valid C-state which has an MSR register. */
#define for_each_cstate_msr(csinfo, csi)             \
        for (csi = (csinfo)->cstates; csi->name; csi++) \
		if (csi->absent || !csi->msr) {} else

/*
 * Information about a single C-state.
 */
struct cstate_info {
	const char *name;
	unsigned int msr;
	/* True for core C-states, false for package C-states. */
	bool core;
	/* True if this C-state does not exist on this CPU. */
	bool absent;
	/* Cycles count before, after idle, and the delta. */
	u64 cyc1, cyc2, cyc;
};

/*
 * Infromation about C-states.
 */
struct wult_cstates_info {
	/* Information about every C-state on this platform. */
	struct cstate_info *cstates;
	/* TSC value before idle, after idle, and the delta. */
	u64 tsc1, tsc2, tsc;
	/* MPERF value before idle, after idle, and the delta. */
	u64 mperf1, mperf2, mperf;
};

void wult_cstates_read_before(struct wult_cstates_info *csinfo);
void wult_cstates_read_after(struct wult_cstates_info *csinfo);
void wult_cstates_calc(struct wult_cstates_info *csinfo);
int wult_cstates_init(struct wult_cstates_info *csinfo);
void wult_cstates_exit(struct wult_cstates_info *csinfo);
#endif
