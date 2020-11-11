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

extern struct wult_info wi;

static int dfs_ldist_get(void *data, u64 *val)
{
	*val = atomic64_read(data);
	return 0;
}

static int dfs_ldist_from_set(void *data, u64 val)
{
	struct wult_device_info *wdi = wi.wdi;
	u64 ldist_from = atomic64_read(data);

	if (ldist_from < wdi->ldist_min || ldist_from > wdi->ldist_max) {
		wult_err("'%s' %llu is out of range, should be within [%llu, %llu]",
			 LDIST_FROM_DFS_NAME, ldist_from, wdi->ldist_min,
			 wdi->ldist_max);
		return -EINVAL;
	}

	if (do_div(ldist_from, wdi->ldist_gran)) {
		wult_err("'%s' must be multiple of delayed timer resolution value of %u nsec",
			 LDIST_FROM_DFS_NAME, wdi->ldist_gran);
		return -EINVAL;
	}

	atomic64_set(data, val);
	return 0;
}

static int dfs_ldist_to_set(void *data, u64 val)
{
	struct wult_device_info *wdi = wi.wdi;
	u64 ldist_to = atomic64_read(data);

	if (ldist_to < wdi->ldist_min || ldist_to > wdi->ldist_max) {
		wult_err("'%s' %llu is out of range, should be within [%llu, %llu]",
			 LDIST_TO_DFS_NAME, ldist_to, wdi->ldist_min,
			 wdi->ldist_max);
		return -EINVAL;
	}
	if (do_div(ldist_to, wdi->ldist_gran)) {
		wult_err("'%s' must be multiple of delayed timer resolution value of %u nsec",
			 LDIST_TO_DFS_NAME, wdi->ldist_gran);
		return -EINVAL;
	}

	atomic64_set(data, val);
	return 0;
}

/* Wult debugfs operations for the lauch distance limit files. */
DEFINE_DEBUGFS_ATTRIBUTE(dfs_ops_ldist_from, dfs_ldist_get, dfs_ldist_from_set,
		         "%llu\n");
DEFINE_DEBUGFS_ATTRIBUTE(dfs_ops_ldist_to, dfs_ldist_get, dfs_ldist_to_set,
		         "%llu\n");

static ssize_t dfs_read_enabled_file(struct file *file, char __user *user_buf,
				     size_t count, loff_t *ppos)
{
	ssize_t res;

	spin_lock(&wi.enable_lock);
	res = debugfs_read_file_bool(file, user_buf, count, ppos);
	spin_unlock(&wi.enable_lock);
	return res;
}

static ssize_t dfs_write_enabled_file(struct file *file,
				      const char __user *user_buf, size_t count,
				      loff_t *ppos)
{
	int err;
	bool enabled_prev;

	spin_lock(&wi.enable_lock);
	enabled_prev = wi.enabled;

	err = debugfs_write_file_bool(file, user_buf, count, ppos);
	if (err < 0)
		goto out_unlock;

	if (wi.enabled != enabled_prev) {
		if (wi.enabled)
			err = wult_enable_nolock();
		else
			wult_disable_nolock();
	}

out_unlock:
	spin_unlock(&wi.enable_lock);
	return err;
}

/* Wult debugfs operations for the 'enabled' file. */
static const struct file_operations dfs_ops_enabled = {
	.read = dfs_read_enabled_file,
	.write = dfs_write_enabled_file,
	.open = simple_open,
	.llseek = default_llseek,
};

static ssize_t dfs_read_u64_file(struct file *file, char __user *user_buf,
				 size_t count, loff_t *ppos)
{
	struct dentry *dent = file->f_path.dentry;
	struct wult_device_info *wdi = wi.wdi;
	char buf[32];
	int err, len;
	ssize_t res;
	u64 val;

	err = debugfs_file_get(dent);
	if (err)
		return err;

	if (!strcmp(dent->d_name.name, LDIST_MIN_DFS_NAME)) {
		val = wdi->ldist_min;
	} else if (!strcmp(dent->d_name.name, LDIST_MAX_DFS_NAME)) {
		val = wdi->ldist_max;
	} else if (!strcmp(dent->d_name.name, LDIST_RES_DFS_NAME)) {
		val = wdi->ldist_gran;
	} else {
		res = -EINVAL;
		goto out;
	}

	len = snprintf(buf, 32, "%llu\n", val);
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

int wult_uapi_device_register(void)
{
	wi.dfsroot = debugfs_create_dir(DRIVER_NAME, NULL);
	if (IS_ERR(wi.dfsroot))
		return PTR_ERR(wi.dfsroot);

	debugfs_create_file(LDIST_FROM_DFS_NAME, 0644, wi.dfsroot,
			    &wi.ldist_from, &dfs_ops_ldist_from);
	debugfs_create_file(LDIST_TO_DFS_NAME, 0644, wi.dfsroot, &wi.ldist_to,
			    &dfs_ops_ldist_to);
	debugfs_create_file(LDIST_MIN_DFS_NAME, 0444, wi.dfsroot, &wi,
			    &dfs_ops_u64);
	debugfs_create_file(LDIST_MAX_DFS_NAME, 0444, wi.dfsroot, &wi,
			    &dfs_ops_u64);
	debugfs_create_file(LDIST_RES_DFS_NAME, 0444, wi.dfsroot, &wi,
			    &dfs_ops_u64);
	debugfs_create_file(ENABLED_DFS_NAME, 0644, wi.dfsroot, &wi.enabled,
			    &dfs_ops_enabled);

	return 0;
}

void wult_uapi_device_unregister(void)
{
	debugfs_remove_recursive(wi.dfsroot);
}
