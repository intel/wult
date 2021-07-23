// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2020, Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#ifndef _WULT_COMPAT_H_
#define _WULT_COMPAT_H_

#include <linux/version.h>

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
 * 'WARN_ON()' in 'tracer.c'. There are no warning starting from kernel version
 * 5.3.
 *
 * This macro makes that warning be conditional on the kernel version. This is
 * ugly, but temporary. We'll drop old kernels support at some point.
 */
#if LINUX_VERSION_CODE < KERNEL_VERSION(5, 3, 0)
#define COMPAT_PECULIAR_TRACE_PROBE
#endif

#endif /* _WULT_COMPAT_H_ */
