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
#include <linux/slab.h>
#include <linux/smp.h>
#include <linux/spinlock.h>
#include <asm/div64.h>
#include <asm/tsc.h>
#include "tracer.h"
#include "uapi.h"
#include "wult.h"

#define MAX_ARM_RETRIES 128

/* Default launch distance range in nanoseconds. */
#define DEFAULT_LDIST_FROM 1000ULL
#define DEFAULT_LDIST_TO 4000000ULL

/* TODO: this whole thing should use sysfs and bus/device model. */

/* CPU number to measure wake latency on (module parameter). */
static unsigned int cpunum;

/* The wult driver information object. */
static struct wult_info *wi;

/* Enable the measurements. */
int wult_enable(void)
{
	int err = 0;

	spin_lock(&wi->enable_lock);
	if (wi->enabled)
		goto out_unlock;

	err = wult_tracer_enable(wi);
	if (err) {
		wult_err("failed to enable the tracer, error %d", err);
		goto out_unlock;
	}

	wi->enabled = true;
	atomic_set(&wi->events_armed, 0);
	atomic_set(&wi->events_happened, 0);
	wake_up(&wi->armer_wq);

out_unlock:
	spin_unlock(&wi->enable_lock);
	return err;
}

/* Disable the measurements. */
void wult_disable(void)
{
	spin_lock(&wi->enable_lock);
	if (wi->enabled) {
		wi->enabled = false;
		wult_tracer_disable(wi);
	}
	spin_unlock(&wi->enable_lock);
}

/*
 * The delayed event device driver should call this function from its event
 * (interrupt) handler.
 */
void wult_interrupt(u64 cyc)
{
	wult_tracer_interrupt(wi, cyc);
	WRITE_ONCE(wi->event_cpu, smp_processor_id());
	atomic_inc(&wi->events_happened);
	wake_up(&wi->armer_wq);
}
EXPORT_SYMBOL_GPL(wult_interrupt);

/* Pick random launch distance. */
static u64 pick_ldist(void)
{
	u64 ldist_from, ldist_to, ldist;

	ldist_from = atomic64_read(&wi->ldist_from);
	ldist_to = atomic64_read(&wi->ldist_to);
	if (ldist_from > ldist_to)
		ldist_from = ldist_to;

	/* Get random ldist within the range. */
	ldist = get_random_u64();
	ldist = do_div(ldist, ldist_to - ldist_from + 1);
	ldist += ldist_from;

	/* Ensure the ldist_gran. */
	if (wi->wdi->ldist_gran > 1) {
		ldist += wi->wdi->ldist_gran - 1;
		do_div(ldist, wi->wdi->ldist_gran);
		ldist *= wi->wdi->ldist_gran;
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
		return err;
	}

	if (wdi->ldist_gran > WULT_MAX_LDIST_GRANULARITY) {
		wult_err("device '%s' lauch distance resolution is %u ns, wich is too coarse, max is %d ns",
			 wdi->devname, wdi->ldist_gran,
			 WULT_MAX_LDIST_GRANULARITY);
		wi->wdi->ops->exit(wi->wdi);
		return -EINVAL;
	}

	return 0;
}

/* Check if the armer threads runs on the correct CPU. */
static inline int check_armer_cpunum(void)
{
	if (smp_processor_id() != wi->cpunum) {
		wult_err("armer thread runs on CPU%u instead of CPU%u",
			 smp_processor_id(), wi->cpunum);
		return -EINVAL;
	}
	return 0;
}

/*
 * The armer kernel thread. The main function of this thread is to arm delayed
 * events.
 */
static int armer_kthread(void *data)
{
	int err;
	unsigned int timeout, events_happened, events_armed, event_cpu;
	unsigned int wrong_cpu_cnt = 0;
	u64 ldist;

	wult_dbg("started on CPU%d", smp_processor_id());

	err = check_armer_cpunum();
	if (err)
		goto init_error;

	/* Initialize the delayed event driver. */
	err = delayed_event_device_init(wi->wdi, wi->cpunum);
	if (err)
		goto init_error;

	/* Indicate that the initialization is complete. */
	wi->initialized = true;
	wake_up(&wi->armer_wq);

	while (!kthread_should_stop()) {
		/* Sleep until we are enabled or asked to exit. */
		wait_event(wi->armer_wq, wi->enabled || kthread_should_stop());

		if (kthread_should_stop())
			break;

		err = check_armer_cpunum();
		if (err)
			goto error;

		events_happened = atomic_read(&wi->events_happened);

		ldist = pick_ldist();
		err = wult_tracer_arm_event(wi, &ldist);
		if (err)
			goto error;

		atomic_inc(&wi->events_armed);

		timeout = ktime_to_ms(ns_to_ktime(ldist)) + 1000;
		err = wait_event_timeout(wi->armer_wq,
			 atomic_read(&wi->events_happened) != events_happened,
			 msecs_to_jiffies(timeout));
		if (err == 0 && wi->enabled) {
			wult_err("delayed event timed out, waited %ums", timeout);
			goto error;
		}

		/* Check that the interrupt happend on the right CPU. */
		event_cpu = READ_ONCE(wi->event_cpu);
		if (event_cpu != wi->cpunum) {
			if (wrong_cpu_cnt++ < 128)
				continue;
			wult_err("delayed event happened on CPU%u instead of CPU%u %u times, stop measuring",
				 event_cpu, wi->cpunum, wrong_cpu_cnt);
			goto error;
		}

		events_happened = atomic_read(&wi->events_happened);
		events_armed = atomic_read(&wi->events_armed);
		if (events_armed != events_happened) {
			wult_err("events count mismatch: armed %u, got %u",
				 events_armed, events_happened);
			goto error;
		}

		/* Send the last measurement data to user-space. */
		spin_lock(&wi->enable_lock);
		if (wi->enabled) {
			err = wult_tracer_send_data(wi);
			if (err) {
				spin_unlock(&wi->enable_lock);
				wult_err("failed to send data out, error %d", err);
				goto error;
			}
		}
		spin_unlock(&wi->enable_lock);
	}

	wult_dbg("exiting");
	wi->wdi->ops->exit(wi->wdi);
	return 0;

error:
	wult_disable();

	/* Wait for the stop event. */
	while (!kthread_should_stop()) {
		__set_current_state(TASK_INTERRUPTIBLE);
		schedule();
	}

	wi->wdi->ops->exit(wi->wdi);
	return -EINVAL;

init_error:
	wi->initialized = true;
	wi->init_err = err;
	wake_up(&wi->armer_wq);
	return err;
}

/* Initialize wult device information object 'wdi'. */
static void init_wdi(struct wult_device_info *wdi)
{
	memset(wi, 0, sizeof(struct wult_info));
	wi->wdi = wdi;
	wdi->priv = wi;
	wi->cpunum = cpunum;
	atomic64_set(&wi->ldist_from, max(wdi->ldist_min, DEFAULT_LDIST_FROM));
	atomic64_set(&wi->ldist_to, min(wdi->ldist_max, DEFAULT_LDIST_TO));
	spin_lock_init(&wi->enable_lock);
	init_waitqueue_head(&wi->armer_wq);
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

	mutex_lock(&wi->dev_mutex);
	if (wi->wdi) {
		wult_err("already have device '%s' registered", wi->wdi->devname);
		goto err_put;
	}

	init_wdi(wdi);

	err = wult_tracer_init(wi);
	if (err) {
		wult_err("failed to initialize the tracer, error %d", err);
		goto err_put;
	}

	wi->armer = kthread_create(armer_kthread, wi, WULT_KTHREAD_NAME);
	if (IS_ERR(wi->armer)) {
		err = PTR_ERR(wi->armer);
		wult_err("failed to create the '%s' kernel thread, error %d",
			 WULT_KTHREAD_NAME, err);
		goto err_tracer;
	}

	kthread_bind(wi->armer, wi->cpunum);
	wake_up_process(wi->armer);

	/* Wait for the delayed event driver to finish initialization. */
	wait_event(wi->armer_wq, wi->initialized);
	if (wi->init_err) {
		err = wi->init_err;
		goto err_tracer;
	}

	err = wult_uapi_device_register(wi);
	if (err) {
		wult_err("failed to create debugfs files, error %d", err);
		goto err_kthread;
	}
	mutex_unlock(&wi->dev_mutex);

	wult_msg("registered device '%s', resolution: %u ns",
		 wdi->devname, wdi->ldist_gran);
	return 0;

err_kthread:
	kthread_stop(wi->armer);
err_tracer:
	wult_tracer_exit(wi);
err_put:
	mutex_unlock(&wi->dev_mutex);
	module_put(THIS_MODULE);
	return err;
}
EXPORT_SYMBOL_GPL(wult_register);

/* Unregister the delayed event source. */
void wult_unregister(void)
{
	wult_msg("unregistering device '%s'", wi->wdi->devname);

	wult_uapi_device_unregister(wi);
	wult_disable();
	kthread_stop(wi->armer);
	wult_tracer_exit(wi);

	mutex_lock(&wi->dev_mutex);
	wi->wdi = NULL;
	mutex_unlock(&wi->dev_mutex);

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

	if (check_tsc_unstable()) {
		wult_err("TSC is marked as unstable");
		return -EINVAL;
	}

	wi = kzalloc(sizeof(struct wult_info), GFP_KERNEL);

	mutex_init(&wi->dev_mutex);
	wi->cpunum = cpunum;

	return 0;
}
module_init(wult_init);

/* Module exit function. */
static void __exit wult_exit(void)
{
	kfree(wi);
}
module_exit(wult_exit);

module_param(cpunum, uint, 0444);
MODULE_PARM_DESC(cpunum, "CPU number to measure wake latency on, default is "
			 "CPU0.");

MODULE_VERSION(WULT_VERSION);
MODULE_DESCRIPTION("wake up latency measurement driver.");
MODULE_AUTHOR("Artem Bityutskiy");
MODULE_LICENSE("GPL v2");
