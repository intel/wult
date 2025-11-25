// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2024 Intel Corporation
 * Author: Adam Hawley <adam.james.hawley@intel.com>
 */

#define pr_fmt(fmt)	KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/debugfs.h>
#include <linux/fs.h>
#include <linux/delay.h>
#include <linux/acpi.h>
#include <linux/irq.h>
#include <linux/irqdomain.h>
#include <asm/apic.h>
#include <linux/ktime.h>
#include <linux/kstrtox.h>
#include <linux/kthread.h>

#include "compat.h"

#define DRIVER_NAME "pbe"
#define PBE_VERSION "1.0"

#define pbe_msg(fmt, ...) \
	pr_notice(DRIVER_NAME ": " fmt "\n", ##__VA_ARGS__)
#define pbe_err(fmt, ...) \
	pr_err(DRIVER_NAME " error: " fmt "\n", ##__VA_ARGS__)

/* LDIST min/max values are in us */
#define LDIST_MIN	10
#define LDIST_DEFAULT	100
#define LDIST_MAX	1000000

/* Use the 'X86_PLATFORM_IPI_VECTOR' value as the IPI vector for waking up CPUs. */
#define IPI_VECTOR	0xf7

/* Driver's root debugfs directory. */
static struct dentry *dfsroot;
static bool enable;
static u64 ldist = LDIST_DEFAULT;
static u64 ldist_min = LDIST_MIN;
static u64 ldist_max = LDIST_MAX;
static struct task_struct *thread;
static unsigned int cpu;

static void pbe_wakeup(void)
{
	struct cpumask mask;

	/* Initialize cpumask */
	cpumask_copy(&mask, cpu_online_mask);
	cpumask_andnot(&mask, &mask, cpumask_of(cpu));

	__apic_send_IPI_mask(&mask, IPI_VECTOR);
}

static int pbe_thread(void *unused)
{
	while (!kthread_should_stop() && enable) {
		usleep_range(ldist, ldist);
		pbe_wakeup();
	}
	return 0;
}

static ssize_t pbe_write_file_enable(struct file *file,
				     const char __user *user_buf,
				     size_t count, loff_t *ppos)
{
	int ret;

	ret = kstrtobool_from_user(user_buf, count, &enable);
	if (ret)
		return ret;

	if (enable) {
		if (thread)
			return -EBUSY;

	        thread = kthread_create(pbe_thread, NULL, "pbe");
		if (IS_ERR(thread))
			return PTR_ERR(thread);

		kthread_bind(thread, cpu);
		wake_up_process(thread);
		pbe_msg("thread started with launch distance %llu", ldist);
	} else {
		if (!thread)
			return -ENODEV;

		enable = false;

		kthread_stop(thread);
		thread = NULL;
		pbe_msg("thread stopped");
	}

	return count;
}

static const struct file_operations pbe_enable_fops = {
	.read =		debugfs_read_file_bool,
	.write =	pbe_write_file_enable,
	.open =		simple_open,
	.llseek =	default_llseek,
};

static int pbe_val_set(void *data, u64 val)
{
	val = val / 1000;

	if (val < LDIST_MIN || val > LDIST_MAX)
		return -EINVAL;

	*(u64 *)data = val;

	return 0;
}

static int pbe_val_get(void *data, u64 *val)
{
	*val = *(u64 *)data * 1000;
	return 0;
}

static int pbe_rw_fops_open(struct inode *inode, struct file *file)
{
	int ret;

	ret = simple_attr_open(inode, file, pbe_val_get, pbe_val_set, "%llu\n");
	if (!ret)
		file->f_mode |= FMODE_LSEEK;
	return ret;
}

static const struct file_operations pbe_rw_fops = {
	.owner		= THIS_MODULE,
	.open		= pbe_rw_fops_open,
	.release	= simple_attr_release,
	.read		= debugfs_attr_read,
	.write		= debugfs_attr_write,
	.llseek		= noop_llseek,
};

static int pbe_ro_fops_open(struct inode *inode, struct file *file)
{
	int ret;

	ret = simple_attr_open(inode, file, pbe_val_get, NULL, "%llu\n");
	if (!ret)
		file->f_mode |= FMODE_LSEEK;

	return ret;
}

static const struct file_operations pbe_ro_fops = {
	.owner		= THIS_MODULE,
	.open		= pbe_ro_fops_open,
	.release	= simple_attr_release,
	.read		= debugfs_attr_read,
	.llseek		= noop_llseek,
};

/* Module initialization function. */
static int __init pbe_init(void)
{
	if (cpu >= NR_CPUS) {
		pbe_err("bad CPU number '%d', max. is %d", cpu, NR_CPUS - 1)
;
		return -EINVAL;
	}

	dfsroot = debugfs_create_dir(DRIVER_NAME, NULL);
	if (IS_ERR(dfsroot))
		return PTR_ERR(dfsroot);

	debugfs_create_file("enabled", 0644, dfsroot, &enable, &pbe_enable_fops);
	debugfs_create_file("ldist_nsec", 0644, dfsroot, &ldist, &pbe_rw_fops);
	debugfs_create_file("ldist_min_nsec", 0444, dfsroot, &ldist_min, &pbe_ro_fops);
	debugfs_create_file("ldist_max_nsec", 0444, dfsroot, &ldist_max, &pbe_ro_fops);

	return 0;
}
module_init(pbe_init);

/* Module exit function. */
static void __exit pbe_exit(void)
{
	if (enable) {
		enable = false;
		kthread_stop(thread);
		pbe_msg("thread stopped");
	}

	debugfs_remove_recursive(dfsroot);
}
module_exit(pbe_exit);

module_param(cpu, uint, 0444);
MODULE_PARM_DESC(cpu, "CPU number to run the pbe thread on, default is CPU0.");

MODULE_VERSION(PBE_VERSION);
MODULE_DESCRIPTION("The pbe driver.");
MODULE_AUTHOR("Adam Hawley");
MODULE_LICENSE("GPL v2");
