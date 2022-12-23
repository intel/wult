// SPDX-License-Identifier: GPL-2.0-only
/*
 * Copyright (C) 2019-2021 Intel Corporation
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#ifndef _WULT_H_
#define _WULT_H_

#include <linux/atomic.h>
#include <linux/ftrace.h>
#include <linux/math64.h>
#include <linux/mutex.h>
#include <linux/printk.h>
#include <linux/wait.h>
#include "tracer.h"

/* Driver version. */
#define WULT_VERSION "3.1"

/* Wult kernel thread name. */
#define WULT_KTHREAD_NAME "wult_armer"

/* The coarsest supported launch distance granularity, nanoseconds. */
#define WULT_MAX_LDIST_GRANULARITY 100000000

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
	/*
	 * Read time before entering idle state. The returned time is in
	 * driver-specific units, e.g., nanoseconds or CPU cycles count.
	 */
	u64 (*get_time_before_idle)(struct wult_device_info *wdi, u64 *adj);
	/*
	 * Read time after idle. The 'cyc' argument is the CPU cycles count
	 * after the CPU woke up from idle.
	 */
	u64 (*get_time_after_idle)(struct wult_device_info *wdi, u64 *adj);
	/* Arm a delayed event 'ldist' nanoseconds away. */
	int (*arm)(struct wult_device_info *wdi, u64 *ldist);
	/* Checks whether the delayed event has happened. */
	bool (*event_has_happened)(struct wult_device_info *wdi);
	/* Returns the launch time in delayed event driver units. */
	u64 (*get_launch_time)(struct wult_device_info *wdi);
	/* Return trace data for the last measurement. */
	struct wult_trace_data_info *
			(*get_trace_data)(struct wult_device_info *wdi);
	/* Enable/disable the delayed event device. */
	int (*enable)(struct wult_device_info *wdi, bool enable);
	/* Initialize the delayed event device. */
	int (*init)(struct wult_device_info *wdi, int cpunum);
	/* Deinitialize the delayed event device. */
	void (*exit)(struct wult_device_info *wdi);
};

/*
 * Wult delayed event device driver information.
 */
struct wult_device_info {
	/*
	 * The launch distance range supported by the delayed event device in
	 * nanoseconds.
	 */
	u64 ldist_min, ldist_max;
	/* The launch distance resolution, nanoseconds. */
	u32 ldist_gran;
	/* The delayed event device driver operations. */
	const struct wult_device_ops *ops;
	/* Name of the delayed event device. */
	const char *devname;
	/* Wult framework private data. */
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
	/*
	 * Protect 'pdev' and serializes delayed event driver registration and
	 * removal.
	 */
	struct mutex dev_mutex;
	/* Driver's root debugfs directory. */
	struct dentry *dfsroot;
	/* The measured CPU number. */
	unsigned int cpunum;
	/* Whether the measurement is enabled. */
	bool enabled;
	/* Whether the early interrupts feature is enabled. */
	bool early_intr;
	/*
	 * Launch distance range in nanoseconds. We pick a random number from
	 * this range when selecting time for the delayed event.
	 */
	u64 ldist_from, ldist_to;
	/*
	 * Serialises wult measurements enabling and disabling, protects the
	 * following fields of this structure: 'enabled', 'early_intr',
	 * 'ldist_from', 'ldist_to'.
	 */
	struct mutex enable_mutex;
	/* Wult tracer information. */
	struct wult_tracer_info ti;
	/* The armer thread. */
	struct task_struct *armer;
	/* Whether the armer thread initialization is done. */
	bool initialized;
	/* The armer thread initialization error code. */
	int init_err;
	/* The wait queue for the armer thread to wait on. */
	wait_queue_head_t armer_wq;
	/* How many delayed events have been armed. */
	atomic_t events_armed;
	/* How many delayed events happened. */
	atomic_t events_happened;
	/* ID of the CPU that handled the last delayed event. */
	unsigned int event_cpu;
	/*
	 * Used for passing an error code from delayed event driver's interrupt
	 * handler.
	 */
	int irq_err;
};

int wult_register(struct wult_device_info *wdi);
void wult_unregister(void);
void wult_interrupt_start(void);
void wult_interrupt_finish(int err);

/* Only for wult framework use, not for delayed event drivers. */
int wult_enable(void);
void wult_disable(void);

#endif
