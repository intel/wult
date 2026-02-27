// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2026 Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#ifndef _WULT_UAPI_H_
#define _WULT_UAPI_H_

struct wult_info;

int wult_uapi_device_register(struct wult_info *wi);
void wult_uapi_device_unregister(struct wult_info *wi);

#endif /* _WULT_UAPI_H_ */
