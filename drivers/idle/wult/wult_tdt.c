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
#include <asm/cpu_device_id.h>
#include <asm/intel-family.h>
#include <asm/msr.h>
#include "wult.h"
#include "compat.h"

#define MSR_TRACEPOINT_NAME	"write_msr"
#define TIMER_TRACEPOINT_NAME	"local_timer_entry"

/* Maximum supported launch distance in nanoseconds. */
#define LDIST_MAX 50000000

/*
 * Get a 'struct wult_tdt' pointer by memory address of its 'wdi' field.
 */
#define wdi_to_wt(wdi) container_of(wdi, struct wult_tdt, wdi)

struct wult_tdt {
	struct hrtimer timer;
	struct wult_device_info wdi;
	u64 tsc_deadline;
	u64 ltime;
	u64 intr_tsc;
	struct tracepoint *msr_tp;
	struct tracepoint *timer_tp;
	int cpu;
	bool timer_armed;
};

static struct wult_tdt wult_tdt = {
	.wdi = { .devname = DRIVER_NAME, },
};

static enum hrtimer_restart timer_interrupt(struct hrtimer *hrtimer)
{
	struct wult_tdt *wt = container_of(hrtimer, struct wult_tdt, timer);

	wt->timer_armed = false;
	wult_interrupt_start();
	wult_interrupt_finish(0);

	return HRTIMER_NORESTART;
}

static u64 get_time_before_idle(struct wult_device_info *wdi, u64 *adj)
{
	*adj = 0;
	return rdtsc_ordered();
}

static u64 get_time_after_idle(struct wult_device_info *wdi, u64 *adj)
{
	*adj = 0;
	return rdtsc_ordered();
}

static u64 get_intr_time(struct wult_device_info *wdi, u64 *adj)
{
	struct wult_tdt *wt = wdi_to_wt(wdi);

	*adj = 0;
	return wt->intr_tsc;
}

static int arm_event(struct wult_device_info *wdi, u64 *ldist)
{
	struct wult_tdt *wt = wdi_to_wt(wdi);

	/*
	 * The TSC deadline timers are controlled by the core kernel, and we do
	 * not have direct access to them from here. So we use hrtimes to arm
	 * events. However, whenever we arm an hrtimer, there is no guarantee
	 * our timer makes it to the HW, because there may be an earlier
	 * timer. But we arm our timer anyway to make sure there is at least
	 * some timer there and we won't sleep forever.
	 */
	hrtimer_start(&wt->timer, ns_to_ktime(*ldist), HRTIMER_MODE_REL_PINNED_HARD);
	wt->timer_armed = true;

	return 0;
}

static bool event_has_happened(struct wult_device_info *wdi)
{
	struct wult_tdt *wt = wdi_to_wt(wdi);

	return hrtimer_get_remaining(&wt->timer) <= 0;
}

static u64 get_launch_time(struct wult_device_info *wdi)
{
	return wdi_to_wt(wdi)->ltime;
}

static void write_msr_hook(void *data, unsigned int msr, u64 val)
{
	struct wult_tdt *wt = data;

	if (smp_processor_id() != wt->cpu)
		/* Not the CPU we are measuring. */
		return;

	if (msr != MSR_IA32_TSC_DEADLINE)
		return;

	wt->tsc_deadline = val;
}

static void local_timer_entry_hook(void *data, int vector)
{
	struct wult_tdt *wt = data;

	if (smp_processor_id() != wt->cpu)
		/* Not the CPU we are measuring. */
		return;

	if (!wt->timer_armed)
		/* Not the timer we armed. */
		return;

	wt->intr_tsc = rdtsc_ordered();
	wt->ltime = wt->tsc_deadline;
}

static int enable(struct wult_device_info *wdi, bool enable)
{
	struct wult_tdt *wt = wdi_to_wt(wdi);
	int err;

	if (!wt->msr_tp || !wt->timer_tp) {
		wult_err("failed to initialize the '%s' tracepoint",
			 !wt->msr_tp ? MSR_TRACEPOINT_NAME : TIMER_TRACEPOINT_NAME);
		return -EINVAL;
	}

	if (enable) {
		err = tracepoint_probe_register(wt->msr_tp,
				(void *)write_msr_hook, wt);
		if (err) {
			wult_err("failed to register the '%s' tracepoint probe,"
				 " error %d", MSR_TRACEPOINT_NAME, err);
			return err;
		}

		err = tracepoint_probe_register(wt->timer_tp,
				(void *)local_timer_entry_hook, wt);
		if (err) {
			wult_err("failed to register the '%s' tracepoint probe,"
				 " error %d", TIMER_TRACEPOINT_NAME, err);
			return err;
		}
	} else {
		tracepoint_probe_unregister(wt->msr_tp,
				(void *)write_msr_hook, wt);
		tracepoint_probe_unregister(wt->timer_tp,
				(void *)local_timer_entry_hook, wt);
	}

	return 0;
}

static int init_device(struct wult_device_info *wdi, int cpu)
{
	struct wult_tdt *wt = wdi_to_wt(wdi);

	/* TODO: ensure that hrtimers are backed by the TSC dealine timer. */

	wt->msr_tp = wult_tracer_find_tracepoint(MSR_TRACEPOINT_NAME);
	if (!wt->msr_tp)
		return -EINVAL;

	wt->timer_tp = wult_tracer_find_tracepoint(TIMER_TRACEPOINT_NAME);
	if (!wt->timer_tp)
		return -EINVAL;

	wt->cpu = cpu;
	hrtimer_setup(&wt->timer, &timer_interrupt, CLOCK_MONOTONIC,
		      HRTIMER_MODE_REL_PINNED_HARD);
	return 0;
}

static void exit_device(struct wult_device_info *wdi)
{
	struct wult_tdt *wt = wdi_to_wt(wdi);

	hrtimer_cancel(&wt->timer);
	wt->msr_tp = NULL;
	wt->timer_tp = NULL;
}

static struct wult_device_ops wult_tdt_ops = {
	.get_time_before_idle = get_time_before_idle,
	.get_time_after_idle = get_time_after_idle,
	.get_intr_time = get_intr_time,
	.arm = arm_event,
	.event_has_happened = event_has_happened,
	.get_launch_time = get_launch_time,
	.enable = enable,
	.init = init_device,
	.exit = exit_device,
};

static const struct x86_cpu_id intel_cpu_ids[] = {
	X86_MATCH_VENDOR_FAM_FEATURE(INTEL, 6, X86_FEATURE_TSC_DEADLINE_TIMER, NULL),
	{}
};
MODULE_DEVICE_TABLE(x86cpu, intel_cpu_ids);

static int __init wult_tdt_init(void)
{
	const struct x86_cpu_id *id;

	id = x86_match_cpu(intel_cpu_ids);
	if (!id) {
		wult_err("the CPU does not support TSC deadline timers");
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
