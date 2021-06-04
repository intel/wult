// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2020, Intel Corporation
 * Authors: Antti Laakso <antti.laakso@intel.com>
 *          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#define DRIVER_NAME "wult_hrtimer"

#include <linux/cpufeature.h>
#include <linux/hrtimer.h>
#include <linux/ktime.h>
#include <linux/module.h>
#include <linux/time.h>
#include "wult.h"

/* Maximum supported launch distance in nanoseconds. */
#define LDIST_MAX 10000000

/*
 * Get a 'struct wult_hrtimer' pointer by memory address of its 'wdi' field.
 */
#define wdi_to_wt(wdi) container_of(wdi, struct wult_hrtimer, wdi)

struct wult_hrtimer {
	struct hrtimer timer;
	struct wult_device_info wdi;
	u64 ltime;
};

static struct wult_hrtimer wult_hrtimer = {
	.wdi = { .devname = DRIVER_NAME, },
};

static enum hrtimer_restart timer_interrupt(struct hrtimer *hrtimer)
{
	wult_interrupt(ktime_get_raw_ns());

	return HRTIMER_NORESTART;
}

static u64 get_time_before_idle(struct wult_device_info *wdi)
{
	return ktime_get_raw_ns();
}

static u64 get_time_after_idle(struct wult_device_info *wdi, u64 cyc)
{
	return ktime_get_raw_ns();
}

static int arm_event(struct wult_device_info *wdi, u64 *ldist)
{
	struct wult_hrtimer *wt = wdi_to_wt(wdi);

	hrtimer_start(&wt->timer, ns_to_ktime(*ldist), HRTIMER_MODE_REL_PINNED_HARD);
	wt->ltime = ktime_get_raw_ns() + *ldist;
	return 0;
}

static bool event_has_happened(struct wult_device_info *wdi)
{
	struct wult_hrtimer *wt = wdi_to_wt(wdi);

	return hrtimer_get_remaining(&wt->timer) <= 0;
}

static u64 get_launch_time(struct wult_device_info *wdi)
{
	return wdi_to_wt(wdi)->ltime;
}

static u64 cyc_to_ns(struct wult_device_info *wdi, u64 cyc)
{
	return cyc;
}

static int init_device(struct wult_device_info *wdi, int cpunum)
{
	struct wult_hrtimer *wt = wdi_to_wt(wdi);

	hrtimer_init(&wt->timer, CLOCK_MONOTONIC_RAW, HRTIMER_MODE_REL_PINNED_HARD);
	wt->timer.function = &timer_interrupt;
	return 0;
}

static void exit_device(struct wult_device_info *wdi)
{
	struct wult_hrtimer *wt = wdi_to_wt(wdi);

	hrtimer_cancel(&wt->timer);
}

static struct wult_device_ops wult_hrtimer_ops = {
	.get_time_before_idle = get_time_before_idle,
	.get_time_after_idle = get_time_after_idle,
	.arm = arm_event,
	.event_has_happened = event_has_happened,
	.get_launch_time = get_launch_time,
	.time_to_ns = cyc_to_ns,
	.init = init_device,
	.exit = exit_device,
};

static int __init wult_hrtimer_init(void)
{
	if (boot_cpu_data.x86_vendor == X86_VENDOR_INTEL &&
	    boot_cpu_data.x86 < 6) {
		wult_err("unsupported Intel CPU family %d, required family 6 "
		         "or higher", boot_cpu_data.x86);
		return -EINVAL;
	}

	wult_hrtimer.wdi.ldist_min = 1;
	wult_hrtimer.wdi.ldist_max = LDIST_MAX;
	wult_hrtimer.wdi.ldist_gran = hrtimer_resolution;
	wult_hrtimer.wdi.ops = &wult_hrtimer_ops;

	return wult_register(&wult_hrtimer.wdi);
}
module_init(wult_hrtimer_init);

static void __exit wult_hrtimer_exit(void)
{
	wult_unregister();
}
module_exit(wult_hrtimer_exit);

MODULE_DESCRIPTION("Wult delayed event driver based Linux high resolution timer");
MODULE_AUTHOR("Artem Bityutskiy");
MODULE_AUTHOR("Antti Laakso");
MODULE_LICENSE("GPL v2");
