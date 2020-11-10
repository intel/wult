// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2020, Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#ifndef _WULT_H_
#define _WULT_H_

#include <linux/atomic.h>
#include <linux/clocksource.h>
#include <linux/ftrace.h>
#include <linux/math64.h>
#include <linux/printk.h>
#include <linux/spinlock.h>
#include <linux/wait.h>
#include "tracer.h"

/* Driver version. */
#define WULT_VERSION "3.1"

/* Wult kernel thread name. */
#define WULT_KTHREAD_NAME "wult_armer"

/* The coarsest supported launch distance resolution, nanoseconds. */
//#define WULT_MAX_RESOLUTION 1000
#define WULT_MAX_RESOLUTION 100000000

/* Longest time interval allowed to be converted with 'wult_cyc2ns(). */
#define WULT_CYC2NS_MAXSEC 2
#define WULT_CYC2NS_MAXNSEC (WULT_CYC2NS_MAXSEC * NSEC_PER_SEC)

#ifndef DRIVER_NAME
#define DRIVER_NAME "wult"
#endif

/* Normal messages. */
#define wult_msg(fmt, ...) \
	pr_notice(DRIVER_NAME ": " fmt "\n", ##__VA_ARGS__)
/* Error messages. */
#define wult_err(fmt, ...) \
	pr_err(DRIVER_NAME " error: " fmt "\n", ##__VA_ARGS__)
/* Debug messages. */
#define wult_dbg(fmt, ...) \
	pr_debug(DRIVER_NAME ": " fmt "\n", ##__VA_ARGS__)

/*
 * Wult delayed event device can include some of its data into the trace. This
 * structure describes a single piece of such data.
 */
struct wult_trace_data_info {
	const char *name;
	u64 val;
};

struct wult_device_info;

/*
 * Wult operations the delayed event device driver has to provide.
 *
 * Note, wult will call these operations only on the measured CPU.
 */
struct wult_device_ops {
	/* Read time after idle in nanoseconds. */
	u64 (*get_time_after_idle)(struct wult_device_info *wdi);
	/* Read time before idle in nanoseconds. */
	u64 (*get_time_before_idle)(struct wult_device_info *wdi);
	/* Arm a delayed timer 'ldist' nanoseconds away. */
	int (*arm)(struct wult_device_info *wdi, u64 *ldist);
	/* Checks whether the delayed event has happened. */
	bool (*event_has_happened)(struct wult_device_info *wdi);
	/* Returns the launch time in nanoseconds. */
	u64 (*get_launch_time)(struct wult_device_info *wdi);
	/* Return trace data for the last measurement. */
	struct wult_trace_data_info *
			(*get_trace_data)(struct wult_device_info *wdi);
	/* Initialize the delayed event device. */
	int (*init)(struct wult_device_info *wdi, int cpunum);
	/* Deinitialize the delayed event device. */
	void (*exit)(struct wult_device_info *wdi);
};

/*
 * Wult delayed event device driver information.
 */
struct wult_device_info {
	/* Whether the device was initialized. */
	bool initialized;
	/* The initialization error code. */
	int init_err;
	/*
	 * The launch distance range supported by the delayed event device in
	 * nanoseconds.
	 */
	u64 ldist_min, ldist_max;
	/* The launch distance resolution, nanoseconds. */
	u32 ldist_gran;
	/* Whether device provides time in cycles or nanoseconds. */
	bool unit_is_ns;
	/* The delayed event device driver operations. */
	const struct wult_device_ops *ops;
	/* Name of the delayed event device. */
	const char *devname;
	/* Wult framework private data. */
	/*
	 * The multiplier ('mult') and divisor ('shift') values which are used
	 * for fast CPU cycles to nanoseconds conversion.
	 */
	u32 mult, shift;
	void *priv;
};

struct dentry;
struct task_struct;

/*
 * This data structure represents this driver and the wake latency functionality
 * it provides.
 */
struct wult_info {
	/* Wult delayed event device driver information. */
	struct wult_device_info *wdi;
	/* Driver's root debugfs directory. */
	struct dentry *dfsroot;
	/* The measured CPU number. */
	unsigned int cpunum;
	/*
	 * Launch distance range in nanoseconds. We pick a random number from
	 * this range when selecting time for the delayed event.
	 */
	atomic64_t ldist_from, ldist_to;
	/*
	 * Serialises wult measurements enabling and disabling, protects the
	 * the 'enabled' field of this structure.
	 */
	spinlock_t enable_lock;
	/* Whether the measurement is enabled. */
	bool enabled;
	/* Wult tracer information. */
	struct wult_tracer_info ti;
	/* The armer thread. */
	struct task_struct *armer;
	/* The wait queue for the armer thread to wait on. */
	wait_queue_head_t armer_wq;
	/* How many delayed events have been armed. */
	atomic_t events_armed;
	/* How many delayed events happened. */
	atomic_t events_happened;
	/* ID of the CPU that handled the last delayed event. */
	unsigned int event_cpu;
};

int wult_register(struct wult_device_info *wdi);
void wult_unregister(void);
void wult_interrupt(void);

/*
 * Convert cycles to nanoseconds. Should be used only for time intervals within
 * wdi->ldist_max.
 */
static inline u64 wult_cyc2ns(struct wult_device_info *wdi, u64 cyc)
{
	u64 ns;

	ns = mul_u64_u32_shr(cyc, wdi->mult, wdi->shift);
	WARN_ON(ns > WULT_CYC2NS_MAXNSEC);
	return ns;
}

/* Only for wult framework use, not for delayed event drivers. */
int wult_enable_nolock(void);
void wult_disable(void);
void wult_disable_nolock(void);
bool wult_is_enabled(void);

#endif
