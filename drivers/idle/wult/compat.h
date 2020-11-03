// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2020, Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#ifndef _WULT_COMPAT_H_
#define _WULT_COMPAT_H_

#include <linux/version.h>
#include <asm/intel-family.h>

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

#endif /* _WULT_COMPAT_H_ */
