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
#include <signal.h>
#include <time.h>
#include <unistd.h>

#include "wult-tdt-helper.h"
#include "common.h"
#include "tdt-bpf.h"

#define ARRAY_SIZE(x) (sizeof(x) / sizeof((x)[0]))

#define tdt_bpf__attach_prog(s,pname) ({ \
	int __retval = 0; \
        (s)->links.tdt_bpf_ ## pname = \
		bpf_program__attach(s->progs.tdt_bpf_ ## pname); \
	if (!s->links.tdt_bpf_ ## pname) { \
		errmsg("BPF program attach failed for " #pname); \
		__retval = 1; \
	} \
	__retval; \
	})

static char ver_buf[256];
static char *version = ver_buf;

static int verbose;
static int perf_ev_amt;
static int cpu = -1;
static double tsc_to_nsec;

static struct tdt_bpf_args bpf_args = { .min_ldist = 1000, .max_ldist = 4000000 };

static const char *output_vars[] = {
	"LTime",
	"LDist",
	"ReqCState",
	"TBI",
	"TAI",
	"TIntr",
	"IntrTS1",
	"IntrTS2",
	"AITS1",
	"AITS2",
	"AIAperf",
	"IntrAperf",
	"AIMperf",
	"IntrMperf",
	"BICyc",
	"BIMonotonic",
	"TotCyc",
	"NMICnt",
	"SWIRQCnt",
	"SMICnt",
	"CC0Cyc",
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
	[MSR_APERF] = "aperf",
	[MSR_MPERF] = "mperf",
	[MSR_SMI] = "smi",
};

static const int core_indices[CORE_STATE_AMT] = {
	1, 3, 6, 7
};

static const int pkg_indices[PKG_STATE_AMT] = {
	2, 3, 6, 7, 8, 9, 10
};

static struct pmu_cfg pmu_configs[WULT_TDT_HELPER_NUM_PERF_COUNTERS];

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
	case WULT_TDT_HELPER_PERF_EVENT_MSR:
		indices = NULL;
		names = msr_names;
		max = MSR_EVENT_COUNT;
		pattern = "msr";
		break;

	case WULT_TDT_HELPER_PERF_EVENT_CORE:
		indices = core_indices;
		names = NULL;
		max = CORE_STATE_AMT;
		pattern = "cstate_core";
		break;

	case WULT_TDT_HELPER_PERF_EVENT_PKG:
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
		if (perf_ev_amt == WULT_TDT_HELPER_NUM_PERF_COUNTERS) {
			errmsg("out of perf counter storage, increase WULT_TDT_HELPER_NUM_PERF_COUNTERS");
			return -1;
		}

		fclose(file);
	}

	bpf_args.perf_ev_amt = perf_ev_amt;

	return 0;
}

static int parse_perf_events(void)
{
	int err;

	err = _parse_perf_events(WULT_TDT_HELPER_PERF_EVENT_MSR);
	err |= _parse_perf_events(WULT_TDT_HELPER_PERF_EVENT_CORE);
	err |= _parse_perf_events(WULT_TDT_HELPER_PERF_EVENT_PKG);

	return err;
}

static int handle_rb_event(void *ctx, void *bpf_event, size_t sz)
{
	const struct tdt_bpf_event *e = bpf_event;
	int i;
	u64 tai;
	u64 tintr;
	u64 ltime;
	bool dump = false;

	/* Ping just wakes us up, ignore it otherwise */
	if (e->type == TDT_EVENT_PING)
		return 0;

	/* Convert TSC counters to time stamp values */
	tai = e->tbi + (e->aic - e->bic2) / tsc_to_nsec;
	tintr = e->tbi + (e->intrc - e->bic2) / tsc_to_nsec;
	ltime = e->tbi + (e->ltimec - e->bic2) / tsc_to_nsec;

	/*
	 *      l   l  c  t   t   t           a   i   a   i   b   b   t   n  s  s  c
	 *      t   d  s  b   a   i           i   n   i   n   i   i   o   m  w  m  c
	 *      i   i  t  i   i   n           a   t   m   t   c   m   t   i  i  i  0
	 *      m   s  a          t           p   a   p   m   y   o   c   c  r     c
	 *      e   t  t          r           r   p   r   p   c   n   y      q     y
	 *             e                      f   r   f   r       o   c            c
	 */

	printf("%lu,%d,%d,%lu,%lu,%lu,0,0,0,0,%lu,%lu,%lu,%lu,%lu,%lu,%lu,%u,%u,%lu,%lu,",
		ltime, e->ldist, e->req_cstate, e->tbi, tai, tintr,
		e->aiaperf, e->intraperf, e->aimperf, e->intrmperf,
		e->bic, e->tbi2, e->perf_counters[MSR_TSC], e->nmic, e->swirqc,
		e->perf_counters[MSR_SMI], e->perf_counters[MSR_MPERF]);

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

static void print_help(void)
{
	printf("Usage: wult-tdt-helper [options]\n");
	printf("Options:\n");
	printf("  -c, --cpu     CPU number to measure.\n");
	printf("  -l, --ldist   launch distance range in nanoseconds (e.g. 100,200).\n");
	printf("  -P, --print-max-ldist  print the maximum supported launch distance in\n"
	       "                         nanoseconds and exit.\n");
	printf("  -V, --version print version info and exit (both tool version and\n");
	printf("                kernel version against which the tool was built).\n");
	printf("  -v, --verbose  be verbose. Specify two times for increased verbosity.\n");
	printf("  -h, --help    show this help message and exit.\n");
}

static int libbpf_debug_print(enum libbpf_print_level level, const char *format,
			      va_list args)
{
	char buf[BUFSIZ];
	char *cur = buf;
	char *end = buf + BUFSIZ;

	cur += snprintf(buf, BUFSIZ, "wult-tdt-helper: ");

	vsnprintf(cur, end - cur, format, args);
	return fprintf(stderr, "%s", buf);
}

static int parse_options(int argc, char **argv)
{
	struct tdt_bpf *skel;
	int opt;
	u32 ver;
	static const struct option long_options[] = {
		{ "cpu",            required_argument, NULL, 'c' },
		{ "ldist",          required_argument, NULL, 'l' },
		{ "print-max-ldist", no_argument, NULL, 'P' },
		{ "version",        no_argument, NULL, 'V' },
		{ "verbose",        no_argument, NULL, 'v' },
		{ "help",           no_argument, NULL, 'h' },
		{ 0 },
	};

	while ((opt = getopt_long(argc, argv, "c:l:PVv::h", long_options,
				  NULL)) != -1) {
		switch (opt) {
		case 'c':
			cpu = atol(optarg);
			break;
		case 'l':
			if (sscanf(optarg, "%u,%u", &bpf_args.min_ldist, &bpf_args.max_ldist) < 2) {
				errmsg("failed to parse launch distance range '%s'", optarg);
				exit(1);
			}
			if (bpf_args.min_ldist > bpf_args.max_ldist) {
				errmsg("bad launch distance range '%s': min. should not be greater than max.", optarg);
				exit(1);
			}
			if (bpf_args.max_ldist > LDIST_MAX) {
				errmsg("too large max. launch distance '%u', should be smaller than '%u' ns",
				       bpf_args.max_ldist, LDIST_MAX);
				exit(1);
			}
			/* Prevent divide by zero error */
			if (bpf_args.max_ldist == bpf_args.min_ldist)
				bpf_args.max_ldist = bpf_args.min_ldist + 1;
			break;
		case 'P':
			msg("max. ldist: %u", LDIST_MAX);
			exit(0);
		case 'V':
			/*
			 * Print out version info. This will first print
			 * out the program version, followed by the kernel
			 * that the BPF program was built against.
			 * Typically the kernel version should not matter
			 * much but very old kernels may not be compatible.
			 */
			printf("Wult TDT helper v%d.%d\n", VERSION_MAJOR, VERSION_MINOR);
			skel = tdt_bpf__open();
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
		case 'v':
			verbose++;
			bpf_args.debug = 1;
			while (optarg && optarg[0]) {
				if (optarg[0] == 'v') {
					verbose++;
				} else {
					errmsg("bad argument to verbose: %s", optarg);
					exit(1);
				}
				optarg++;
			}
			break;
		default:
			print_help();
			exit(0);
		}
	}

	if (verbose > 2) {
		errmsg("too many '-v' / '--verbose' options, specify it two times at max.");
		exit(1);
	}

	if (verbose == 2)
		libbpf_set_print(libbpf_debug_print);

	return 0;
}

static inline u64 rdtsc(void)
{
	u32 low, high;
	__asm__ __volatile__("rdtscp" : "=a" (low), "=d" (high));
	return ((u64)high << 32) | low;
}

static int calibrate_tsc(int fd)
{
	int i, read_cnt;
	u64 tsc, tsc_perf, tsc1;
	u64 min_diff = 0;
	u64 tsc_cal, tsc_diff;

	if (fd < 0) {
		errmsg("No TSC PMU file detected for calibration.");
		return -1;
	}

	for (i = 0; i < 100; i++) {
		tsc1 = rdtsc();

		read_cnt = read(fd, &tsc_perf, sizeof(u64));
		if (read_cnt == -1) {
			syserrmsg("failed to read TSC counter via perf");
			return -1;
		}

		tsc = rdtsc();

		/* Ignore first few values */
		if (i < 10)
			continue;

		/*
		 * Search for minimum TSC delta; this gives most accurate
		 * result for the calibration value.
		 */
		tsc_diff = tsc - tsc1;

		if (min_diff && min_diff < tsc_diff)
			continue;

		min_diff = tsc_diff;

		bpf_args.timer_calib =
			tsc1 + (tsc - tsc1) / 3 - tsc_perf;
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
	int tsc_fd = -1;
	int perf_map_fd;
	FILE *f;
	struct ring_buffer *event_rb;
	int type;
	char buf[BUFSIZ];
	int cmd;
	struct tdt_bpf *skel;
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

	skel = tdt_bpf__open();
	if (!skel) {
		errmsg("failed to open eBPF skeleton");
		exit(1);
	}

	skel->rodata->cpu_num = cpu;

	verbose("Updated min_ldist to %d", bpf_args.min_ldist);
	verbose("Updated max_ldist to %d", bpf_args.max_ldist);

	err = tdt_bpf__load(skel);
	if (err) {
		errmsg("failed to load and verify BPF skeleton");
		goto cleanup;
	}

	err = tdt_bpf__attach_prog(skel, cpu_idle);
	if (err)
		goto cleanup;

	err = tdt_bpf__attach_prog(skel, write_msr);
	if (err)
		goto cleanup;

	err = tdt_bpf__attach_prog(skel,nmi_handler);
	if (err)
		goto cleanup;

	err = tdt_bpf__attach_prog(skel,softirq_entry);
	if (err)
		goto cleanup;

	err = tdt_bpf__attach_prog(skel, local_timer_entry);
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

		if (i == MSR_TSC)
			tsc_fd = pmu_fd;
	}

	/* Calibrate the TSC value from perf against locally read TSC */
	err = calibrate_tsc(tsc_fd);
	if (err) {
		errmsg("failed to calibrate TSC");
		goto cleanup;
	}

	verbose("TSC calibration value: %lu", bpf_args.timer_calib);

	err = bpf_prog_test_run_opts(
			bpf_program__fd(skel->progs.tdt_bpf_setup),
			&topts);
	if (err) {
		errmsg("failed to execute tdt_bpf_setup: %d", err);
		goto cleanup;
	}

	if (topts.retval != 0) {
		errmsg("tdt_bpf_setup failed, returns %d", topts.retval);
		err = topts.retval;
		goto cleanup;
	}

	tsc_to_nsec = bpf_args.tsc_khz / 1000000.0;

	verbose("TSC rate: %ukHz, tsc_to_nsec=%e", bpf_args.tsc_khz,
		tsc_to_nsec);

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
		case WULT_TDT_HELPER_PERF_EVENT_MSR:
			/* MSR events are used for synthetic purposes only */
			break;
		case WULT_TDT_HELPER_PERF_EVENT_CORE:
			printf("CC%dCyc,", pmu_configs[i].index);
			break;
		case WULT_TDT_HELPER_PERF_EVENT_PKG:
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
	tdt_bpf__destroy(skel);
	return err;
}
