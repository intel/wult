/* SPDX-License-Identifier: GPL-2.0 */
/*
 * Copyright(c) 2022 Intel Corporation.
 * Author: Tero Kristo <tero.kristo@linux.intel.com>
 */

#ifndef __WULTRUNNER_H__
#define __WULTRUNNER_H__

typedef uint8_t u8;
typedef uint64_t u64;
typedef uint32_t u32;

#define VERSION_MAJOR	0
#define VERSION_MINOR	1

#define verbose(fmt, ...) do { \
		if (verbose) { \
			printf("wultrunner: debug: " fmt "\n", ##__VA_ARGS__); \
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

/* Maximum supported launch distance in nanoseconds. */
#define LDIST_MAX 50000000U

enum {
	CMD_NONE,
	CMD_EXIT
};

enum {
	WULTRUNNER_PERF_EVENT_MSR,
	WULTRUNNER_PERF_EVENT_CORE,
	WULTRUNNER_PERF_EVENT_PKG,
};

/*
 * 'DECLARE_LIBBPF_OPTS' was renamed to 'LIBBPF_OPTS' in kernel version 5.18.
 */
#ifndef LIBBPF_OPTS
#define LIBBPF_OPTS DECLARE_LIBBPF_OPTS
#endif

#endif /* __WULTRUNNER_H__ */
