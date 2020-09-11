// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2020, Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#include <linux/debugfs.h>
#include <linux/cpufeature.h>
#include <linux/delay.h>
#include <linux/err.h>
#include <linux/errno.h>
#include <linux/fs.h>
#include <linux/kthread.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/processor.h>
#include <linux/random.h>
#include <linux/smp.h>
#include <linux/spinlock.h>
#include <asm/div64.h>
#include "tracer.h"
#include "uapi.h"
#include "wult.h"

#define MAX_ARM_RETRIES 128

/* Default launch distance range in nanoseconds. */
#define DEFAULT_LDIST_FROM 1000ULL
#define DEFAULT_LDIST_TO 4000000ULL

/* TODO: this whole thing should use sysfs and bus/device model. */

/* CPU number to measure wake latency on. */
static unsigned int cpunum;

/* The wult driver information object. */
struct wult_info wi;

/*
 * This mutex protect 'wi.pdev' and serializes delayed event driver
 * registration and removal.
 */
static DEFINE_MUTEX(wi_mutex);

/* Disable the measurements. */
int wult_enable_nolock(void)
{
	int err;

	wult_dbg("enabling");
	err = wult_tracer_enable(&wi);
	if (err) {
		wult_err("failed to enable the tracer, error %d", err);
		return err;
	}

	wi.enabled = true;
	atomic_set(&wi.events_armed, 0);
	atomic_set(&wi.events_happened, 0);
	wake_up(&wi.armer_wq);

	return 0;
}

void wult_disable_nolock(void)
{
	wult_dbg("disabling");
	wi.enabled = false;
	wult_tracer_disable(&wi);
}

/* Disable the measurements. */
void wult_disable(void)
{
	spin_lock(&wi.enable_lock);
	if (wi.enabled)
		wult_disable_nolock();
	spin_unlock(&wi.enable_lock);
}

bool wult_is_enabled(void)
{
	bool enabled;

	spin_lock(&wi.enable_lock);
	enabled = wi.enabled;
	spin_unlock(&wi.enable_lock);
	return enabled;
}

/*
 * The delayed event device driver should call this function from its event
 * (interrupt) handler.
 */
void wult_interrupt(void)
{
	WRITE_ONCE(wi.event_cpu, smp_processor_id());
	atomic_inc(&wi.events_happened);
	wake_up(&wi.armer_wq);
}
EXPORT_SYMBOL_GPL(wult_interrupt);

/* Pick random launch distance. */
static u64 pick_ldist(void)
{
	u64 ldist_from, ldist_to, ldist;

	ldist_from = atomic64_read(&wi.ldist_from);
	ldist_to = atomic64_read(&wi.ldist_to);
	if (ldist_from > ldist_to)
		ldist_from = ldist_to;

	/* Get random ldist within the range. */
	ldist = get_random_u64();
	ldist = do_div(ldist, ldist_to - ldist_from + 1);
	ldist += ldist_from;

	/* Ensure the ldist_gran. */
	if (wi.wdi->ldist_gran > 1) {
		ldist += wi.wdi->ldist_gran - 1;
		do_div(ldist, wi.wdi->ldist_gran);
		ldist *= wi.wdi->ldist_gran;
	}

	return ldist;
}

/* Initialize the delayed event device driver. */
static int delayed_event_device_init(struct wult_device_info *wdi,
		                     unsigned int cpunum)
{
	int err;

	err = wdi->ops->init(wdi, cpunum);
	if (err) {
		wult_err("failed to initialize the delayed event device, error %d",
			 err);
		goto out_err;
	}

	if (wdi->ldist_gran > WULT_MAX_RESOLUTION) {
		wult_err("device '%s' lauch distance resolution is %u ns, wich is too coarse, max is %d ns",
			 wdi->devname, wdi->ldist_gran, WULT_MAX_RESOLUTION);
		wi.wdi->ops->exit(wi.wdi);
		err = -EINVAL;
		goto out_err;
	}

out_err:
	wi.wdi->initialized = true;
	wi.wdi->init_err = err;
	return err;
}

/*
 * The armer kernel thread. The main function of this thread is to arm the
 * delayed timer.
 */
static int armer_kthread(void *data)
{
	int err;
	unsigned int timeout, events_happened, events_armed, event_cpu;
	unsigned int wrong_cpu_cnt = 0;
	u64 ldist;

	wult_dbg("started on CPU%d", smp_processor_id());

	/* Initialize the delayed event driver. */
	err = delayed_event_device_init(wi.wdi, wi.cpunum);
	/* Indicate that delayed event device initialization is complete */
	wake_up(&wi.armer_wq);
	if (err)
		return err;

	while (!kthread_should_stop()) {
		/* Sleep until we are enabled or asked to exit. */
		wait_event(wi.armer_wq,
			   wult_is_enabled() || kthread_should_stop());

		if (kthread_should_stop())
			break;

		if (smp_processor_id() != wi.cpunum) {
			wult_trerr("armer thread runs on CPU%u instead of CPU%u",
				   smp_processor_id(), wi.cpunum);
			goto error;
		}

		event_cpu = READ_ONCE(wi.event_cpu);
		if (event_cpu != wi.cpunum && ++wrong_cpu_cnt > 128) {
			wult_trerr("delayed event happened on CPU%u instead of CPU%u %u times, stop measuring",
				   event_cpu, wi.cpunum, wrong_cpu_cnt);
			goto error;
		}

		events_happened = atomic_read(&wi.events_happened);
		events_armed = atomic_read(&wi.events_armed);
		if (events_armed != events_happened) {
			wult_trerr("events count mismatch: armed %u, got %u",
				   events_armed, events_happened);
			goto error;
		}

		ldist = pick_ldist();
		err = wult_tracer_arm_event(&wi, &ldist);
		if (err)
			goto error;

		atomic_inc(&wi.events_armed);

		timeout = ktime_to_ms(ns_to_ktime(ldist)) + 1000;
		err = wait_event_timeout(wi.armer_wq,
			 atomic_read(&wi.events_happened) != events_happened,
			 msecs_to_jiffies(timeout));
		if (err == 0 && wult_is_enabled()) {
			wult_trerr("delayed event timed out, waited %ums",
				   timeout);
			goto error;
		}

		/* Send the last measurement data to user-space. */
		wult_tracer_send_data(&wi);
	}

	wult_dbg("exiting");
	wi.wdi->ops->exit(wi.wdi);
	return 0;

error:
	wult_disable();

	/* Wait for the stop event. */
	while (!kthread_should_stop()) {
		__set_current_state(TASK_INTERRUPTIBLE);
		schedule();
	}

	wi.wdi->ops->exit(wi.wdi);
	return -EINVAL;
}

/* Initialize wult device information object 'wdi'. */
static void init_wdi(struct wult_device_info *wdi)
{
	memset(&wi, 0, sizeof(struct wult_info));
	wi.wdi = wdi;
	wdi->priv = &wi;
	wi.cpunum = cpunum;
	atomic64_set(&wi.ldist_from, max(wdi->ldist_min, DEFAULT_LDIST_FROM));
	atomic64_set(&wi.ldist_to, min(wdi->ldist_max, DEFAULT_LDIST_TO));
	spin_lock_init(&wi.enable_lock);
	init_waitqueue_head(&wi.armer_wq);
	/*
	 * Claculate 'mult' and 'shift' that will further be used for converting
	 * count of cycles to nanoseconds.
	 */
	clocks_calc_mult_shift(&wdi->mult, &wdi->shift, tsc_khz * 1000,
			       NSEC_PER_SEC, WULT_CYC2NS_MAXSEC);
}

/*
 * Register the delayed event device, which will be used for arming events in
 * the future in order to measure wake latency.
 */
int wult_register(struct wult_device_info *wdi)
{
	int err = -EINVAL;
	if (!try_module_get(THIS_MODULE))
		return -ENODEV;

	mutex_lock(&wi_mutex);
	if (wi.wdi) {
		wult_err("already have device '%s' registered", wi.wdi->devname);
		goto err_put;
	}

	init_wdi(wdi);

	err = wult_tracer_init(&wi);
	if (err) {
		wult_err("failed to initialize the tracer, error %d", err);
		goto err_put;
	}

	wi.armer = kthread_create(armer_kthread, &wi, WULT_KTHREAD_NAME);
	if (IS_ERR(wi.armer)) {
		err = PTR_ERR(wi.armer);
		wult_err("failed to create the '%s' kernel thread, error %d",
			 WULT_KTHREAD_NAME, err);
		goto err_tracer;
	}

	kthread_bind(wi.armer, wi.cpunum);
	wake_up_process(wi.armer);

	/* Wait for the delayed event driver to finish initialization. */
	wait_event(wi.armer_wq, wi.wdi->initialized);
	if (wi.wdi->init_err) {
		err = wi.wdi->init_err;
		goto err_tracer;
	}

	err = wult_dfs_create();
	if (err) {
		wult_err("failed to create debugfs files, error %d", err);
		goto err_kthread;
	}
	mutex_unlock(&wi_mutex);

	wult_msg("registered device '%s', resolution: %u ns",
		 wdi->devname, wdi->ldist_gran);
	return 0;

err_kthread:
	kthread_stop(wi.armer);
err_tracer:
	wult_tracer_exit(&wi);
err_put:
	mutex_unlock(&wi_mutex);
	module_put(THIS_MODULE);
	return err;
}
EXPORT_SYMBOL_GPL(wult_register);

/* Unregister the delayed event source. */
void wult_unregister(void)
{
	wult_msg("unregistering device '%s'", wi.wdi->devname);

	wult_dfs_remove();
	wult_disable();
	kthread_stop(wi.armer);
	wult_tracer_exit(&wi);

	mutex_lock(&wi_mutex);
	wi.wdi = NULL;
	mutex_unlock(&wi_mutex);

	module_put(THIS_MODULE);
	return;
}
EXPORT_SYMBOL_GPL(wult_unregister);

/* Module initialization function. */
static int __init wult_init(void)
{
	if (cpunum >= NR_CPUS) {
		wult_err("bad CPU number '%d', max. is %d", cpunum, NR_CPUS - 1);
		return -EINVAL;
	}

	if (boot_cpu_data.x86_vendor == X86_VENDOR_INTEL &&
	    boot_cpu_data.x86 < 6) {
		wult_err("unsupported Intel CPU family %d, required family 6 "
		         "or higher", boot_cpu_data.x86);
		return -EINVAL;
	}

	if (!cpu_has(&cpu_data(cpunum), X86_FEATURE_CONSTANT_TSC)) {
		wult_err("constant TSC is required");
		return -EINVAL;
	}

	wi.cpunum = cpunum;

	return 0;
}
module_init(wult_init);

/* Module exit function. */
static void __exit wult_exit(void)
{
}
module_exit(wult_exit);

module_param(cpunum, uint, 0444);
MODULE_PARM_DESC(cpunum, "CPU number to measure wake latency on, default is "
			 "CPU0.");

MODULE_VERSION(WULT_VERSION);
MODULE_DESCRIPTION("wake up latency measurement driver.");
MODULE_AUTHOR("Artem Bityutskiy");
MODULE_LICENSE("GPL v2");
