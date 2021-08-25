// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2020, Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#include <linux/cpu.h>
#include <linux/errno.h>
#include <asm/msr.h>
#include "compat.h"
#include "cstates.h"
#include "wult.h"

/*
 * Read and save the C-state residency counters before idle.
 */
void wult_cstates_read_before(struct wult_cstates_info *csinfo)
{
	struct cstate_info *csi;

	csinfo->tsc1 = rdtsc_ordered();
	csinfo->mperf1 = __rdmsr(MSR_IA32_MPERF);
	for_each_cstate(csinfo, csi)
		csi->cyc1 = __rdmsr(csi->msr);
}

/*
 * Read TSC and 'mperf' after idle.
 */
void wult_cstates_read_after(struct wult_cstates_info *csinfo)
{
	csinfo->mperf2 = __rdmsr(MSR_IA32_MPERF);
	csinfo->tsc2 = rdtsc_ordered();
}

/*
 * Read C-state residency counters after idle. Calculate the delta between the
 * newly read values and the values read before idle.
 *
 * Unlike 'wult_cstates_read_after()' this function does not have to be called
 * as soon as possible after idle, because as long as the CPU is in C0, the
 * C-state residency counters do not change and can be read at a later
 * convenient time.
 */
void wult_cstates_calc(struct wult_cstates_info *csinfo)
{
	struct cstate_info *csi;

	/* Read C-state residency counters after idle */
	for_each_cstate(csinfo, csi)
		csi->cyc2 = __rdmsr(csi->msr);

	csinfo->dtsc = csinfo->tsc2 - csinfo->tsc1;
	csinfo->dmperf = csinfo->mperf2 - csinfo->mperf1;

	/*
	 * Calculate the delta between the C-state residency counters before
	 * and after idle.
	 */
	for_each_cstate(csinfo, csi)
		csi->dcyc = csi->cyc2 - csi->cyc1;
}

static struct cstate_info intel_cstates[] = {
	{.name = "CC1", MSR_CORE_C1_RES, .core = true},
	{.name = "CC3", MSR_CORE_C3_RESIDENCY, .core = true},
	{.name = "CC6", MSR_CORE_C6_RESIDENCY, .core = true},
	{.name = "CC7", MSR_CORE_C7_RESIDENCY, .core = true},
	{.name = "PC2", MSR_PKG_C2_RESIDENCY},
	{.name = "PC3", MSR_PKG_C3_RESIDENCY},
	{.name = "PC6", MSR_PKG_C6_RESIDENCY},
	{.name = "PC7", MSR_PKG_C7_RESIDENCY},
	{.name = "PC8", MSR_PKG_C8_RESIDENCY},
	{.name = "PC9", MSR_PKG_C9_RESIDENCY},
	{.name = "PC10", MSR_PKG_C10_RESIDENCY},
	{NULL}
};

/*
 * Intel CPU-specific C-state initialization function.
 */
static int intel_cstate_init(struct wult_cstates_info *csinfo)
{
	struct cstate_info *csi;
	u64 reg;

	csinfo->cstates = intel_cstates;
	for_each_cstate(csinfo, csi)
		/*
		 * Assume the C-state is present if we do not get an exception
		 * when reading the MSR. If the C-state is not actually
		 * supported by this platform, MSR read will always return 0.
		 */
		if (rdmsrl_safe(csi->msr, &reg))
			csi->absent = true;

	return 0;
}

static struct cstate_info no_cstates[] = {
	{NULL}
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
