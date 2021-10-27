// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2020, Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#ifndef _WULT_COMPAT_H_
#define _WULT_COMPAT_H_

#include <linux/version.h>

#if LINUX_VERSION_CODE >= KERNEL_VERSION(5, 14, 0)
#define COMPAT_HAVE_SET_AFFINITY
#endif

#endif /* _WULT_COMPAT_H_ */
