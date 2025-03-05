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

static int set_enabled(bool enabled)
{
	int err = 0;

	if (enabled)
		err = wult_enable();
	else
		wult_disable();

	return err;
}

static ssize_t dfs_write_bool_file(struct file *file,
				   const char __user *user_buf,
				   size_t count, loff_t *ppos)
{
	int err;
	bool val;
	struct dentry *dent = file->f_path.dentry;

	err = kstrtobool_from_user(user_buf, count, &val);
	if (err)
		return err;

	err = debugfs_file_get(dent);
	if (err)
		return err;

	if (!strcmp(dent->d_name.name, ENABLED_FNAME))
		err = set_enabled(val);
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

static ssize_t dfs_read_ro_u64_file(struct file *file, char __user *user_buf,
				    size_t count, loff_t *ppos)
{
	struct dentry *dent = file->f_path.dentry;
	struct wult_info *wi = file->private_data;
	char buf[32];
	int err, len;
	ssize_t res;
	u64 val;

	err = debugfs_file_get(dent);
	if (err)
		return err;

	if (!strcmp(dent->d_name.name, LDIST_MIN_FNAME)) {
		val = wi->wdi->ldist_min;
	} else if (!strcmp(dent->d_name.name, LDIST_MAX_FNAME)) {
		val = wi->wdi->ldist_max;
	} else {
		res = -EINVAL;
		goto out;
	}

	len = snprintf(buf, ARRAY_SIZE(buf), "%llu\n", val);
	res = simple_read_from_buffer(user_buf, count, ppos, buf, len);
out:
	debugfs_file_put(dent);
	return res;
}

/* Wult debugfs operations for R/O files backed by u64 variables. */
static const struct file_operations dfs_ops_ro_u64 = {
	.read = dfs_read_ro_u64_file,
	.open = simple_open,
	.llseek = default_llseek,
};

static ssize_t dfs_read_rw_u64_file(struct file *file, char __user *user_buf,
				    size_t count, loff_t *ppos)
{
	struct dentry *dent = file->f_path.dentry;
	struct wult_info *wi = file->private_data;
	char buf[32];
	int err, len;
	ssize_t res;
	u64 val;

	err = debugfs_file_get(dent);
	if (err)
		return err;

	mutex_lock(&wi->enable_mutex);
	if (!strcmp(dent->d_name.name, LDIST_FROM_FNAME)) {
		val = wi->ldist_from;
	} else if (!strcmp(dent->d_name.name, LDIST_TO_FNAME)) {
		val = wi->ldist_to;
	} else {
		err = -EINVAL;
	}
	mutex_unlock(&wi->enable_mutex);

	if (err) {
		res = -EINVAL;
		goto out;
	}

	len = snprintf(buf, ARRAY_SIZE(buf), "%llu\n", val);
	res = simple_read_from_buffer(user_buf, count, ppos, buf, len);
out:
	debugfs_file_put(dent);
	return res;
}

static ssize_t dfs_write_rw_u64_file(struct file *file,
				     const char __user *user_buf,
				     size_t count, loff_t *ppos)
{
	struct dentry *dent = file->f_path.dentry;
	struct wult_info *wi = file->private_data;
	int err;
	ssize_t len;
	char buf[32];
	u64 val;

	err = debugfs_file_get(dent);
	if (err)
		return err;

	len = simple_write_to_buffer(buf, ARRAY_SIZE(buf), ppos, user_buf,
				     count);
	if (len < 0)
		goto out;

	buf[len] = '\0';
	err = kstrtoull(buf, 0, &val);
	if (err) {
		len = err;
		goto out;
	}

	mutex_lock(&wi->enable_mutex);
	if (wi->enabled) {
		/* Forbid changes if measurements are enabled. */
		err = -EBUSY;
		goto out_unlock;
	}

	err = -EINVAL;
	if (val > wi->wdi->ldist_max || val < wi->wdi->ldist_min)
		goto out_unlock;

	if (!strcmp(dent->d_name.name, LDIST_FROM_FNAME)) {
		if (val > wi->ldist_to)
			goto out_unlock;
		wi->ldist_from = val;
	} else if (!strcmp(dent->d_name.name, LDIST_TO_FNAME)) {
		if (val < wi->ldist_from)
			goto out_unlock;
		wi->ldist_to = val;
	} else {
		goto out_unlock;
	}
	mutex_unlock(&wi->enable_mutex);

out:
	debugfs_file_put(dent);
	return len;

out_unlock:
	mutex_unlock(&wi->enable_mutex);
	debugfs_file_put(dent);
	return err;
}

/* Wult debugfs operations for R/W files backed by u64 variables. */
static const struct file_operations dfs_ops_rw_u64 = {
	.read = dfs_read_rw_u64_file,
	.write = dfs_write_rw_u64_file,
	.open = simple_open,
	.llseek = default_llseek,
};

int wult_uapi_device_register(struct wult_info *wi)
{
	wi->dfsroot = debugfs_create_dir(DRIVER_NAME, NULL);
	if (IS_ERR(wi->dfsroot))
		return PTR_ERR(wi->dfsroot);

	debugfs_create_file(ENABLED_FNAME, 0644, wi->dfsroot, wi,
			    &dfs_ops_bool);
	debugfs_create_file(LDIST_MIN_FNAME, 0444, wi->dfsroot, wi,
			    &dfs_ops_ro_u64);
	debugfs_create_file(LDIST_MAX_FNAME, 0444, wi->dfsroot, wi,
			    &dfs_ops_ro_u64);
	debugfs_create_file(LDIST_FROM_FNAME, 0644, wi->dfsroot, wi,
			    &dfs_ops_rw_u64);
	debugfs_create_file(LDIST_TO_FNAME, 0644, wi->dfsroot, wi,
			    &dfs_ops_rw_u64);

	return 0;
}

void wult_uapi_device_unregister(struct wult_info *wi)
{
	debugfs_remove_recursive(wi->dfsroot);
}
