// SPDX-License-Identifier: GPL-2.0
/*
 * Copyright(c) 2022 Intel Corporation.
 * Author: Tero Kristo <tero.kristo@linux.intel.com>
 */

#include <uapi/linux/bpf.h>
#include <uapi/linux/time.h>
#include <uapi/linux/errno.h>
#include <linux/version.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

#include "common.h"

#define dbgmsg(fmt, ...) do { \
	if (debug) \
		bpf_printk("hrt_bpf DBG: " fmt, ##__VA_ARGS__); \
} while (0)

#define errmsg(fmt, ...)  bpf_printk("hrt_bpf ERR: " fmt, ##__VA_ARGS__)

/*
 * Below is hardcoded, as including the corresponding linux header would
 * break BPF object building.
 */
#define PWR_EVENT_EXIT -1

/* Hardcoded BPF_F_TIMER_ABS as we might not have it in the kernel */
#define ABS_TIMER_FLAGS		1

struct {
	__uint(type, BPF_MAP_TYPE_RINGBUF);
	__uint(max_entries, 4096);
} events SEC(".maps");

struct {
	__uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
	__uint(key_size, sizeof(int));
	__uint(value_size, sizeof(u32));
	__uint(max_entries, WULTRUNNER_NUM_PERF_COUNTERS);
} perf SEC(".maps");

struct timer_elem {
	struct bpf_timer t;
};

struct {
	__uint(type, BPF_MAP_TYPE_ARRAY);
	__uint(max_entries, 1);
	__type(key, int);
	__type(value, struct timer_elem);
} timers SEC(".maps");

static int debug;
static int min_t;
static int max_t;
static struct hrt_bpf_event bpf_event;
static u64 ltime;
static u32 ldist;
static bool timer_armed;
static bool capture_timer_id;
static void *timer_id;
static bool has_abs_timer;

static u64 perf_counters[WULTRUNNER_NUM_PERF_COUNTERS];

const u32 linux_version_code = LINUX_VERSION_CODE;

/*
 * These are used as configuration variables passed in by userspace.
 * volatile modifier is needed, as otherwise the compiler assumes these
 * to be constants and does not recognize the changes done by the tool;
 * effectively hardcoding the values as all zeroes in the compiled BPF
 * code.
 */
const volatile u32 cpu_num;

/*
 * Read TSC counter value via the perf subsystem.
 */
static u64 read_tsc(void)
{
	u64 count;
	s64 err;

	count = bpf_perf_event_read(&perf, MSR_TSC);
	err = (s64)count;

	/*
	 * Check if reading TSC has failed for some reason. This is not
	 * a fatal condition and the next read will typically succeed
	 * unless we are executing the read from bad context.
	 */
	if (err >= -512 && err < 0) {
		errmsg("TSC read error: %d", err);
		count = 0;
	}

	return count;
}

/*
 * Send a dummy ping message to userspace process to wake it up.
 */
static void ping_cpu(void)
{
	struct hrt_bpf_event *e;

	e = bpf_ringbuf_reserve(&events, 1, 0);
	if (!e) {
		errmsg("ringbuf overflow, ping discarded");
		return;
	}

	e->type = HRT_EVENT_PING;

	bpf_ringbuf_submit(e, 0);
}

/*
 * Send wakeup event data to userspace. Verifies that the event is
 * not bogus and passes it up.
 */
static void send_event(void)
{
	struct hrt_bpf_event *e;
	int i;

	/*
	 * Check that we have all required data in place, these
	 * may be populated in different order if we are running
	 * an idle state with interrupts enabled/disabled
	 */
	if (!bpf_event.tai || !bpf_event.tintr || !bpf_event.tbi)
		return;

	if (bpf_event.tbi >= bpf_event.ltime ||
	    bpf_event.tintr <= bpf_event.ltime ||
	    bpf_event.tai <= bpf_event.ltime)
		goto cleanup;

	e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
	if (!e) {
		/*
		 * A failure here is not fatal, current event will
		 * be discarded but next one will succeed if userspace
		 * has cleared up the buffer. Just in case, send a
		 * message to userspace about overflow situation.
		 */
		errmsg("ringbuf overflow, event discarded");
		return;
	}

	__builtin_memcpy(e, &bpf_event, sizeof(*e));

	e->type = HRT_EVENT_DATA;

	/* Index 0 is TSC, skip it here */
	for (i = 1; i < WULTRUNNER_NUM_PERF_COUNTERS; i++)
		e->perf_counters[i] = perf_counters[i];

	bpf_ringbuf_submit(e, 0);

cleanup:
	bpf_event.tbi = 0;
	bpf_event.tai = 0;
	bpf_event.tintr = 0;
}

/*
 * Re-arm the timer with new launch distance value.
 */
static int kick_timer(void)
{
	int key = 0;
	struct bpf_timer *timer;
	int ret;
	int cpu_id = bpf_get_smp_processor_id();

	if (bpf_event.tbi || timer_armed)
		return 0;

	timer = bpf_map_lookup_elem(&timers, &key);
	if (!timer)
		/*
		 * This check will never fail, but must be in place to
		 * satisfy BPF verifier.
		 */
		return 0;

	ldist = bpf_get_prandom_u32();
	ldist = ldist % (max_t - min_t);
	ldist = ldist + min_t;

	dbgmsg("kick_timer: ldist=%d, cpu=%d, has-abs=%d", ldist, cpu_id,
	       has_abs_timer);

	if (has_abs_timer) {
		ltime = bpf_ktime_get_boot_ns() + ldist;
		bpf_timer_start(timer, ltime, ABS_TIMER_FLAGS);
	} else {
		bpf_timer_start(timer, ldist, 0);
		ltime = bpf_ktime_get_boot_ns() + ldist;
	}

	timer_armed = true;

	return ret;
}

/*
 * Captures the value of a single perf variable.
 */
static int snapshot_perf_var(int idx, bool exit)
{
	u64 count = bpf_perf_event_read(&perf, idx);
	s64 err;

	err = (s64)count;
	if (err < 0 && err >= -EINVAL)
		return (int)err;

	if (exit)
		perf_counters[idx] = count - perf_counters[idx];
	else
		perf_counters[idx] = count;

	return 0;
}

/*
 * Snapshot performance register values. The links to the specific
 * registers are provided by userspace, and they contain the residency
 * times within specific HW sleep states among other things.
 */
static void snapshot_perf_vars(bool exit)
{
	int i;
	s64 err;

	/* Skip MSR events 0..2 (TSC/APERF/MPERF) */
	for (i = 3; i < WULTRUNNER_NUM_PERF_COUNTERS; i++) {
		err = snapshot_perf_var(i, exit);
		if (err)
			break;
	}
}

/*
 * Timer callback for out own timer. We use this to finalize our
 * captured wakeup event, and to re-arm the timer.
 * Timer callbacks are executed in slightly different BPF context
 * and for example perf_events are not accessible here.
 */
static int timer_callback(void *map, int *key, struct bpf_timer *timer)
{
	struct hrt_bpf_event *e = &bpf_event;
	int cpu_id = bpf_get_smp_processor_id();

	dbgmsg("timer_cb, cpu=%d", cpu_id);

	timer_armed = false;

	if (e->tbi) {
		e->intrts2 = bpf_ktime_get_boot_ns();
		e->ldist = ldist;
		e->ltime = ltime;
		/*
		 * TAI stamp missing means we are executing a POLL
		 * state waiting for a scheduling event to happen.
		 * Send a dummy ping message to userspace so that
		 * cpuidle knows to wake-up also, otherwise we only
		 * end up executing the interrupt handler.
		 */
		if (!e->tai)
			ping_cpu();
	}

	send_event();
	kick_timer();

	return 0;
}

/*
 * Start the hrtimer, called from userspace.
 */
SEC("syscall")
int hrt_bpf_start_timer(struct hrt_bpf_args *args)
{
	int key = 0;
	struct bpf_timer *timer;
	int ret;

	debug = args->debug;
	min_t = args->min_t;
	max_t = args->max_t;

	timer = bpf_map_lookup_elem(&timers, &key);
	if (!timer)
		return -ENOENT;

	capture_timer_id = true;

	bpf_timer_init(timer, &timers, CLOCK_MONOTONIC);

	capture_timer_id = false;

	bpf_timer_set_callback(timer, timer_callback);

	/*
	 * Attempt to start timer with the BPF_F_TIMER_ABS flag set, if it fails,
	 * we don't have support for the absolute timer in the kernel, and must
	 * fallback to relative one.
	 */
	ret = bpf_timer_start(timer, bpf_ktime_get_boot_ns() + 1000000,
			      ABS_TIMER_FLAGS);
	if (ret)
		has_abs_timer = false;
	else
		has_abs_timer = true;

	kick_timer();

	return 0;
}

/*
 * Local timer entry tracepoint. This is the earliest tracepoint we
 * can tap into in the timer subsystem for an expiring timer. Use
 * this to capture the timer interrupt timestamps.
 */
SEC("tp_btf/local_timer_entry")
int BPF_PROG(hrt_bpf_local_timer_entry, int vector)
{
	struct hrt_bpf_event *e = &bpf_event;
	int cpu_id = bpf_get_smp_processor_id();
	u64 t;

	if (cpu_id == cpu_num && !e->tintr) {
		t = bpf_ktime_get_boot_ns();
		if (t >= ltime ) {
			e->tintr = t;
			e->intrts1 = t;
			if (e->tai) {
				snapshot_perf_vars(true);
				snapshot_perf_var(MSR_MPERF, true);
			}
			e->intrc = read_tsc();
			e->intrmperf = bpf_perf_event_read(&perf, MSR_MPERF);
			e->intraperf = bpf_perf_event_read(&perf, MSR_APERF);
		}
	}

	return 0;
}

/*
 * Softirq tracepoint. This is used to capture the number of softirqs
 * executed. If any unexpected softirqs happen during the wakeup event
 * processing, the event is discarded by the userspace to avoid any
 * extra latencies induced by the extra interrupt processing.
 */
SEC("tp_btf/softirq_entry")
int BPF_PROG(hrt_bpf_softirq_entry, int vector)
{
	struct hrt_bpf_event *e = &bpf_event;
	int cpu_id = bpf_get_smp_processor_id();

	if (cpu_id == cpu_num)
		e->swirqc++;

	return 0;
}

/*
 * NMI tracepoint. This is used similarly to the softirq tracepoint
 * to capture the amount of NMIs that have happened during out
 * wakeup event handling, and to filter out any events that are messed
 * up by NMI processing.
 */
SEC("tp_btf/nmi_handler")
int BPF_PROG(hrt_bpf_nmi_handler, void *handler, s64 t, int vector)
{
	struct hrt_bpf_event *e = &bpf_event;
	int cpu_id = bpf_get_smp_processor_id();

	if (cpu_id == cpu_num)
		e->nmic++;

	return 0;
}

/*
 * hrtimer initialization tracepoint. This is used to get the unique
 * ID to our own timer so that we can match it later on.
 */
SEC("tp_btf/hrtimer_init")
int BPF_PROG(hrt_bpf_timer_init, void *timer)
{
	if (capture_timer_id)
		timer_id = timer;

	return 0;
}

/*
 * hrtimer expire tracepoint is used to capture the timer timestamps
 * in case these were missed by the earlier tracepoint (timer queue
 * execution for example.)
 */
SEC("tp_btf/hrtimer_expire_entry")
int BPF_PROG(hrt_bpf_timer_expire_entry, void *timer, void *now)
{
	struct hrt_bpf_event *e = &bpf_event;

	if (timer == timer_id && e->tbi && !e->tintr) {
		e->intrts1 = bpf_ktime_get_boot_ns();
		e->tintr = e->intrts1;
		if (e->tai) {
			snapshot_perf_vars(true);
			snapshot_perf_var(MSR_MPERF, true);
		}
		e->intrc = read_tsc();
		e->intrmperf = bpf_perf_event_read(&perf, MSR_MPERF);
		e->intraperf = bpf_perf_event_read(&perf, MSR_APERF);
	}

	return 0;
}

/*
 * Cpuidle tracepoint. Captures sleep entry/exit timestamps when
 * entering/exiting idle.
 */
SEC("tp_btf/cpu_idle")
int BPF_PROG(hrt_bpf_cpu_idle, unsigned int cstate, unsigned int cpu_id)
{
	struct hrt_bpf_event *e = &bpf_event;
	int idx = cpu_id;
	u64 t;

	if (cpu_id != cpu_num)
		return 0;

	if (cstate == PWR_EVENT_EXIT) {
		t = bpf_ktime_get_boot_ns();

		if (e->tintr || t >= ltime) {
			e->tai = t;
			e->aits1 = e->tai;

			if (e->tintr) {
				snapshot_perf_vars(true);
				snapshot_perf_var(MSR_MPERF, true);
			}
			e->aic = read_tsc();
			e->aits2 = bpf_ktime_get_boot_ns();
			e->aimperf = bpf_perf_event_read(&perf, MSR_MPERF);
			e->aiaperf = bpf_perf_event_read(&perf, MSR_APERF);
		} else {
			e->tbi = 0;
		}

		dbgmsg("exit cpu_idle, state=%d, idle_time=%lu",
		       e->req_cstate, e->tai - e->tbi);

		send_event();
		kick_timer();
	} else {
		dbgmsg("enter cpu_idle, state=%d", cstate);
		e->req_cstate = cstate;
		idx = cstate;

		e->bimonotonic = bpf_ktime_get_boot_ns();
		e->bic = read_tsc();
		snapshot_perf_var(MSR_MPERF, false);
		snapshot_perf_vars(false);

		e->tbi = bpf_ktime_get_boot_ns();
		if (e->tbi > ltime)
			e->tbi = 0;

		e->tai = 0;
		e->nmic = 0;
		/*
		 * We are trying to count only unrelated SW interrupts. Our
		 * timer also introduces one SW interrupt, which we do not want
		 * to count. Hence, initilize to -1.
		 */
		e->swirqc = (u32)-1;
		e->tintr = 0;
	}

	return 0;
}

char _license[] SEC("license") = "GPL";
