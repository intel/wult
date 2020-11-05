// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2020, Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#include <linux/cpu.h>
#include <linux/errno.h>
#include <asm/intel-family.h>
#include <asm/msr.h>
#include "compat.h"
#include "cstates.h"
#include "wult.h"

/*
 * Read the C-state information before idle.
 */
void wult_cstates_read_before(struct wult_cstates_info *csinfo)
{
	struct cstate_info *csi;

	csinfo->tsc1 = rdtsc_ordered();
	csinfo->mperf1 = __rdmsr(MSR_IA32_MPERF);
	for_each_cstate_msr(csinfo, csi)
		csi->cyc1 = __rdmsr(csi->msr);
}

/*
 * Read the C-state information after idle.
 */
void wult_cstates_read_after(struct wult_cstates_info *csinfo)
{
	struct cstate_info *csi;

	csinfo->mperf2 = __rdmsr(MSR_IA32_MPERF);
	csinfo->tsc2 = rdtsc_ordered();
	for_each_cstate_msr(csinfo, csi)
		csi->cyc2 = __rdmsr(csi->msr);
}

static inline struct cstate_info *find_cc1_info(struct wult_cstates_info *csinfo)
{
	return &csinfo->cstates[0];
}

/* Calculates the delta between 2 C-state statistics snapshots. */
void wult_cstates_calc(struct wult_cstates_info *csinfo)
{
	struct cstate_info *csi, *cc1_csi;
	u64 cyc;

	csinfo->tsc = csinfo->tsc2 - csinfo->tsc1;
	csinfo->mperf = csinfo->mperf2 - csinfo->mperf1;

	/* Read the C-state counters and calculate the delta. */
	for_each_cstate_msr(csinfo, csi)
		csi->cyc = csi->cyc2 - csi->cyc1;

	cc1_csi = find_cc1_info(csinfo);
	if (!cc1_csi->msr) {
		/* Calculate CC1 residency since there is no MSR for it. */
		cyc = 0;
		for_each_cstate_msr(csinfo, csi)
			if (csi->core)
				cyc += csi->cyc;
		cyc += csinfo->mperf;
		cc1_csi->cyc = csinfo->tsc - cyc;
	}
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
	for_each_cstate_msr(csinfo, csi)
		/*
		 * Assume the C-state is present if we do not get an exception
		 * when reading the MSR. If the C-state is not actually
		 * supported by this platform, the MSR will always be 0, which
		 * is OK.
		 */
		if (rdmsrl_safe(csi->msr, &reg)) {
			csi->msr = 0;
			csi->absent = true;
		}

	/*
	 * CC1 is treated differently, because we can derive it. Figure out if
	 * the C1 residency MSR is provided by the platform.
	 */
	csi = find_cc1_info(csinfo);
	if (csi->absent) {
		/*
		 * Reading the MSR caused an exception, clearly it is not
		 * supported, so we'll need to derive it.
		 */
		csi->absent = false;
		return 0;
	}

	/*
	 * The CC1 residency MSR exists in Atoms starting from Silvermont, and
	 * on big core platforms starting from IceLake.
	 */
	switch (boot_cpu_data.x86_model) {
	case INTEL_FAM6_ATOM_SILVERMONT:
	case INTEL_FAM6_ATOM_SILVERMONT_D:
	case INTEL_FAM6_ATOM_AIRMONT:
	case INTEL_FAM6_ATOM_AIRMONT_NP:
	case INTEL_FAM6_ATOM_GOLDMONT:
	case INTEL_FAM6_ATOM_GOLDMONT_D:
	case INTEL_FAM6_ATOM_GOLDMONT_PLUS:
	case INTEL_FAM6_ATOM_TREMONT:
	case INTEL_FAM6_ATOM_TREMONT_D:
	case INTEL_FAM6_XEON_PHI_KNL:
	case INTEL_FAM6_XEON_PHI_KNM:
	case INTEL_FAM6_ICELAKE_X:
	case INTEL_FAM6_ICELAKE_D:
	case INTEL_FAM6_ICELAKE:
	case INTEL_FAM6_ICELAKE_L:
	case INTEL_FAM6_TIGERLAKE:
	case INTEL_FAM6_TIGERLAKE_L:
	case INTEL_FAM6_SAPPHIRERAPIDS_X:
	case INTEL_FAM6_COMETLAKE:
	case INTEL_FAM6_COMETLAKE_L:
		break;
	default:
		csi->msr = 0;
	}

	wult_msg("CC1 residency MSR status: %ssupported", csi->msr ? "" : "not ");

	return 0;
}

static struct cstate_info default_cstates[] = {
	{.name = "CC1", .core = true},
	{NULL}
};

/*
 * C-state initialization function for unsupported x86 CPUs. Assumes there is
 * only one C-state - CC1.
 */
static int default_cstate_init(struct wult_cstates_info *csinfo)
{
	csinfo->cstates = default_cstates;
	return 0;
}

/*
 * Find out which C-states the platform supports and how to get information
 * about them.
 */
int wult_cstates_init(struct wult_cstates_info *csinfo)
{
	int err = -EINVAL;

	if (boot_cpu_data.x86_vendor == X86_VENDOR_INTEL)
		err = intel_cstate_init(csinfo);
	else
		err = default_cstate_init(csinfo);

	return err;
}

void wult_cstates_exit(struct wult_cstates_info *csinfo)
{
	return;
}
