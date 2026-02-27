// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2024-2026 Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#ifndef _PBE_COMPAT_H_
#define _PBE_COMPAT_H_

#include <linux/version.h>

#if LINUX_VERSION_CODE < KERNEL_VERSION(6, 6, 0)
#define __apic_send_IPI_mask(mask, vector) apic->send_IPI_mask(mask, vector)
#endif

#endif /* _PBE_COMPAT_H_ */

