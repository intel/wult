// SPDX-License-Identifier: GPL-2.0
/*
 * Copyright(c) 2022 Intel Corporation.
 * Author: Tero Kristo <tero.kristo@linux.intel.com>
 */

#include "vmlinux.h"
#include <linux/version.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

#include "common.h"

#define dbgmsg(fmt, ...) do { \
	if (debug) \
		bpf_printk("tdt_bpf DBG: " fmt, ##__VA_ARGS__); \
} while (0)

#define errmsg(fmt, ...)  bpf_printk("tdt_bpf ERR: " fmt, ##__VA_ARGS__)

/*
 * Below is hardcoded, as including the corresponding linux header would
 * break BPF object building.
 */
#define PWR_EVENT_EXIT -1

#define MSR_IA32_TSC_DEADLINE		0x6e0

#define CLOCK_MONOTONIC			1

#define ENOENT				2
#define EINVAL				22

extern const void tsc_khz __ksym;

struct {
	__uint(type, BPF_MAP_TYPE_RINGBUF);
	__uint(max_entries, 16384);
} events SEC(".maps");

struct {
	__uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
	__uint(key_size, sizeof(int));
	__uint(value_size, sizeof(u32));
	__uint(max_entries, WULT_TDT_HELPER_NUM_PERF_COUNTERS);
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
static int min_ldist;
static int max_ldist;
static struct tdt_bpf_event bpf_event;
static u64 ltimec;
static u32 ldist;
static bool timer_armed;
static bool restart_timer;
static int perf_ev_amt;

static bool reading_tsc;
static int tsc_event_count;
static bool tsc_event_captured;
static struct perf_event *tsc_event;

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

	/*
	 * Read the relative value of TSC via perf. We don't really care
	 * about the returned value except for error checking, instead
	 * we read the raw TSC value later by directly accessing the
	 * kernel data structure via bpf_core_read().
	 */
	reading_tsc = true;
	tsc_event_count = 0;
	err = bpf_perf_event_read(&perf, MSR_TSC);
	reading_tsc = false;

	/*
	 * If TSC event hasn't been captured yet, check if we captured it now.
	 * This requires that the event_count is one and one only.
	 * If it is still not captured, we don't know the raw TSC value,
	 * so we just bail out returning 0.
	 */
	if (!tsc_event_captured) {
		if (tsc_event_count == 1) {
			tsc_event_captured = true;
			dbgmsg("Captured TSC event %p", tsc_event);
		} else
			return 0;
	}

	/*
	 * Check if reading TSC has failed for some reason. This is not
	 * a fatal condition and the next read will typically succeed
	 * unless we are executing the read from bad context.
	 */
	if (err >= -512 && err < 0) {
		errmsg("TSC read error: %d", err);
		count = 0;
	} else {
		/*
		 * Read the raw performance counter value from the saved
		 * perf_event as it has just been updated by the above
		 * call to the bpf_perf_event_read().
		 */
		bpf_core_read(&count, sizeof(u64), &tsc_event->hw.prev_count);
	}

	return count;
}

static void warn_overflow(const char *type)
{
	u64 t;
	static u32 count;
	static u64 last_warn;

	count++;

	t = bpf_ktime_get_boot_ns();

	if (t > last_warn + 1000000000) {
		errmsg("ringbuf overflow, %s discarded (total %u)",
		       type, count);
		last_warn = t;
	}
}

/*
 * Cleanup stale wakeup event data from local event cache.
 */
static void cleanup_event(void)
{
	struct tdt_bpf_event *e = &bpf_event;

	e->bic = 0;
	e->bic2 = 0;
	e->aic = 0;
	e->aic2 = 0;
	e->intrc = 0;
	e->intrc2 = 0;
	e->tbi = 0;
	e->ltimec = 0;
}

/*
 * Send a dummy ping message to userspace process to wake it up.
 * Sending the message will add the data to the ringbuffer and touch
 * the waitqueue waking up any processes that are waiting on it.
 * This is needed for certain C-states (e.g. POLL), where interrupts
 * are enabled during idle, but where the interrupt itself is not enough
 * to wake-up the system fully.
 */
static void ping_cpu(void)
{
	struct tdt_bpf_event *e;

	/*
	 * Check if we have data in ringbuffer already; if yes, it means
	 * that userspace is already processing data and is not waiting
	 * on the waitqueue, and sending any new data is not going to be
	 * able to wake it up. Therefore, drop the datapoint if the
	 * previous one has not been handled yet.
	 */
	if (bpf_ringbuf_query(&events, BPF_RB_AVAIL_DATA)) {
		warn_overflow("ping");
		cleanup_event();
		return;
	}

	e = bpf_ringbuf_reserve(&events, 1, 0);
	if (!e)
		return;

	e->type = TDT_EVENT_PING;

	bpf_ringbuf_submit(e, 0);
}

/*
 * Send wakeup event data to userspace. Verifies that the event is
 * not bogus and passes it up.
 */
static void send_event(void)
{
	struct tdt_bpf_event *e;
	int i;

	if (timer_armed)
		return;

	/*
	 * Check that we have all required data in place, these
	 * may be populated in different order if we are running
	 * an idle state with interrupts enabled/disabled
	 */
	if (!bpf_event.aic2 || !bpf_event.intrc2 || !bpf_event.bic)
		return;

	if (bpf_event.bic >= bpf_event.ltimec ||
	    bpf_event.intrc <= bpf_event.ltimec ||
	    bpf_event.aic <= bpf_event.ltimec)
		goto cleanup;

	e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
	if (!e) {
		/*
		 * A failure here is not fatal, current event will
		 * be discarded but next one will succeed if userspace
		 * has cleared up the buffer. Just in case, send a
		 * message to userspace about overflow situation.
		 */
		warn_overflow("event");
		goto cleanup;
	}

	__builtin_memcpy(e, &bpf_event, sizeof(*e));

	e->type = TDT_EVENT_DATA;

	bpf_ringbuf_submit(e, 0);

cleanup:
	cleanup_event();
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

	if (cpu_id != cpu_num)
		return 0;

	timer = bpf_map_lookup_elem(&timers, &key);
	if (!timer)
		/*
		 * This check will never fail, but must be in place to
		 * satisfy BPF verifier.
		 */
		return 0;

	ldist = bpf_get_prandom_u32();
	ldist = ldist % (max_ldist - min_ldist);
	ldist = ldist + min_ldist;

	dbgmsg("kick_timer: ldist=%d, cpu=%d", ldist, cpu_id);

	timer_armed = true;

	bpf_timer_start(timer, ldist, 0);

	return ret;
}

/*
 * Captures the value of a single perf variable.
 */
static int snapshot_perf_var(int idx, bool exit)
{
	u64 count = bpf_perf_event_read(&perf, idx);
	s64 err;
	struct tdt_bpf_event *e = &bpf_event;

	err = (s64)count;
	if (err < 0 && err >= -EINVAL)
		return (int)err;

	if (exit)
		e->perf_counters[idx] = count - e->perf_counters[idx];
	else
		e->perf_counters[idx] = count;

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

	/* Skip MSR events 0..2 (TSC/MPERF/APERF) */
	for (i = MSR_APERF + 1; i < perf_ev_amt && i < WULT_TDT_HELPER_NUM_PERF_COUNTERS; i++) {
		err = snapshot_perf_var(i, exit);

		if (err)
			break;
	}
}

/*
 * Timer callback for our own timer. We use this to finalize our
 * captured wakeup event, and to re-arm the timer.
 * Timer callbacks are executed in slightly different BPF context
 * and for example perf_events are not accessible here.
 */
static int timer_callback(void *map, int *key, struct bpf_timer *timer)
{
	struct tdt_bpf_event *e = &bpf_event;
	int cpu_id = bpf_get_smp_processor_id();

	dbgmsg("timer_cb, cpu=%d", cpu_id);

	timer_armed = false;

	/*
	 * Check if we happen to execute the timer callback on wrong CPU.
	 * In this case, the timer IRQ timestamps are either completely
	 * missing, or wrong. Either case, we need to restart the timer
	 * on the correct CPU.
	 */
	if (cpu_id != cpu_num) {
		restart_timer = true;
		return 0;
	}

	send_event();
	kick_timer();

	return 0;
}

/*
 * Setup the eBPF program. This captures the TSC frequency from kernel
 * and passes it back to userspace, and initializes and starts our timer.
 */
SEC("syscall")
int tdt_bpf_setup(struct tdt_bpf_args *args)
{
	int key = 0;
	struct bpf_timer *timer;
	u32 freq;

	if (args->perf_ev_amt > WULT_TDT_HELPER_NUM_PERF_COUNTERS)
		return -EINVAL;

	perf_ev_amt = args->perf_ev_amt;

	bpf_core_read(&freq, sizeof(freq), &tsc_khz);

	args->tsc_khz = freq;
	debug = args->debug;
	min_ldist = args->min_ldist;
	max_ldist = args->max_ldist;

	timer = bpf_map_lookup_elem(&timers, &key);
	if (!timer)
		return -ENOENT;

	bpf_timer_init(timer, &timers, CLOCK_MONOTONIC);

	bpf_timer_set_callback(timer, timer_callback);

	kick_timer();

	return 0;
}

/*
 * Local timer entry tracepoint. This is the earliest tracepoint we
 * can tap into in the timer subsystem for an expiring timer. Use
 * this to capture the timer interrupt timestamps.
 */
SEC("tp_btf/local_timer_entry")
int BPF_PROG(tdt_bpf_local_timer_entry, int vector)
{
	struct tdt_bpf_event *e = &bpf_event;
	int cpu_id = bpf_get_smp_processor_id();
	u64 t;
	u64 c;

	if (cpu_id != cpu_num)
		return 0;

	c = read_tsc();

	if (e->bic && timer_armed) {
		e->intrc = c;
		e->ldist = ldist;
		e->ltimec = ltimec;

		if (e->aic) {
			snapshot_perf_vars(true);
			snapshot_perf_var(MSR_MPERF, true);
			snapshot_perf_var(MSR_TSC, true);
		}

		e->intrc2 = read_tsc();
		e->intrmperf = bpf_perf_event_read(&perf, MSR_MPERF);
		e->intraperf = bpf_perf_event_read(&perf, MSR_APERF);

		/*
		 * AIC stamp missing means we are executing a POLL
		 * state waiting for a scheduling event to happen.
		 * Send a dummy ping message to userspace so that
		 * cpuidle knows to wake-up also, otherwise we only
		 * end up executing the interrupt handler.
		 */
		if (!e->aic)
			ping_cpu();
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
int BPF_PROG(tdt_bpf_softirq_entry, int vector)
{
	struct tdt_bpf_event *e = &bpf_event;
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
int BPF_PROG(tdt_bpf_nmi_handler, void *handler, s64 t, int vector)
{
	struct tdt_bpf_event *e = &bpf_event;
	int cpu_id = bpf_get_smp_processor_id();

	if (cpu_id == cpu_num)
		e->nmic++;

	return 0;
}

/*
 * Capture handle to the TSC perf_event. This handle is used later to
 * directly read the raw TSC value from kernel data structure whenever
 * needed. Only needs to effectively execute once during the startup
 * of the program as the pointer will not change after that.
 */
SEC("kprobe/msr_event_update")
int BPF_KPROBE(tdt_bpf_msr_event_update_entry, struct perf_event *event)
{
	if (reading_tsc && !tsc_event_captured) {
		tsc_event = event;
		tsc_event_count++;
	}

	return 0;
}

/*
 * Write MSR tracepoint. This captures any MSR writes to the system,
 * and specifically this is used to capture the next HW timer programming,
 * so that we know the cycle accurate time of the next timer expire.
 */
SEC("tp_btf/write_msr")
int BPF_PROG(tdt_bpf_write_msr, unsigned int msr, u64 val)
{
	int cpu_id = bpf_get_smp_processor_id();

	if (cpu_id == cpu_num && msr == MSR_IA32_TSC_DEADLINE)
		ltimec = val;

	return 0;
}

/*
 * Check if TSC perf event has been captured yet or not. Returns true
 * if it has been captured, false otherwise.
 */
SEC("syscall")
int tdt_bpf_tsc_event_captured(void *args)
{
	return tsc_event_captured;
}

/*
 * Cpuidle tracepoint. Captures sleep entry/exit timestamps when
 * entering/exiting idle.
 */
SEC("tp_btf/cpu_idle")
int BPF_PROG(tdt_bpf_cpu_idle, unsigned int cstate, unsigned int cpu_id)
{
	struct tdt_bpf_event *e = &bpf_event;
	int idx = cpu_id;
	u64 t;
	u64 c;

	if (cpu_id != cpu_num)
		return 0;

	c = read_tsc();

	/* Flush any pending events at this state */
	if (restart_timer) {
		cleanup_event();
		kick_timer();
		restart_timer = false;
	}

	if (cstate == PWR_EVENT_EXIT) {
		if (e->aic)
			return 0;

		e->aic = c;

		if (e->intrc) {
			snapshot_perf_vars(true);
			snapshot_perf_var(MSR_MPERF, true);
			snapshot_perf_var(MSR_TSC, true);
		}

		e->aic2 = read_tsc();
		e->aimperf = bpf_perf_event_read(&perf, MSR_MPERF);
		e->aiaperf = bpf_perf_event_read(&perf, MSR_APERF);

		dbgmsg("exit cpu_idle, state=%d, idle_cyc=%lu",
		       e->req_cstate, e->aic - e->bic);

		send_event();
		kick_timer();
	} else {
		if (!timer_armed)
			return 0;

		dbgmsg("enter cpu_idle, state=%d", cstate);

		cleanup_event();

		e->req_cstate = cstate;
		idx = cstate;

		e->bic = c;
		e->tbi2 = bpf_ktime_get_boot_ns();

		snapshot_perf_var(MSR_TSC, false);
		snapshot_perf_var(MSR_MPERF, false);
		snapshot_perf_vars(false);

		e->tbi = bpf_ktime_get_boot_ns();
		e->bic2 = read_tsc();

		if (e->bic2 >= ltimec) {
			e->bic2 = 0;
			e->bic = 0;
			e->tbi = 0;
		}

		e->nmic = 0;
		e->swirqc = (u32)-1;
	}

	return 0;
}

char _license[] SEC("license") = "GPL";
