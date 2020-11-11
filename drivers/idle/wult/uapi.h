// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2020, Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#ifndef _WULT_UAPI_H_
#define _WULT_UAPI_H_

/*
 * Names of debugfs files exposing the allowed launch distance range.
 */
#define LDIST_MIN_DFS_NAME "ldist_min_nsec"
#define LDIST_MAX_DFS_NAME "ldist_max_nsec"

/*
 * Names of debugfs files exposing the currently configured launch distance
 * range.
 */
#define LDIST_FROM_DFS_NAME "ldist_from_nsec"
#define LDIST_TO_DFS_NAME "ldist_to_nsec"

/* Name of debugfs file for exposing the launch distance resolution. */
#define LDIST_RES_DFS_NAME "resolution_nsec"

/* Name of debugfs file for starting and stopping the measurements. */
#define ENABLED_DFS_NAME "enabled"

int wult_uapi_device_register(struct wult_info *wi);
void wult_uapi_device_unregister(struct wult_info *wi);

#endif
