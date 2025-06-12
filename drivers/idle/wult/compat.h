// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2021 Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#ifndef _WULT_COMPAT_H_
#define _WULT_COMPAT_H_

#include <linux/version.h>

#if LINUX_VERSION_CODE >= KERNEL_VERSION(5, 14, 0)
#define COMPAT_HAVE_SET_AFFINITY
#endif

#if LINUX_VERSION_CODE < KERNEL_VERSION(6, 15, 0)
#define hrtimer_setup(_timer, _func, _clock_id, _mode) \
        do { \
                hrtimer_init((_timer), (_clock_id), (_mode)); \
                (_timer)->function = (_func); \
        } while(0)
#endif

#if LINUX_VERSION_CODE > KERNEL_VERSION(6, 15, 0)
#define rdmsrl_safe(_reg, _val) rdmsrq_safe((_reg), (_val))
#endif

#endif /* _WULT_COMPAT_H_ */
