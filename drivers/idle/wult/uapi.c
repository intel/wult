// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2021 Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#include <linux/debugfs.h>
#include <linux/err.h>
#include <linux/errno.h>
#include <linux/fs.h>
#include <linux/vmalloc.h>
#include "tracer.h"
#include "uapi.h"
#include "wult.h"

/*
 * Names of debugfs files exposing the allowed launch distance range.
 */
#define LDIST_MIN_FNAME "ldist_min_nsec"
#define LDIST_MAX_FNAME "ldist_max_nsec"

/*
 * Names of debugfs files exposing the currently configured launch distance
 * range.
 */
#define LDIST_FROM_FNAME "ldist_from_nsec"
#define LDIST_TO_FNAME   "ldist_to_nsec"

/* Name of debugfs file for starting and stopping the measurements. */
#define ENABLED_FNAME "enabled"

/* Name of debugfs file for enabling early interrupts. */
#define EARLY_INTR_FNAME "early_intr"

static ssize_t enabled_write(struct file *file, const char __user *user_buf,
			     size_t count, loff_t *ppos)
{
	bool *enabled = file->private_data;
	struct wult_info *wi = container_of(enabled, struct wult_info, enabled);
	ssize_t err;

	err = debugfs_write_file_bool(file, user_buf, count, ppos);
	if (err < 0)
		return err;

	if (*enabled)
		return wult_enable();

	wult_disable();
	return err;
}

static const struct file_operations enabled_ops = {
	.read = debugfs_read_file_bool,
	.write = enabled_write,
	.open = simple_open,
	.llseek = default_llseek,
};

static ssize_t ei_write(struct file *file, const char __user *user_buf,
			size_t count, loff_t *ppos)
{
	bool *ei = file->private_data;
	struct wult_info *wi = container_of(ei, struct wult_info, ei);
	ssize_t err;

	err = debugfs_write_file_bool(file, user_buf, count, ppos);
	if (err < 0)
		return err;

	mutex_lock(&wi->enable_mutex);
	if (wi->early_intr != *ei && wi->enabled) {
		/* Forbid changes if measurements are enabled. */
		err = -EBUSY;
	} else
		wi->early_intr = *ei;
	mutex_unlock(&wi->enable_mutex);

	return err;
}

static const struct file_operations ei_ops = {
	.read = debugfs_read_file_bool,
	.write = ei_write,
	.open = simple_open,
	.llseek = default_llseek,
};

static int ldist_from_get(void *data, u64 *val)
{
	struct wult_info *wi = data;

	mutex_lock(&wi->enable_mutex);
	*val = wi->ldist_from;
	mutex_unlock(&wi->enable_mutex);

	return 0;
}

static int ldist_from_set(void *data, u64 val)
{
	struct wult_info *wi = data;
	int err;

	mutex_lock(&wi->enable_mutex);
	if (wi->enabled) {
		/* Forbid changes if measurements are enabled. */
		err = -EBUSY;
		goto out_unlock;
	}

	err = -EINVAL;
	if (val > wi->wdi->ldist_max || val < wi->wdi->ldist_min)
		goto out_unlock;
	if (val > wi->ldist_to)
		goto out_unlock;

	err = 0;
	wi->ldist_from = val;
out_unlock:
	mutex_unlock(&wi->enable_mutex);
	return err;
}

DEFINE_DEBUGFS_ATTRIBUTE(ldist_from_ops, ldist_from_get, ldist_from_set, "%llu\n");

static int ldist_to_get(void *data, u64 *val)
{
	struct wult_info *wi = data;

	mutex_lock(&wi->enable_mutex);
	*val = wi->ldist_tom;
	mutex_unlock(&wi->enable_mutex);
	return 0;
}

static int ldist_to_set(void *data, u64 val)
{
	struct wult_info *wi = data;
	int err;

	mutex_lock(&wi->enable_mutex);
	if (wi->enabled) {
		/* Forbid changes if measurements are enabled. */
		err = -EBUSY;
		goto out_unlock;
	}

	err = -EINVAL;
	if (val > wi->wdi->ldist_max || val < wi->wdi->ldist_min)
		goto out_unlock;
	if (val < wi->ldist_from)
		goto out_unlock;

	err = 0;
	wi->ldist_from = val;
out_unlock:
	mutex_unlock(&wi->enable_mutex);
	return err;
}
DEFINE_DEBUGFS_ATTRIBUTE(ldist_to_ops, ldist_to_get, ldist_to_set, "%llu\n");

int wult_uapi_device_register(struct wult_info *wi)
{
	wi->dfsroot = debugfs_create_dir(DRIVER_NAME, NULL);
	if (IS_ERR(wi->dfsroot))
		return PTR_ERR(wi->dfsroot);

	debugfs_create_file(ENABLED_FNAME, 0644, wi->dfsroot, &wi->enabled, &enabled_ops);
	debugfs_create_file(EARLY_INTR_FNAME, 0644, wi->dfsroot, &wi->ei, &ei_ops);

	debugfs_create_u64(LDIST_MIN_FNAME, 0444, wi->dfsroot, &wi->wdi->ldist_min);
	debugfs_create_u64(LDIST_MAX_FNAME, 0444, wi->dfsroot, &wi->wdi->ldist_max);

	debugfs_create_file(LDIST_FROM_FNAME, 0644, wi->dfsroot, wi, &ldist_from_ops);
	debugfs_create_file(LDIST_TO_FNAME, 0644, wi->dfsroot, wi, &ldist_to_ops);

	return 0;
}

void wult_uapi_device_unregister(struct wult_info *wi)
{
	debugfs_remove_recursive(wi->dfsroot);
}
