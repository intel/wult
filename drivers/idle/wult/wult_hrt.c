// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2021 Intel Corporation
 * Authors: Antti Laakso <antti.laakso@intel.com>
 *          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#define DRIVER_NAME "wult_hrt"

#include <linux/cpufeature.h>
#include <linux/hrtimer.h>
#include <linux/ktime.h>
#include <linux/module.h>
#include <linux/time.h>
#include <asm/cpu_device_id.h>
#include <asm/intel-family.h>
#include <asm/msr.h>
#include "wult.h"

#define TRACEPOINT_NAME "hrtimer_expire_entry"

/* Maximum supported launch distance in nanoseconds. */
#define LDIST_MAX 50000000

/*
 * Get a 'struct wult_hrt' pointer by memory address of its 'wdi' field.
 */
#define wdi_to_wt(wdi) container_of(wdi, struct wult_hrt, wdi)

struct wult_hrt {
	struct hrtimer timer;
	struct wult_device_info wdi;
	u64 ltime;
	struct tracepoint *tp;
	int cpunum;
};

static struct wult_hrt wult_hrt = {
	.wdi = { .devname = DRIVER_NAME, },
};

static enum hrtimer_restart timer_interrupt(struct hrtimer *hrtimer)
{
	return HRTIMER_NORESTART;
}

static u64 get_time_before_idle(struct wult_device_info *wdi, u64 *adj)
{
	*adj = 0;
	return ktime_get_ns();
}

static u64 get_time_after_idle(struct wult_device_info *wdi, u64 *adj)
{
	*adj = 0;
	return ktime_get_ns();
}

static int arm_event(struct wult_device_info *wdi, u64 *ldist)
{
	struct wult_hrt *wt = wdi_to_wt(wdi);

	wt->ltime = ktime_get_ns() + *ldist;
	hrtimer_start(&wt->timer, ns_to_ktime(wt->ltime), HRTIMER_MODE_ABS_PINNED_HARD);
	return 0;
}

static bool event_has_happened(struct wult_device_info *wdi)
{
	struct wult_hrt *wt = wdi_to_wt(wdi);

	return hrtimer_get_remaining(&wt->timer) <= 0;
}

static u64 get_launch_time(struct wult_device_info *wdi)
{
	return wdi_to_wt(wdi)->ltime;
}

static void hrtimer_expire_entry_hook(void *data, struct hrtimer *hrtimer, ktime_t *now)
{
	struct wult_hrt *wt = data;

	if (smp_processor_id() != wt->cpunum)
		/* Not the CPU we are measuring. */
		return;

	if (hrtimer != &wt->timer)
		/* Not the timer we armed. */
		return;

	wult_interrupt_start();
	wult_interrupt_finish(0);
}

static int enable(struct wult_device_info *wdi, bool enable)
{
	struct wult_hrt *wt = wdi_to_wt(wdi);
	int err;

	if (!wt->tp) {
		wult_err("failed to initialize the '%s' tracepoint", TRACEPOINT_NAME);
		return -EINVAL;
	}

	if (enable) {
		err = tracepoint_probe_register(wt->tp,
				(void *)hrtimer_expire_entry_hook, wt);
		if (err) {
			wult_err("failed to register the '%s' tracepoint probe,"
				" error %d", TRACEPOINT_NAME, err);
			return err;
		}
	} else {
		tracepoint_probe_unregister(wt->tp,
				(void *)hrtimer_expire_entry_hook, wt);
	}

	return 0;
}

static int init_device(struct wult_device_info *wdi, int cpunum)
{
	struct wult_hrt *wt = wdi_to_wt(wdi);

	wt->tp = wult_tracer_find_tracepoint(TRACEPOINT_NAME);
	if (!wt->tp)
		return -EINVAL;

	wt->cpunum = cpunum;
	hrtimer_init(&wt->timer, CLOCK_MONOTONIC, HRTIMER_MODE_ABS_PINNED_HARD);
	wt->timer.function = &timer_interrupt;
	return 0;
}

static void exit_device(struct wult_device_info *wdi)
{
	struct wult_hrt *wt = wdi_to_wt(wdi);

	hrtimer_cancel(&wt->timer);
	wt->tp = NULL;
}

static struct wult_device_ops wult_hrt_ops = {
	.get_time_before_idle = get_time_before_idle,
	.get_time_after_idle = get_time_after_idle,
	.get_intr_time = get_time_after_idle,
	.arm = arm_event,
	.event_has_happened = event_has_happened,
	.get_launch_time = get_launch_time,
	.enable = enable,
	.init = init_device,
	.exit = exit_device,
};

static const struct x86_cpu_id intel_cpu_ids[] = {
	X86_MATCH_VENDOR_FAM(INTEL, 6, NULL),
	{}
};
MODULE_DEVICE_TABLE(x86cpu, intel_cpu_ids);

static int __init wult_hrt_init(void)
{
	const struct x86_cpu_id *id;

	id = x86_match_cpu(intel_cpu_ids);
	if (!id) {
		wult_err("unsupported Intel CPU family, required family 6 or higher");
		return -EINVAL;
	}

	wult_hrt.wdi.ldist_min = 1;
	wult_hrt.wdi.ldist_max = LDIST_MAX;
	wult_hrt.wdi.ldist_gran = hrtimer_resolution;
	wult_hrt.wdi.ops = &wult_hrt_ops;

	return wult_register(&wult_hrt.wdi);
}
module_init(wult_hrt_init);

static void __exit wult_hrt_exit(void)
{
	wult_unregister();
}
module_exit(wult_hrt_exit);

MODULE_DESCRIPTION("Wult delayed event driver based Linux high resolution timer");
MODULE_AUTHOR("Artem Bityutskiy");
MODULE_AUTHOR("Antti Laakso");
MODULE_LICENSE("GPL v2");
