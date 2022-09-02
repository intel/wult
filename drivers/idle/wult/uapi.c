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

static int set_enabled(bool enabled)
{
	int err = 0;

	if (enabled)
		err = wult_enable();
	else
		wult_disable();

	return err;
}

/*
 * Set a boolean variable pointed to by 'boolptr' to value 'val'.
 */
static int set_bool(struct wult_info *wi, bool *boolptr, bool val)
{
	int err = 0;

	mutex_lock(&wi->enable_mutex);
	if (*boolptr == val || !wi->enabled)
		*boolptr = val;
	else
		/*
		 * The measurements must be disabled in order to toggle the
		 * interrupt focus mode.
		 */
		err = -EBUSY;
	mutex_unlock(&wi->enable_mutex);

	return err;
}

static ssize_t dfs_write_bool_file(struct file *file,
				   const char __user *user_buf,
				   size_t count, loff_t *ppos)
{
	int err;
	bool val;
	struct dentry *dent = file->f_path.dentry;
	struct wult_info *wi = file->private_data;

	err = kstrtobool_from_user(user_buf, count, &val);
	if (err)
		return err;

	err = debugfs_file_get(dent);
	if (err)
		return err;

	if (!strcmp(dent->d_name.name, ENABLED_FNAME))
		err = set_enabled(val);
	else if (!strcmp(dent->d_name.name, EARLY_INTR_FNAME))
		err = set_bool(wi, &wi->early_intr, val);
	else
		err = -EINVAL;

	debugfs_file_put(dent);

	if (!err)
		return count;
	return err;
}

static ssize_t dfs_read_bool_file(struct file *file, char __user *user_buf,
				  size_t count, loff_t *ppos)
{
	int err;
	bool val;
	char buf[2];
	struct dentry *dent = file->f_path.dentry;
	struct wult_info *wi = file->private_data;

	err = debugfs_file_get(dent);
	if (err)
		return err;

	if (!strcmp(dent->d_name.name, ENABLED_FNAME)) {
		val = wi->enabled;
	} else if (!strcmp(dent->d_name.name, EARLY_INTR_FNAME)) {
		val = wi->early_intr;
	} else {
		err = -EINVAL;
		goto error;
	}

	if (val)
		buf[0] = 'Y';
	else
		buf[0] = 'N';
	buf[1] = '\n';

	err = simple_read_from_buffer(user_buf, count, ppos, buf, 2);

error:
	debugfs_file_put(dent);
	return err;
}

/* Wult debugfs operations for the 'enabled', and other files. */
static const struct file_operations dfs_ops_bool = {
	.read = dfs_read_bool_file,
	.write = dfs_write_bool_file,
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

	debugfs_create_file(ENABLED_FNAME, 0644, wi->dfsroot, wi,
			    &dfs_ops_bool);
	debugfs_create_file(EARLY_INTR_FNAME, 0644, wi->dfsroot, wi,
			    &dfs_ops_bool);

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
