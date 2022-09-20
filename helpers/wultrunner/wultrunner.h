/* SPDX-License-Identifier: GPL-2.0 */
/*
 * Copyright(c) 2022 Intel Corporation.
 * Author: Tero Kristo <tero.kristo@linux.intel.com>
 */

#ifndef WULTRUNNER_H_
#define WULTRUNNER_H_

typedef uint8_t u8;
typedef uint64_t u64;
typedef uint32_t u32;

#define VERSION_MAJOR	0
#define VERSION_MINOR	1

#define verbose(fmt, ...) do { \
		if (verbose) { \
			printf("wultrunner: " fmt "\n", ##__VA_ARGS__); \
		} \
	} while (0)
#define msg(fmt, ...) do { \
		printf("wultrunner: " fmt "\n", ##__VA_ARGS__); \
	} while (0)

#define warnmsg(fmt, ...) do { \
		fprintf(stderr, "wultrunner warning: " fmt "\n", ##__VA_ARGS__); \
	} while (0)
#define syswarnmsg(fmt, ...) do { \
		fprintf(stderr, "wultrunner warning: " fmt ": %s\n", ##__VA_ARGS__, strerror(errno)); \
	} while (0)
#define errmsg(fmt, ...) do { \
		fprintf(stderr, "wultrunner error: " fmt "\n", ##__VA_ARGS__); \
	} while (0)
#define syserrmsg(fmt, ...) do { \
		fprintf(stderr, "wultrunner error: " fmt ": %s\n", ##__VA_ARGS__, strerror(errno)); \
	} while (0)

#define WULTRUNNER_NUM_PERF_COUNTERS 16

enum {
	MSR_TSC,
	MSR_MPERF,
	MSR_SMI,
	MSR_EVENT_COUNT
};

enum {
	HRT_EVENT_DATA,
	HRT_EVENT_PING,
};

/**
 * bpf_event - info about bpf events
 * @type: type of event
 * @ldist: launch distance (in ns)
 * @ltime: launch time (ktime_ns time)
 * @tbi: time before idle (ns)
 * @tai: time after idle (ns)
 * @tintr: time for interrupt execution start
 * @bic: cycles before idle
 * @aic: cycles after idle
 * @intrc: cycles at interrupt handler
 * @aits1: time after idle #1
 * @aits2: time after idle #2
 * @intrts1: time at hrtimer interrupt #1
 * @intrts2: time at hrtimer interrupt #2
 * @req_cstate: requested cstate
 * @perf_counters: contents of requested perf counters
 */
struct bpf_event {
	u8 type;
	u32 ldist;
	u64 ltime;
	u64 tbi;
	u64 tai;
	u64 tintr;
	u64 bic;
	u64 aic;
	u64 intrc;
	u64 aits1;
	u64 aits2;
	u64 intrts1;
	u64 intrts2;
	int req_cstate;
	u64 perf_counters[WULTRUNNER_NUM_PERF_COUNTERS];
};

struct bpf_args {
	u32 min_t;
	u32 max_t;
};

/*
 * 'DECLARE_LIBBPF_OPTS' was renamed to 'LIBBPF_OPTS' in kernel version 5.18.
 */
#ifndef LIBBPF_OPTS
#define LIBBPF_OPTS DECLARE_LIBBPF_OPTS
#endif

#endif /* WULTRUNNER_H_ */
