// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2021 Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#ifndef _WULT_CSTATE_H_
#define _WULT_CSTATE_H_

/* Maximum C-state cycles snapsots count. */
#define MAX_CSTATE_SNAPSHOTS 2

/* Iterate over every valid C-state. */
#define for_each_cstate(csinfo, csi)             \
        for (csi = (csinfo)->cstates; csi->name; csi++) \
		if (csi->absent || !csi->msr) {} else

/*
 * Information about a single C-state.
 */
struct cstate_info {
	const char *name;
	const unsigned int msr;
	/* True for core C-states, false for package C-states. */
	bool core;
	/* True if this C-state does not exist on this CPU. */
	bool absent;
	/* C-state counter snapshots.  */
	u64 cyc[MAX_CSTATE_SNAPSHOTS];
	/* Delta between between any two C-state counter snapshots. */
	u64 dcyc;
};

/*
 * Infromation about C-states.
 */
struct wult_cstates_info {
	/* Information about every C-state on this platform. */
	struct cstate_info *cstates;
	/* TSC snapshots. */
	u64 tsc[MAX_CSTATE_SNAPSHOTS];
	/* Delta between any two TSC snapshots. */
	u64 dtsc;
	/* MPERF snapshots. */
	u64 mperf[MAX_CSTATE_SNAPSHOTS];
	/* Delta between any two MPERF snapshots. */
	u64 dmperf;
};

/*
 * Read TSC and save it in snapshot number 'snum'.
 */
static inline void wult_cstates_snap_tsc(struct wult_cstates_info *csinfo,
		                         unsigned int snum)
{
	csinfo->tsc[snum] = rdtsc_ordered();
}

/*
 * Read MPERF and save it in snapshot number 'snum'.
 */
static inline void wult_cstates_snap_mperf(struct wult_cstates_info *csinfo,
		                           unsigned int snum)
{
	csinfo->mperf[snum] = __rdmsr(MSR_IA32_MPERF);
}


void wult_cstates_snap_cst(struct wult_cstates_info *csinfo, unsigned int snum);
void wult_cstates_calc(struct wult_cstates_info *csinfo,
		       unsigned int snum1, unsigned int snum2);
int wult_cstates_init(struct wult_cstates_info *csinfo);
#endif
