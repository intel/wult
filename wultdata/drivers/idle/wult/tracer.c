// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2026 Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#include <linux/err.h>
#include <linux/errno.h>
#include <linux/slab.h>
#include <linux/string.h>
#include <linux/tracepoint.h>
#include <linux/trace_events.h>
#include <trace/events/power.h>
#include <asm/cpu_device_id.h>
#include "cstates.h"
#include "tracer.h"
#include "wult.h"

/* Name of the tracepoint we hook to. */
#define TRACEPOINT_NAME "cpu_idle"

/*
 * Name of the wult synthetic event which is used for sending measurement data
 * to user-space.
 */
#define TRACE_EVENT_NAME "wult_cpu_idle"

struct tracepoint_info {
	const char *name;
	struct tracepoint *tp;
};

/* The common, platform-independent wult event fields. */
static struct synth_field_desc common_fields[] = {
	{ .type = "u64", .name = "LDist" },
	{ .type = "u64", .name = "LTime" },
	{ .type = "u64", .name = "TBI" },
	{ .type = "u64", .name = "TBIAdj" },
	{ .type = "u64", .name = "TAI" },
	{ .type = "u64", .name = "TAIAdj" },
	{ .type = "u64", .name = "TIntr" },
	{ .type = "u64", .name = "TIntrAdj" },
	{ .type = "unsigned int", .name = "ReqCState" },
	{ .type = "u64", .name = "AITS1" },
	{ .type = "u64", .name = "AITS2" },
	{ .type = "u64", .name = "IntrTS1" },
	{ .type = "u64", .name = "IntrTS2" },
	{ .type = "u64", .name = "TotCyc" },
	{ .type = "u64", .name = "CC0Cyc" },
	{ .type = "u64", .name = "SMICnt" },
	{ .type = "u64", .name = "NMICnt" },
	{ .type = "u64", .name = "AIAperf" },
	{ .type = "u64", .name = "IntrAperf" },
	{ .type = "u64", .name = "AIMperf" },
	{ .type = "u64", .name = "IntrMperf" },
	{ .type = "u64", .name = "BICyc" },
	{ .type = "u64", .name = "BIMonotonic" },
	{ .type = "u64", .name = "IdleCnt" },
	{ .type = "u64", .name = "PrevTAI" },
	{ .type = "u64", .name = "DropNoIdle" },
	{ .type = "u64", .name = "DropEarlyWake" },
	{ .type = "u64", .name = "DropLateIdle" },
	{ .type = "u64", .name = "DropEarlyIntr" },
};

static inline unsigned int get_smi_count(void)
{
	u32 smicnt = 0;

	if (boot_cpu_data.x86_vendor == X86_VENDOR_INTEL)
		rdmsrq(MSR_SMI_COUNT, smicnt);
	return smicnt;
}

/* Get measurement data before idle. */
static void before_idle(struct wult_info *wi)
{
	struct wult_tracer_info *ti = &wi->ti;

	WARN_ON(!irqs_disabled());
	ti->idle_cnt += 1;
	ti->smi_bi = get_smi_count();
	ti->nmi_bi = get_nmi_count(wi);

	ti->bi_monotonic = ktime_get_ns();
	ti->bi_cyc = rdtsc_ordered();

	/* Make a snapshot of C-state counters. */
	wult_cstates_snap_cst(&ti->csinfo, 0);
	wult_cstates_snap_tsc(&ti->csinfo, 0);
	wult_cstates_snap_mperf(&ti->csinfo, 0);

	ti->tbi = wi->wdi->ops->get_time_before_idle(wi->wdi, &ti->tbi_adj);
}

/* Get measurement data after idle. */
static void after_idle(struct wult_info *wi)
{
	struct wult_tracer_info *ti = &wi->ti;
	struct wult_device_info *wdi = wi->wdi;

	ti->ai_ts1 = ktime_get_ns();

	ti->prev_tai = ti->tai;
	ti->tai = wdi->ops->get_time_after_idle(wdi, &ti->tai_adj);

	/*
	 * Record APERF and MPERF value at after-idle point to
	 * calculate the CPU frequency.
	 */
	ti->ai_aperf = __rdmsr(MSR_IA32_APERF);
	ti->ai_mperf = __rdmsr(MSR_IA32_MPERF);

	if (ti->armed) {
		/* The interrupt handler did not run yet. */
		ti->event_happened = wdi->ops->event_has_happened(wdi);
		if (ti->event_happened) {
			wult_cstates_snap_mperf(&ti->csinfo, 1);
			wult_cstates_snap_tsc(&ti->csinfo, 1);
			ti->armed = false;
		}
	}

	ti->ai_ts2 = ktime_get_ns();
}

/* Get measurements in the interrupt handler after idle. */
void wult_tracer_interrupt(struct wult_info *wi)
{
	struct wult_tracer_info *ti = &wi->ti;
	struct wult_device_info *wdi = wi->wdi;

	ti->intr_ts1 = ktime_get_ns();
	ti->tintr = wdi->ops->get_intr_time(wdi, &ti->tintr_adj);

	/*
	 * Record APERF and MPERF value at in-interrupt point to
	 * calculate the CPU frequency.
	 */
	ti->intr_aperf = __rdmsr(MSR_IA32_APERF);
	ti->intr_mperf = __rdmsr(MSR_IA32_MPERF);

	if (ti->armed) {
		/* 'after_idle()' did not run yet. */
		wult_cstates_snap_mperf(&ti->csinfo, 1);
		wult_cstates_snap_tsc(&ti->csinfo, 1);
		ti->event_happened = wdi->ops->event_has_happened(wdi);
		ti->armed = false;
	}

	ti->intr_ts2 = ktime_get_ns();

	/*
	 * NMI/SMI counters are used for checking if an SMI/NMI happen during
	 * the measurements. Therefore, they have to be read last.
	 */
	ti->smi_intr = get_smi_count();
	ti->nmi_intr = get_nmi_count(wi);
}

static void cpu_idle_hook(void *data, unsigned int req_cstate, unsigned int cpu_id)
{
	struct wult_info *wi = data;
	struct wult_tracer_info *ti = &wi->ti;
	static bool bi_finished = false;

	if (cpu_id != wi->cpu)
		/* Not the CPU we are measuring. */
		return;

	if (req_cstate == PWR_EVENT_EXIT) {
		if (bi_finished)
			after_idle(wi);
		bi_finished = false;
	} else {
		ti->req_cstate = req_cstate;
		if (ti->armed) {
			before_idle(data);
			bi_finished = true;
		}
	}
}

/*
 * Arm an event 'ldist' nanoseconds from now. Returns the actual 'ldist' and
 * absolute launch time value in nanoseconds.
 */
int wult_tracer_arm_event(struct wult_info *wi, u64 *ldist)
{
	int err;
	struct wult_tracer_info *ti = &wi->ti;

	ti->idle_cnt = 0;
	ti->armed = true;
	ti->event_happened = false;
	err = wi->wdi->ops->arm(wi->wdi, ldist);
	if (err) {
		wult_err("failed to arm a delayed event %lluns away, error %d",
			 *ldist, err);
		return err;
	}

	ti->ldist = *ldist;
	return 0;
}

int wult_tracer_send_data(struct wult_info *wi)
{
	struct wult_device_info *wdi = wi->wdi;
	struct wult_tracer_info *ti = &wi->ti;
	struct wult_trace_data_info *tdata = NULL;
	struct synth_event_trace_state trace_state;
	struct cstate_info *csi;
	bool drop_no_idle = false;
	bool drop_early_wake = false;
	bool drop_late_idle = false;
	bool drop_early_intr = false;
	u64 ltime;
	bool idle = ti->idle_cnt;
	int err_after_send = 0;
	int err;

	if (WARN_ON(ti->armed))
		/*
		 * This function must be called only after the armed event has
		 * happened.
		 */
		return -EINVAL;

	if (!ti->event_happened) {
		wult_err("delayed event driver reported that the armed event "
			 "had not happened");
		return -EINVAL;
	}

	ltime = wdi->ops->get_launch_time(wdi);

	/*
	 * Check if the expected IRQ time is within the sleep time. Events that
	 * do not pass the check are sent too, with the reason flagged in the
	 * 'Drop*' fields.
	 */
	if (!idle)
		/* 'tbi' and 'tai' are from a previous event. */
		drop_no_idle = true;
	else if (ltime >= ti->tai)
		drop_early_wake = true;
	else if (ltime <= ti->tbi)
		drop_late_idle = true;
	else if (ltime >= ti->tintr)
		drop_early_intr = true;

	if (idle) {
		if (WARN_ON(ti->csinfo.tsc[0] > ti->csinfo.tsc[1]))
			err_after_send = -EINVAL;

		wult_cstates_snap_cst(&ti->csinfo, 1);
		wult_cstates_calc(&ti->csinfo, 0, 1);
	}

	/*
	 * Note: 'idle' will be 'false' if the event happened, but the CPU did not
	 * enter idle after the event was armed because CPU was running something.
	 * Send the event anyway, with the idle-related fields set to 0.
	 */

	err = synth_event_trace_start(ti->event_file, &trace_state);
	if (err)
		return err;

	/* Add values of the common fields. */
	err = synth_event_add_next_val(ti->ldist, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(ltime, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(idle ? ti->tbi : 0, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(idle ? ti->tbi_adj : 0, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(idle ? ti->tai : 0, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(idle ? ti->tai_adj : 0, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(ti->tintr, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(ti->tintr_adj, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(ti->req_cstate, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(idle ? ti->ai_ts1 : 0, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(idle ? ti->ai_ts2 : 0, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(ti->intr_ts1, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(ti->intr_ts2, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(idle ? ti->csinfo.dtsc : 0, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(idle ? ti->csinfo.dmperf : 0, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(idle ? ti->smi_intr - ti->smi_bi : 0,
				       &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(idle ? ti->nmi_intr - ti->nmi_bi : 0,
				       &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(idle ? ti->ai_aperf : 0, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(ti->intr_aperf, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(idle ? ti->ai_mperf : 0, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(ti->intr_mperf, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(idle ? ti->bi_cyc : 0, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(idle ? ti->bi_monotonic : 0,
				       &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(ti->idle_cnt, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(ti->prev_tai, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(drop_no_idle, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(drop_early_wake, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(drop_late_idle, &trace_state);
	if (err)
		goto out_end;
	err = synth_event_add_next_val(drop_early_intr, &trace_state);
	if (err)
		goto out_end;

	/* Add C-state cycle counter values. */
	for_each_cstate(&ti->csinfo, csi) {
		err = synth_event_add_next_val(idle ? csi->dcyc : 0, &trace_state);
		if (err)
			goto out_end;
	}

	if (wdi->ops->get_trace_data) {
		tdata = wdi->ops->get_trace_data(wdi);
		if (IS_ERR(tdata)) {
			err = PTR_ERR(tdata);
			goto out_end;
		}
		/* Add driver-specific field values. */
		for (; tdata->name; tdata++) {
			err = synth_event_add_next_val(tdata->val, &trace_state);
			if (err)
				goto out_end;
		}
	}

	err = synth_event_trace_end(&trace_state);
	if (!err)
		err = err_after_send;
	return err;

out_end:
	synth_event_trace_end(&trace_state);
	return err;
}

int wult_tracer_enable(struct wult_info *wi)
{
	int err;
	struct wult_tracer_info *ti = &wi->ti;

	ti->event_happened = ti->armed = false;
	err = tracepoint_probe_register(ti->tp, (void *)cpu_idle_hook, wi);
	if (err) {
		wult_err("failed to register the '%s' tracepoint probe, error %d",
			 TRACEPOINT_NAME, err);
		return err;
	}

	err = trace_array_set_clr_event(ti->event_file->tr, "synthetic",
					TRACE_EVENT_NAME, true);
	if (err)
		tracepoint_synchronize_unregister();

	return err;
}

void wult_tracer_disable(struct wult_info *wi)
{
	tracepoint_probe_unregister(wi->ti.tp, (void *)cpu_idle_hook, wi);
	trace_array_set_clr_event(wi->ti.event_file->tr, "synthetic",
				  TRACE_EVENT_NAME, false);
}

static void match_tracepoint(struct tracepoint *tp, void *priv)
{
	struct tracepoint_info *tp_info = priv;

	if (!strcmp(tp->name, tp_info->name))
		tp_info->tp = tp;
}

struct tracepoint *wult_tracer_find_tracepoint(const char *tp_name)
{
	struct tracepoint_info tp_info = {
		.name = tp_name,
		.tp = NULL,
	};

	for_each_kernel_tracepoint(&match_tracepoint, &tp_info);
	if (!tp_info.tp)
		wult_err("failed to find the '%s' tracepoint", tp_info.name);

	return tp_info.tp;
}
EXPORT_SYMBOL_GPL(wult_tracer_find_tracepoint);

static int wult_synth_event_init(struct wult_info *wi)
{
	struct wult_tracer_info *ti = &wi->ti;
	struct wult_trace_data_info *p, *tdata;
	struct cstate_info *csi;
	struct dynevent_cmd cmd;
	char *cmd_buf, name_buf[64];
	int name_len;
	int err;

	cmd_buf = kzalloc(MAX_DYNEVENT_CMD_LEN, GFP_KERNEL);
	if (!cmd_buf)
		return -ENOMEM;

	synth_event_cmd_init(&cmd, cmd_buf, MAX_DYNEVENT_CMD_LEN);

	/* Add the common fields. */
	err = synth_event_gen_cmd_array_start(&cmd, TRACE_EVENT_NAME,
					      THIS_MODULE, common_fields,
					      ARRAY_SIZE(common_fields));
	if (err)
		goto out_free;

	/* Add C-states fields. */
	for_each_cstate(&ti->csinfo, csi) {
		name_len = snprintf(name_buf, sizeof(name_buf), "%sCyc", csi->name);
		if (name_len >= sizeof(name_buf)) {
			err = -EINVAL;
			goto out_free;
		}

		err = synth_event_add_field(&cmd, "u64", name_buf);
		if (err)
			goto out_free;
	}

	/* Add driver-specific fields, if any. */
	if (wi->wdi->ops->get_trace_data) {
		tdata = wi->wdi->ops->get_trace_data(wi->wdi);
		if (IS_ERR(tdata)) {
			err = PTR_ERR(tdata);
			goto out_free;
		}

		for (p = tdata; p->name; p++) {
			err = synth_event_add_field(&cmd, "u64", p->name);
			if (err)
				goto out_free;
		}
	}

	err = synth_event_gen_cmd_end(&cmd);
	if (err)
		goto out_free;

	ti->event_file = trace_get_event_file(NULL, "synthetic",
					      TRACE_EVENT_NAME);
	if (IS_ERR(ti->event_file)) {
		err = PTR_ERR(ti->event_file);
		synth_event_delete(TRACE_EVENT_NAME);
	}

	return err;

out_free:
	kfree(cmd_buf);
	return err;
}

static void wult_synth_event_exit(const struct wult_tracer_info *ti)
{
	trace_put_event_file(ti->event_file);
	synth_event_delete(TRACE_EVENT_NAME);
}

int wult_tracer_init(struct wult_info *wi)
{
	struct wult_tracer_info *ti = &wi->ti;
	int err;

	err = wult_cstates_init(&ti->csinfo);
	if (err)
		return err;

	/* Find the tracepoint to hook to. */
	ti->tp = wult_tracer_find_tracepoint(TRACEPOINT_NAME);
	if (!ti->tp)
		return -EINVAL;

	err = wult_synth_event_init(wi);
	if (err)
		return err;

	return 0;
}

void wult_tracer_exit(struct wult_info *wi)
{
	struct wult_tracer_info *ti = &wi->ti;

	wult_synth_event_exit(ti);
	tracepoint_synchronize_unregister();
}
