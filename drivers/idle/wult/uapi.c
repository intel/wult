// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2020, Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#include <linux/debugfs.h>
#include <linux/err.h>
#include <linux/errno.h>
#include <linux/fs.h>
#include "tracer.h"
#include "uapi.h"
#include "wult.h"

static ssize_t dfs_write_enabled_file(struct file *file,
				      const char __user *user_buf, size_t count,
				      loff_t *ppos)
{
	int err;

	err = wult_enable();
	if (err)
		return err;

	return debugfs_write_file_bool(file, user_buf, count, ppos);
}

/* Wult debugfs operations for the 'enabled' file. */
static const struct file_operations dfs_ops_enabled = {
	.read = debugfs_read_file_bool,
	.write = dfs_write_enabled_file,
	.open = simple_open,
	.llseek = default_llseek,
};

static ssize_t dfs_read_u64_file(struct file *file, char __user *user_buf,
				 size_t count, loff_t *ppos)
{
	struct dentry *dent = file->f_path.dentry;
	struct wult_info *wi;
	char buf[32];
	int err, len;
	ssize_t res;
	u64 val;

	err = debugfs_file_get(dent);
	if (err)
		return err;

	wi = file->private_data;
	if (!strcmp(dent->d_name.name, LDIST_MIN_DFS_NAME)) {
		val = wi->wdi->ldist_min;
	} else if (!strcmp(dent->d_name.name, LDIST_MAX_DFS_NAME)) {
		val = wi->wdi->ldist_max;
	} else if (!strcmp(dent->d_name.name, LDIST_RES_DFS_NAME)) {
		val = wi->wdi->ldist_gran;
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

/* Wult debugfs operations for R/O files backed by an u64 variable. */
static const struct file_operations dfs_ops_u64 = {
	.read = dfs_read_u64_file,
	.open = simple_open,
	.llseek = default_llseek,
};

static ssize_t dfs_read_atomic64_file(struct file *file, char __user *user_buf,
				      size_t count, loff_t *ppos)
{
	struct dentry *dent = file->f_path.dentry;
	struct wult_info *wi;
	char buf[32];
	int err, len;
	ssize_t res;
	u64 val;

	err = debugfs_file_get(dent);
	if (err)
		return err;

	wi = file->private_data;
	if (!strcmp(dent->d_name.name, LDIST_FROM_DFS_NAME)) {
		val = atomic64_read(&wi->ldist_from);
	} else if (!strcmp(dent->d_name.name, LDIST_TO_DFS_NAME)) {
		val = atomic64_read(&wi->ldist_to);
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

static ssize_t dfs_write_atomic64_file(struct file *file, const char __user *user_buf,
				       size_t count, loff_t *ppos)
{
	struct dentry *dent = file->f_path.dentry;
	struct wult_info *wi;
	int err;
	ssize_t res;
	char buf[32];
	atomic64_t *dest;
	u64 val;

	err = debugfs_file_get(dent);
	if (err)
		return err;

	wi = file->private_data;

	if (!strcmp(dent->d_name.name, LDIST_FROM_DFS_NAME)) {
		dest = &wi->ldist_from;
	} else if (!strcmp(dent->d_name.name, LDIST_TO_DFS_NAME)) {
		dest = &wi->ldist_to;
	} else {
		err = -EINVAL;
		goto out;
	}

	snprintf(buf, ARRAY_SIZE(buf), "%lld", atomic64_read(dest));
	res = simple_write_to_buffer(buf, ARRAY_SIZE(buf), ppos, user_buf,
			             count);
	if (res < 0)
		goto out;

        err = kstrtoull(buf, 0, &val);
        if (err)
                goto out;

	atomic64_set(dest, val);

out:
	debugfs_file_put(dent);
	return res;
}

/* Wult debugfs operations for R/W files backed by an atomic64 variable. */
static const struct file_operations dfs_ops_atomic64 = {
	.read = dfs_read_atomic64_file,
	.write = dfs_write_atomic64_file,
	.open = simple_open,
	.llseek = default_llseek,
};

int wult_uapi_device_register(struct wult_info *wi)
{
	wi->dfsroot = debugfs_create_dir(DRIVER_NAME, NULL);
	if (IS_ERR(wi->dfsroot))
		return PTR_ERR(wi->dfsroot);

	debugfs_create_file(LDIST_FROM_DFS_NAME, 0644, wi->dfsroot, wi,
			    &dfs_ops_atomic64);
	debugfs_create_file(LDIST_TO_DFS_NAME, 0644, wi->dfsroot, wi,
			    &dfs_ops_atomic64);
	debugfs_create_file(LDIST_MIN_DFS_NAME, 0444, wi->dfsroot, wi,
			    &dfs_ops_u64);
	debugfs_create_file(LDIST_MAX_DFS_NAME, 0444, wi->dfsroot, wi,
			    &dfs_ops_u64);
	debugfs_create_file(LDIST_RES_DFS_NAME, 0444, wi->dfsroot, wi,
			    &dfs_ops_u64);
	debugfs_create_file(ENABLED_DFS_NAME, 0644, wi->dfsroot, &wi->enabled,
			    &dfs_ops_enabled);

	return 0;
}

void wult_uapi_device_unregister(struct wult_info *wi)
{
	debugfs_remove_recursive(wi->dfsroot);
}
