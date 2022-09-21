// SPDX-License-Identifier: GPL-2.0
/*
 * Copyright (c) 2022, Intel Corporation
 * Author: Tero Kristo <tero.kristo@linux.intel.com>
 */
/*
 * _GNU_SOURCE below is needed to configure some system includes, otherwise
 * things like CPU_SET / CPU_ZERO / sched_setaffinity() are not going to be
 * available at all causing compiler error.
 */
#define _GNU_SOURCE
#include <bpf/bpf.h>
#include <getopt.h>
#include <errno.h>
#include <fcntl.h>
#include <linux/perf_event.h>
#include <sched.h>
#include <stdio.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

#include "wultrunner.h"
#include "bpf-hrt.h"

#define ARRAY_SIZE(x) (sizeof(x) / sizeof((x)[0]))

#define bpf_hrt__attach_prog(s,pname) ({ \
	int __retval = 0; \
        (s)->links.bpf_hrt_ ## pname = \
		bpf_program__attach(s->progs.bpf_hrt_ ## pname); \
	if (!s->links.bpf_hrt_ ## pname) { \
		errmsg("BPF program attach failed for " #pname); \
		__retval = 1; \
	} \
	__retval; \
	})

static char ver_buf[256];
static char *version = ver_buf;

static bool verbose;
static int perf_ev_amt;
static int cpu = -1;

static struct bpf_hrt_args bpf_args = { .min_t = 1000, .max_t = 4000000 };

static const char *output_vars[] = {
	"LTime",
	"LDist",
	"ReqCState",
	"TBI",
	"TAI",
	"TIntr",
	"AITS1",
	"AITS2",
	"IntrTS1",
	"IntrTS2",
	"TotCyc",
	"SMICnt",
	"CC0Cyc",
};

enum {
	CMD_NONE,
	CMD_EXIT
};

enum {
	WULTRUNNER_PERF_EVENT_MSR,
	WULTRUNNER_PERF_EVENT_CORE,
	WULTRUNNER_PERF_EVENT_PKG,
};

struct pmu_cfg {
	struct perf_event_attr attr;
	int type;
	int index;
};

#define CORE_STATE_AMT 4
#define PKG_STATE_AMT 7

static const char *msr_names[MSR_EVENT_COUNT] = {
	[MSR_TSC] = "tsc",
	[MSR_MPERF] = "mperf",
	[MSR_SMI] = "smi",
};

static const int core_indices[CORE_STATE_AMT] = {
	1, 3, 6, 7
};

static const int pkg_indices[PKG_STATE_AMT] = {
	2, 3, 6, 7, 8, 9, 10
};

static struct pmu_cfg pmu_configs[WULTRUNNER_NUM_PERF_COUNTERS];

static int _parse_perf_events(int type)
{
	const int *indices;
	const char **names;
	int max;
	int i;
	char fname[BUFSIZ];
	const char *pattern;
	FILE *file;
	char buf[BUFSIZ];
	struct perf_event_attr attr;
	int cfg;
	struct pmu_cfg *pmu_config = &pmu_configs[perf_ev_amt];
	int pmu_type;

	switch (type) {
	case WULTRUNNER_PERF_EVENT_MSR:
		indices = NULL;
		names = msr_names;
		max = MSR_EVENT_COUNT;
		pattern = "msr";
		break;

	case WULTRUNNER_PERF_EVENT_CORE:
		indices = core_indices;
		names = NULL;
		max = CORE_STATE_AMT;
		pattern = "cstate_core";
		break;

	case WULTRUNNER_PERF_EVENT_PKG:
		indices = pkg_indices;
		names = NULL;
		max = PKG_STATE_AMT;
		pattern = "cstate_pkg";
		break;

	default:
		errmsg("bad perf event type: %d", type);
		return -1;
	}

	snprintf(fname, BUFSIZ, "/sys/bus/event_source/devices/%s/type",
		 pattern);
	file = fopen(fname, "r");
	if (!file) {
		syswarnmsg("unable to find perf event_source %s. Please use custom events/driver",
			   pattern);
		return 0;
	}

	if (!fgets(buf, BUFSIZ, file)) {
		syswarnmsg("failed to read %s", fname);
		return 0;
	}

	pmu_type = atol(buf);

	verbose("PMU type for %s: %d", pattern, pmu_type);

	for (i = 0; i < max; i++) {
		if (indices)
			snprintf(fname, BUFSIZ, "/sys/bus/event_source/devices/%s/events/c%d-residency",
				 pattern, indices[i]);
		else if(names)
			snprintf(fname, BUFSIZ, "/sys/bus/event_source/devices/%s/events/%s",
				 pattern, names[i]);

		verbose("Reading %s", fname);

		file = fopen(fname, "r");
		if (!file)
			continue;

		if (!fgets(buf, BUFSIZ, file)) {
			syswarnmsg("failed to read %s", fname);
			continue;
		}

		if (sscanf(buf, "event=0x%x", &cfg) < 1) {
			syswarnmsg("failed to parse event: '%s'", buf);
			continue;
		}

		memset(&attr, 0, sizeof(attr));

		attr.type = pmu_type;
		attr.config = cfg;

		pmu_config->type = type;
		if (indices)
			pmu_config->index = indices[i];

		memcpy(&pmu_config->attr, &attr, sizeof(attr));

		verbose("Created PMU config[%d]: type=%d, cfg=%lld, index=%lld",
			perf_ev_amt, pmu_type, attr.config, attr.config);

		pmu_config++;
		perf_ev_amt++;
		if (perf_ev_amt == WULTRUNNER_NUM_PERF_COUNTERS) {
			errmsg("out of perf counter storage, increase WULTRUNNER_NUM_PERF_COUNTERS");
			return -1;
		}

		fclose(file);
	}

	return 0;
}

static int parse_perf_events(void)
{
	int err;

	err = _parse_perf_events(WULTRUNNER_PERF_EVENT_MSR);
	err |= _parse_perf_events(WULTRUNNER_PERF_EVENT_CORE);
	err |= _parse_perf_events(WULTRUNNER_PERF_EVENT_PKG);

	return err;
}

static void print_help(void)
{
	printf("Usage: wultrunner [options]\n");
	printf("Options:\n");
	printf("  -c, --cpu     CPU number to measure.\n");
	printf("  -l, --ldist   launch distance range in nanoseconds (e.g. 100,200).\n");
	printf("  -d, --debug   enable debug.\n");
	printf("  -v, --version print version info and exit (both tool version and\n");
	printf("                kernel version against which the tool was built).\n");
	printf("  -h, --help    show this help message and exit.\n");
}

static int handle_rb_event(void *ctx, void *bpf_event, size_t sz)
{
	const struct bpf_hrt_event *e = bpf_event;
	int i;
	u64 totcyc;

	/* Ping just wakes us up, do nothing. */
	if (e->type == HRT_EVENT_PING)
		return 0;

	/* Calculate total cycles */
	if (e->aic > e->intrc)
		totcyc = e->aic - e->bic;
	else
		totcyc = e->intrc - e->bic;

	printf("%lu,%d,%d,%lu,%lu,%lu,%lu,%lu,%lu,%lu,%lu,%lu,%lu,",
		e->ltime, e->ldist, e->req_cstate, e->tbi, e->tai,
		e->tintr, e->aits1, e->aits2, e->intrts1, e->intrts2,
		totcyc, e->perf_counters[MSR_SMI],
		e->perf_counters[MSR_MPERF]);

	/*
	 * Print out perf events, index 0..n are generic MSR events and
	 * are only used by the BPF program itself, so don't print these
	 * out here.
	 */
	for (i = MSR_EVENT_COUNT; i < perf_ev_amt; i++)
		printf("%ld,", e->perf_counters[i]);

	printf("\n");

	return 0;
}

static int get_command(char *buf, size_t bufsize)
{
	int len;

	len = read(STDIN_FILENO, buf, bufsize - 1);
	if (len == -1) {
		if (errno == EAGAIN) {
			return CMD_NONE;
		} else {
			errmsg("failed to read command");
			return -1;
		}
	}

	if (len == 0) {
		errmsg("failed to read command: read 0 bytes");
		return -1;
	}

	if (buf[len - 1] != '\n') {
		errmsg("no newline at the end of input, read '%s'", buf);
		return -1;
	}

	buf[len - 1] = 0;
	len -= -1;

	if (!strcmp(buf, "q"))
		return CMD_EXIT;

	return CMD_NONE;
}

static int parse_options(int argc, char **argv)
{
	static const struct option long_options[] = {
		{ "help", no_argument, NULL, 'h' },
		{ "cpu", required_argument, NULL, 'c' },
		{ "debug", no_argument, NULL, 'd' },
		{ "ldist", required_argument, NULL, 'l' },
		{ "version", no_argument, NULL, 'v' },
		{ 0 },
	};
	struct bpf_hrt *skel;
	int opt;
	u32 ver;

	while ((opt = getopt_long(argc, argv, "hdc:l:v", long_options,
				  NULL)) != -1) {
		switch (opt) {
		case 'c':
			cpu = atol(optarg);
			break;
		case 'd':
			verbose = true;
			break;
		case 'l':
			if (sscanf(optarg, "%d,%d", &bpf_args.min_t, &bpf_args.max_t) < 2) {
				errmsg("failed to parse ldist range: %s", optarg);
				exit(1);
			}
			break;
		case 'v':
			/*
			 * Print out version info. This will first print
			 * out the program version, followed by the kernel
			 * that the BPF program was built against.
			 * Typically the kernel version should not matter
			 * much but very old kernels may not be compatible.
			 */
			printf("Wultrunner v%d.%d\n", VERSION_MAJOR, VERSION_MINOR);
			skel = bpf_hrt__open();
			if (!skel) {
				errmsg("failed to open eBPF skeleton");
				exit(1);
			}
			ver = skel->rodata->linux_version_code;

			printf("eBPF built against linux kernel %d.%d.%d\n",
			       (ver >> 16) & 0xff,
			       (ver >> 8) & 0xff,
			       ver & 0xff);
			exit(0);
			break;
		default:
			print_help();
			exit(0);
		}
	}

	return 0;
}

int main(int argc, char **argv)
{
	int err = 0;
	cpu_set_t cpuset;
	int i;
	int count;
	u32 value;
	int fd;
	int pmu_fd;
	int perf_map_fd;
	FILE *f;
	struct ring_buffer *event_rb;
	int type;
	char buf[BUFSIZ];
	int cmd;
	struct bpf_hrt *skel;
	LIBBPF_OPTS(bpf_test_run_opts, topts,
			.ctx_in = &bpf_args,
			.ctx_size_in = sizeof(bpf_args),
	);

	err = parse_options(argc, argv);
	if (err)
		return err;

	if (cpu < 0) {
		errmsg("no CPU defined");
		exit(1);
	}

	CPU_ZERO(&cpuset);
	CPU_SET(cpu, &cpuset);
	err = sched_setaffinity(0, sizeof(cpuset), &cpuset);
	if (err) {
		errmsg("failed to set CPU affinity to %d, err=%d", cpu, err);
		exit(err);
	}

	/* Check available perf counters */
	parse_perf_events();

	skel = bpf_hrt__open();
	if (!skel) {
		errmsg("failed to open eBPF skeleton");
		exit(1);
	}

	skel->rodata->cpu_num = cpu;

	verbose("Updated min_t to %d", bpf_args.min_t);
	verbose("Updated max_t to %d", bpf_args.max_t);

	err = bpf_hrt__load(skel);
	if (err) {
		errmsg("failed to load and verify BPF skeleton");
		goto cleanup;
	}

	err = bpf_hrt__attach_prog(skel, cpu_idle);
	if (err)
		goto cleanup;

	err = bpf_hrt__attach_prog(skel, timer_init);
	if (err)
		goto cleanup;

	err = bpf_hrt__attach_prog(skel, timer_expire_entry);
	if (err)
		goto cleanup;

	err = perf_map_fd = bpf_map__fd(skel->maps.perf);
	if (err < 0) {
		errmsg("unable to find 'perf' map");
		goto cleanup;
	}

	/* Open perf events */
	for (i = 0; i < perf_ev_amt; i++) {
		pmu_fd = syscall(__NR_perf_event_open, &pmu_configs[i].attr,
				 -1/*pid*/, cpu, -1/*group_fd*/, 0);
		if (pmu_fd < 0) {
			errmsg("failed to open perf_event %d:%lld",
			       pmu_configs[i].type, pmu_configs[i].attr.config);
			exit(1);
		}

		bpf_map_update_elem(perf_map_fd, &i, &pmu_fd, BPF_ANY);

		err = ioctl(pmu_fd, PERF_EVENT_IOC_ENABLE, 0);
		if (err) {
			errmsg("failed to enable perf event %d:%lld",
			       pmu_configs[i].type, pmu_configs[i].attr.config);
			exit(1);
		}
	}

	err = bpf_prog_test_run_opts(
			bpf_program__fd(skel->progs.bpf_hrt_start_timer),
			&topts);
	if (err) {
		errmsg("failed to execute start_timer: %d", err);
		goto cleanup;
	}

	if (topts.retval != 0) {
		errmsg("start_timer failed, returns %d", topts.retval);
		err = topts.retval;
		goto cleanup;
	}

	/* Poll events from the eBPF program */
	err = bpf_map__fd(skel->maps.events);
	if (err < 0) {
		errmsg("Can't get 'events' shared mem from object - %m");
		goto cleanup;
	}

	fd = err;

	event_rb = ring_buffer__new(fd, handle_rb_event, NULL, NULL);
	if (!event_rb) {
		errmsg("failed to create event ringbuf");
		err = 1;
		goto cleanup;
	}

	for (i = 0; i < ARRAY_SIZE(output_vars); i++)
		printf("%s,", output_vars[i]);

	for (i = 0; i < perf_ev_amt; i++) {
		type = pmu_configs[i].type;

		switch (type) {
		case WULTRUNNER_PERF_EVENT_MSR:
			/* MSR events are used for synthetic purposes only */
			break;
		case WULTRUNNER_PERF_EVENT_CORE:
			printf("CC%dCyc,", pmu_configs[i].index);
			break;
		case WULTRUNNER_PERF_EVENT_PKG:
			printf("PC%dCyc,", pmu_configs[i].index);
			break;
		}
	}

	printf("\n");

	if (setvbuf(stdout, NULL, _IOLBF, 0) || setvbuf(stdin, NULL, _IOLBF, 0)) {
		errmsg("failed to set stream buffering mode");
		err = -1;
		goto cleanup;
	}

	if (fcntl(STDIN_FILENO, F_SETFL, O_NONBLOCK)) {
		errmsg("failed to set O_NONBLOCK for stdin");
		err = -1;
		goto cleanup;
	}

	while (1) {
		/*
		 * Following function is called ring_buffer__poll but it is
		 * asynchronous actually waiting for an event to happen before
		 * doing anything.
		 */
		err = ring_buffer__poll(event_rb, -1);
		if (err < 0)
			errmsg("ring_buffer__poll: error=%d", err);
		cmd = get_command(buf, BUFSIZ);
		if (cmd == CMD_EXIT) {
			err = 0;
			break;
		}
	}

cleanup:
	bpf_hrt__destroy(skel);
	return err;
}
