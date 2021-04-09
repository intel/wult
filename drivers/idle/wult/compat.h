// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2020, Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#ifndef _WULT_COMPAT_H_
#define _WULT_COMPAT_H_

#include <linux/version.h>
#include <asm/intel-family.h>

/* This was added in v5.8 */
#ifndef INTEL_FAM6_SAPPHIRERAPIDS_X
#define INTEL_FAM6_SAPPHIRERAPIDS_X 0x8F
#endif

/*
 * Some Icelake macros were added in v5.2, but then there was a rename in v5.4
 * (INTEL_FAM6_ICELAKE_DESKTOP -> INTEL_FAM6_ICELAKE_D).
 */
#ifndef INTEL_FAM6_ICELAKE_D
#define INTEL_FAM6_ICELAKE_X 0x6A
#define INTEL_FAM6_ICELAKE_D 0x6C
#define INTEL_FAM6_ICELAKE   0x7D
#define INTEL_FAM6_ICELAKE_L 0x7E
#endif

/* Prior to v5.4 the name was 'INTEL_FAM6_ATOM_GOLDMONT_X' */
#ifndef INTEL_FAM6_ATOM_GOLDMONT_D
#define INTEL_FAM6_ATOM_GOLDMONT_D 0x5F
#endif

#ifndef INTEL_FAM6_ATOM_GOLDMONT_PLUS
#define INTEL_FAM6_ATOM_GOLDMONT_PLUS 0x7A
#endif

/* This was added in v5.4. */
#ifndef INTEL_FAM6_ATOM_TREMONT
#define INTEL_FAM6_ATOM_TREMONT 0x96
#endif

#ifndef INTEL_FAM6_ATOM_TREMONT_D
#define INTEL_FAM6_ATOM_TREMONT_D 0x86
#endif

#ifndef INTEL_FAM6_ATOM_AIRMONT_NP
#define INTEL_FAM6_ATOM_AIRMONT_NP 0x75
#endif

#ifndef INTEL_FAM6_TIGERLAKE_L
#define INTEL_FAM6_TIGERLAKE_L 0x8C
#define INTEL_FAM6_TIGERLAKE   0x8D
#endif

#ifndef INTEL_FAM6_COMETLAKE_L
#define INTEL_FAM6_COMETLAKE_L 0xA6
#define INTEL_FAM6_COMETLAKE   0xA5
#endif

/* This was added in v4.20. */
#ifndef INTEL_FAM6_ATOM_SILVERMONT
#define INTEL_FAM6_ATOM_SILVERMONT 0x37
#endif

#ifndef INTEL_FAM6_ATOM_SILVERMONT_D
#define INTEL_FAM6_ATOM_SILVERMONT_D 0x4D
#endif

/* Synthetic events support was added in v5.6 */
#if LINUX_VERSION_CODE < KERNEL_VERSION(5, 6, 0)
#define COMPAT_USE_TRACE_PRINTK
#endif

/*
 * Old kernels have peculiar trace probe behavior while it is being registered
 * and unregistered.  Namely, during registering the 'cpu_idle_hook()' hook, it
 * is called with 'PWR_EVENT_EXIT' several times in a row (like we keep exiting
 * a C-state several times without entering it). During registering, it is
 * called with a non-'PWR_EVENT_EXIT' value several times in a row, like we
 * keep entering a C-state without exiting. This is some sort of tracing
 * subsystem artifact, or bug. We do not observe it in new kernels.
 *
 * As a result, with old kenels, there are warnings coming from
 * 'WARN_ON(before_idle_called)' in 'tracer.c'. There are no warning starting
 * from kernel version 5.3.
 *
 * This macro makes that warning be conditional on the kernel version. This is
 * ugly, but temporary. We'll drop old kernels support at some point.
 */
#if LINUX_VERSION_CODE < KERNEL_VERSION(5, 3, 0)
#define COMPAT_PECULIAR_TRACE_PROBE
#endif

#endif /* _WULT_COMPAT_H_ */
