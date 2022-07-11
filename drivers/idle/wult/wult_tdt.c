// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2021 Intel Corporation
 * Authors: Antti Laakso <antti.laakso@intel.com>
 *          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 *
 * This delayed event driver uses x86 TSC deadline timer. The events are armed
 * using the 'hrtimer' API, but in order to achieve higher precision, this
 * driver directly reads TSC deadline timer registers. This is not something
 * we'd be allowed to do in upstream kernel.
 */

#define DRIVER_NAME "wult_tdt"

#include <linux/cpufeature.h>
#include <linux/hrtimer.h>
#include <linux/ktime.h>
#include <linux/module.h>
#include <linux/time.h>
#include <asm/intel-family.h>
#include <asm/msr.h>
#include "wult.h"

/* Maximum supported launch distance in nanoseconds. */
#define LDIST_MAX 10000000

/*
 * Get a 'struct wult_tdt' pointer by memory address of its 'wdi' field.
 */
#define wdi_to_wt(wdi) container_of(wdi, struct wult_tdt, wdi)

struct wult_tdt {
	struct hrtimer timer;
	struct wult_device_info wdi;
	u64 deadline_before;
};

static struct wult_tdt wult_tdt = {
	.wdi = { .devname = DRIVER_NAME, },
};

static enum hrtimer_restart timer_interrupt(struct hrtimer *hrtimer)
{
	wult_interrupt_start();
	wult_interrupt_finish(0);

	return HRTIMER_NORESTART;
}

static u64 get_time_before_idle(struct wult_device_info *wdi, u64 *adj)
{
	struct wult_tdt *wt = wdi_to_wt(wdi);

	*adj = 0;

	/*
	 * This callback is invoked just before going to idle, and now we can
	 * find out what is the actual TSC deadline armed. If we wake up by a
	 * TSC deadline timer, it will be the currently programed deadline, not
	 * the timer we armed earlier in 'arm_event()'.
	 */
	rdmsrl(MSR_IA32_TSC_DEADLINE, wt->deadline_before);
	return rdtsc_ordered();
}

static u64 get_time_after_idle(struct wult_device_info *wdi, u64 *adj)
{
	*adj = 0;
	return rdtsc_ordered();
}

static int arm_event(struct wult_device_info *wdi, u64 *ldist)
{
	struct wult_tdt *wt = wdi_to_wt(wdi);

	/*
	 * The TSC deadline timers are controlled by the core kernel, and we do
	 * not have direct access to them from here. So we use hrtimes to arm
	 * events. However, whenever we arm an hrtimer, there is no guarantee
	 * our timer makes it to the HW, because there may be an earlier
	 * timer. But we arm our time anyway to make sure there is at least
	 * some timer there and we won't sleep forever.
	 */
	hrtimer_start(&wt->timer, ns_to_ktime(*ldist), HRTIMER_MODE_REL_PINNED_HARD);
	return 0;
}

static bool event_has_happened(struct wult_device_info *wdi)
{
	u64 deadline;
	struct wult_tdt *wt = wdi_to_wt(wdi);

	/*
	 * The HW zeroes out the deadline MSR value when deadline is reached,
	 * so if it is non-zero, this is not a TSC deadline timer event.
	 */
	rdmsrl(MSR_IA32_TSC_DEADLINE, deadline);
	if (deadline)
		return false;

	/* Make sure there was a TSC deadline timer armed. */
	if (wt->deadline_before == 0)
		return false;

	if (rdtsc_ordered() <= wt->deadline_before)
		return false;

	return hrtimer_get_remaining(&wt->timer) <= 0;
}

static u64 get_launch_time(struct wult_device_info *wdi)
{
	/*
	 * We piggybacked on the nearest TSC deadline, so it is our launch
	 * time.
	 */
	return wdi_to_wt(wdi)->deadline_before;
}

static int init_device(struct wult_device_info *wdi, int cpunum)
{
	struct wult_tdt *wt = wdi_to_wt(wdi);

	if (!cpu_has(&cpu_data(cpunum), X86_FEATURE_TSC_DEADLINE_TIMER)) {
		wult_err("the CPU does not support TSC deadline timers");
		return -EINVAL;
	}

	/* TODO: ensure that hrtimers are backed by the TSC dealine timer. */

	hrtimer_init(&wt->timer, CLOCK_MONOTONIC, HRTIMER_MODE_REL_PINNED_HARD);
	wt->timer.function = &timer_interrupt;
	return 0;
}

static void exit_device(struct wult_device_info *wdi)
{
	struct wult_tdt *wt = wdi_to_wt(wdi);

	hrtimer_cancel(&wt->timer);
}

static struct wult_device_ops wult_tdt_ops = {
	.get_time_before_idle = get_time_before_idle,
	.get_time_after_idle = get_time_after_idle,
	.arm = arm_event,
	.event_has_happened = event_has_happened,
	.get_launch_time = get_launch_time,
	.init = init_device,
	.exit = exit_device,
};

static int __init wult_tdt_init(void)
{
	if (boot_cpu_data.x86_vendor == X86_VENDOR_INTEL &&
	    boot_cpu_data.x86 < 6) {
		wult_err("unsupported Intel CPU family %d, required family 6 "
		         "or higher", boot_cpu_data.x86);
		return -EINVAL;
	}

	wult_tdt.wdi.ldist_min = 1;
	wult_tdt.wdi.ldist_max = LDIST_MAX;
	wult_tdt.wdi.ldist_gran = hrtimer_resolution;
	wult_tdt.wdi.ops = &wult_tdt_ops;

	return wult_register(&wult_tdt.wdi);
}
module_init(wult_tdt_init);

static void __exit wult_tdt_exit(void)
{
	wult_unregister();
}
module_exit(wult_tdt_exit);

MODULE_DESCRIPTION("Wult delayed event driver based on x86 TSC deadline timer");
MODULE_AUTHOR("Artem Bityutskiy");
MODULE_AUTHOR("Antti Laakso");
MODULE_LICENSE("GPL v2");
