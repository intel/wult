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

#ifdef DEBUG
#define debug_printk(fmt, ...) bpf_printk("bpf_hrt DBG: " fmt, ##__VA_ARGS__)
#else
#define debug_printk(fmt, ...) do { } while (0)
#endif

#define warn_printk(fmt, ...) bpf_printk("bpf_hrt WRN: " fmt, ##__VA_ARGS__)

/*
 * Below is hardcoded, as including the corresponding linux header would
 * break BPF object building.
 */
#define PWR_EVENT_EXIT -1

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

static int min_t;
static int max_t;
static struct bpf_hrt_event bpf_event;
static u64 ltime;
static u32 ldist;
static bool timer_armed;
static bool capture_timer_id;
static void *timer_id;

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

static u64 bpf_hrt_read_tsc(void)
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
		warn_printk("TSC read error: %d", err);
		count = 0;
	}

	return count;
}

static void bpf_hrt_ping_cpu(void)
{
	struct bpf_hrt_event *e;

	e = bpf_ringbuf_reserve(&events, 1, 0);
	if (!e) {
		warn_printk("ringbuf overflow, ping discarded");
		return;
	}

	e->type = HRT_EVENT_PING;

	bpf_ringbuf_submit(e, 0);
}

static void bpf_hrt_send_event(void)
{
	struct bpf_hrt_event *e;
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
		warn_printk("ringbuf overflow, event discarded");
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

int bpf_hrt_kick_timer(void)
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

	debug_printk("kick_timer: ldist=%d, cpu=%d", ldist, cpu_id);

	bpf_timer_start(timer, ldist, 0);

	ltime = bpf_ktime_get_boot_ns() + ldist;

	timer_armed = true;

	return ret;
}

static void bpf_hrt_snapshot_perf_vars(bool exit)
{
	int i;
	u64 count, *ptr;
	int key;
	s64 err;

	if (exit)
		perf_counters[MSR_MPERF] =
			bpf_perf_event_read(&perf, MSR_MPERF) -
			perf_counters[MSR_MPERF];

	/* Skip TSC events 0..1 (TSC/MPERF) */
	for (i = 2; i < WULTRUNNER_NUM_PERF_COUNTERS; i++) {
		count = bpf_perf_event_read(&perf, i);
		err = (s64)count;

		/* Exit if no entry found */
		if (err < 0 && err >= -EINVAL)
			break;

		if (exit)
			perf_counters[i] = count - perf_counters[i];
		else
			perf_counters[i] = count;
	}

	if (!exit)
		perf_counters[MSR_MPERF] =
			bpf_perf_event_read(&perf, MSR_MPERF);
}

static int bpf_hrt_timer_cb(void *map, int *key, struct bpf_timer *timer)
{
	struct bpf_hrt_event *e = &bpf_event;
	int cpu_id = bpf_get_smp_processor_id();

	debug_printk("timer_cb, cpu=%d", cpu_id);

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
			bpf_hrt_ping_cpu();
	}

	bpf_hrt_send_event();
	bpf_hrt_kick_timer();

	return 0;
}

SEC("syscall")
int bpf_hrt_start_timer(struct bpf_hrt_args *args)
{
	int key = 0;
	struct bpf_timer *timer;

	min_t = args->min_t;
	max_t = args->max_t;

	timer = bpf_map_lookup_elem(&timers, &key);
	if (!timer)
		return -ENOENT;

	capture_timer_id = true;

	bpf_timer_init(timer, &timers, CLOCK_MONOTONIC);

	capture_timer_id = false;

	bpf_timer_set_callback(timer, bpf_hrt_timer_cb);

	bpf_hrt_kick_timer();

	return 0;
}

SEC("tp_btf/hrtimer_init")
int BPF_PROG(bpf_hrt_timer_init, void *timer)
{
	if (capture_timer_id)
		timer_id = timer;

	return 0;
}

SEC("tp_btf/hrtimer_expire_entry")
int BPF_PROG(bpf_hrt_timer_expire_entry, void *timer, void *now)
{
	struct bpf_hrt_event *e = &bpf_event;

	if (timer == timer_id && e->tbi) {
		e->intrts1 = bpf_ktime_get_boot_ns();
		e->tintr = e->intrts1;
		if (e->tai)
			bpf_hrt_snapshot_perf_vars(true);
		e->intrc = bpf_hrt_read_tsc();
	}

	return 0;
}

SEC("tp_btf/cpu_idle")
int BPF_PROG(bpf_hrt_cpu_idle, unsigned int cstate, unsigned int cpu_id)
{
	struct bpf_hrt_event *e = &bpf_event;
	int idx = cpu_id;
	u64 t;

	if (cpu_id != cpu_num)
		return 0;

	if (cstate == PWR_EVENT_EXIT) {
		t = bpf_ktime_get_boot_ns();

		if (e->tintr || t >= ltime) {
			e->tai = t;
			e->aits1 = e->tai;

			if (e->tintr)
				bpf_hrt_snapshot_perf_vars(true);

			e->aic = bpf_hrt_read_tsc();
			e->aits2 = bpf_ktime_get_boot_ns();
		} else {
			e->tbi = 0;
		}

		debug_printk("exit cpu_idle, state=%d, idle_time=%lu",
			     e->req_cstate, e->tai - e->tbi);

		bpf_hrt_send_event();
		bpf_hrt_kick_timer();
	} else {
		debug_printk("enter cpu_idle, state=%d", cstate);
		e->req_cstate = cstate;
		idx = cstate;

		t = bpf_ktime_get_boot_ns();

		e->bic = bpf_hrt_read_tsc();
		bpf_hrt_snapshot_perf_vars(false);

		e->tbi = bpf_ktime_get_boot_ns();
		if (e->tbi > ltime)
			e->tbi = 0;

		e->tai = 0;
	}

	return 0;
}

char _license[] SEC("license") = "GPL";
