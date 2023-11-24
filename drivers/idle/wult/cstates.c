// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2021 Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#include <linux/cpu.h>
#include <linux/errno.h>
#include <asm/msr.h>
#include "compat.h"
#include "cstates.h"
#include "wult.h"

/*
 * Read C-state counters and save them in snapshot number 'snum'.
 */
void wult_cstates_snap_cst(struct wult_cstates_info *csinfo, unsigned int snum)
{
	struct cstate_info *csi;

	if (WARN_ON(snum >= MAX_CSTATE_SNAPSHOTS))
		return;

	for_each_cstate(csinfo, csi)
		csi->cyc[snum] = __rdmsr(csi->msr);
}

/*
 * Calculate the delta between snapshots number 'snum1' and 'snum2'.
 */
void wult_cstates_calc(struct wult_cstates_info *csinfo,
		       unsigned int snum1, unsigned int snum2)
{
	struct cstate_info *csi;

	if (WARN_ON(snum1 >= MAX_CSTATE_SNAPSHOTS) ||
	    WARN_ON(snum2 >= MAX_CSTATE_SNAPSHOTS))
		return;

	csinfo->dtsc = csinfo->tsc[snum2] - csinfo->tsc[snum1];
	csinfo->dmperf = csinfo->mperf[snum2] - csinfo->mperf[snum1];
	for_each_cstate(csinfo, csi)
		csi->dcyc = csi->cyc[snum2] - csi->cyc[snum1];
}

static struct cstate_info intel_cstates[] = {
	{.name = "CC1", MSR_CORE_C1_RES},
	{.name = "CC3", MSR_CORE_C3_RESIDENCY},
	{.name = "CC6", MSR_CORE_C6_RESIDENCY},
	{.name = "CC7", MSR_CORE_C7_RESIDENCY},
	{.name = "MC6", MSR_MODULE_C6_RES_MS},
	{.name = "PC2", MSR_PKG_C2_RESIDENCY},
	{.name = "PC3", MSR_PKG_C3_RESIDENCY},
	{.name = "PC6", MSR_PKG_C6_RESIDENCY},
	{.name = "PC7", MSR_PKG_C7_RESIDENCY},
	{.name = "PC8", MSR_PKG_C8_RESIDENCY},
	{.name = "PC9", MSR_PKG_C9_RESIDENCY},
	{.name = "PC10", MSR_PKG_C10_RESIDENCY},
	{}
};

/*
 * Intel CPU-specific C-state initialization function.
 */
static int intel_cstate_init(struct wult_cstates_info *csinfo)
{
	struct cstate_info *csi;
	u64 reg;

	csinfo->cstates = intel_cstates;
	for_each_cstate(csinfo, csi) {
		if (rdmsrl_safe(csi->msr, &reg))
			/* We got an exception while reading the MSR. */
			csi->absent = true;
		else if (!reg) {
			/*
			 * The MSR contains zero, which means that either it is
			 * not supported, or the C-state has never been reached
			 * yet. Let's assume it is not reachable and exclude
			 * it.
			 */
			csi->absent = true;
		}
	}

	return 0;
}

static struct cstate_info no_cstates[] = {
	{}
};

/*
 * Find out which C-states the platform supports and how to get information
 * about them.
 */
int wult_cstates_init(struct wult_cstates_info *csinfo)
{
	int err = 0;

	if (boot_cpu_data.x86_vendor == X86_VENDOR_INTEL)
		err = intel_cstate_init(csinfo);
	else
		csinfo->cstates = no_cstates;

	return err;
}
