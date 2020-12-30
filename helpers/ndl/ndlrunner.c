/*
 * -*- coding: utf-8 -*-
 * vim: ts=8 sw=8 tw=100 noet ai si
 *
 * Copyright (C) 2019-2020 Intel Corporation
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
 */

#include <errno.h>
#include <fcntl.h>
#include <stdlib.h>
#include <stdio.h>
#include <getopt.h>
#include <unistd.h>
#include <ifaddrs.h>
#include <poll.h>
#include <pthread.h>
#include <signal.h>
#include <string.h>
#include <netinet/in.h>
#include <linux/errqueue.h>
#include <linux/net_tstamp.h>
#include <sys/prctl.h>

#define verbose(fmt, ...) do { \
		if (verbose) { \
			printf("ndlrunner: " fmt "\n", ##__VA_ARGS__); \
		} \
	} while (0)
#define msg(fmt, ...) do { \
		printf("ndlrunner: " fmt "\n", ##__VA_ARGS__); \
	} while (0)
#define errmsg(fmt, ...) do { \
		fprintf(stderr, "ndlrunner error: " fmt "\n", ##__VA_ARGS__); \
	} while (0)
#define syserrmsg(fmt, ...) do { \
		fprintf(stderr, "ndlrunner error: " fmt ": %s\n", \
				##__VA_ARGS__, strerror(errno)); \
	} while (0)

#define NANO  1000000000ULL

/* The majic sequence we append to the delayed packet. */
#define MAGIC 0xBADF00DFEE1C001ULL
#define PACKET_SIZE (sizeof(uint64_t) + sizeof(MAGIC))

/*
 * Size of the buffer for reading commands from standard output.
 */
#define CMD_BUF_SIZE 512

/*
 * How many times in a row we allow the RTD register to contain zero. If it is always zero, this
 * indicates that something is misconfigured and we are not measuring anything.
 */
#define ZERO_RTD_LIMIT 10

/*
 * How many times in a row it is OK if arming a delayed packet fails. Sometimes it may happen
 * because, for example, time changed while we were in the middle of arming the packet, or time just
 * drifted too much and our launch distance was very small, so that we ended up trying to arm a
 * packet in the past.
 */
#define ARM_FAIL_LIMIT 4

/*
 * Error queue message buffer size.
 */
#define ERRQUEUE_BUF_SIZE 4096

/* Command codes (command may be sent via the standard input). */
#define CMD_NONE 0
#define CMD_EXIT 1

static const char *ifname;
static unsigned long long dpcnt = 1;
static unsigned long long launch_distance;
static unsigned long long launch_range;
static int port = 0;
static int verbose = 0;
static int loop_forever = 1;

/*
 * A buffer for storring socket error messages that we generally ignore, but may need at some
 * point.
 */
static char errqueue_buf[ERRQUEUE_BUF_SIZE];

/*
 * Create a socket suitable for scheduling packets to be sent in the future.
 */
static int create_send_socket(void)
{
	int sock, tmp;
	struct sockaddr_in addr;
	struct sock_txtime txtime_info;

	memset(&addr, 0, sizeof(addr));
	addr.sin_family = AF_INET;
	addr.sin_addr.s_addr = htonl(INADDR_ANY);
	addr.sin_port = htons(port);

	sock = socket(PF_INET, SOCK_DGRAM, IPPROTO_UDP);
	if (sock < 0) {
		syserrmsg("failed to create socket");
		return -1;
	}
	tmp = 1;
	if (setsockopt(sock, SOL_SOCKET, SO_BROADCAST, &tmp, sizeof(tmp))) {
		syserrmsg("failed to set 'SO_BROADCAST' socket option");
		goto err_close;
	}
	tmp = 3;
	if (setsockopt(sock, SOL_SOCKET, SO_PRIORITY, &tmp, sizeof(tmp))) {
		syserrmsg("failed to set socket priority to %d", tmp);
		goto err_close;
	}
	if (bind(sock, (struct sockaddr *) &addr, sizeof(addr))) {
		syserrmsg("failed to bind the socket");
		goto err_close;
	}
	if (setsockopt(sock, SOL_SOCKET, SO_BINDTODEVICE, ifname, strlen(ifname))) {
		syserrmsg("failed bind to network interface '%s'", ifname);
		goto err_close;
	}

	txtime_info.clockid = CLOCK_TAI;
	txtime_info.flags = SOF_TXTIME_REPORT_ERRORS;
	if (setsockopt(sock, SOL_SOCKET, SO_TXTIME, &txtime_info, sizeof(txtime_info))) {
		syserrmsg("failed to set 'SO_TXTIME' socket option");
		goto err_close;
	}

	if (!port) {
		struct sockaddr_in addr1;

		tmp = sizeof(addr1);
		getsockname(sock, (struct sockaddr *)&addr1, (socklen_t *)&tmp);
		port = ntohs(addr1.sin_port);
		verbose("port number: %d", port);
	}

	return sock;

err_close:
	close(sock);
	return -1;
}

static int handle_socket_errors(int sock, struct sockaddr_in *addr)
{
	unsigned char buf[PACKET_SIZE];
	char msg_control[CMSG_SPACE(sizeof(struct sock_extended_err))];
	struct sock_extended_err *serr;
	struct cmsghdr *cmsg;
	struct msghdr msg;
	struct iovec iov;
	uint64_t ltime;

	iov.iov_base = buf;
	iov.iov_len = sizeof(buf);

	msg.msg_iov = &iov;
	msg.msg_iovlen = 1;
	msg.msg_name = addr;
	msg.msg_namelen = sizeof(*addr);
	msg.msg_control = msg_control;
	msg.msg_controllen = sizeof(msg_control);

	if (recvmsg(sock, &msg, MSG_ERRQUEUE) == -1) {
		syserrmsg("'recvmsg()' on socket error queue failed");
		return -1;
	}

	cmsg = CMSG_FIRSTHDR(&msg);
	serr = (struct sock_extended_err *)CMSG_DATA(cmsg);

	if (serr->ee_origin == SO_EE_ORIGIN_TXTIME) {
		ltime = ((uint64_t)serr->ee_data << 32) + serr->ee_info;
		if (serr->ee_code == SO_EE_CODE_TXTIME_INVALID_PARAM) {
			snprintf(errqueue_buf, ERRQUEUE_BUF_SIZE,
				 "packet with launch time %llu ns was dropped: invalid parameters",
				 (unsigned long long)ltime);
			return EAGAIN;
		}
		if (serr->ee_code ==  SO_EE_CODE_TXTIME_MISSED) {
			snprintf(errqueue_buf, ERRQUEUE_BUF_SIZE,
				"packet with launch time %llu ns was dropped: missed deadline",
				(unsigned long long)ltime);
			return EAGAIN;
		}
	}

	snprintf(errqueue_buf, ERRQUEUE_BUF_SIZE,
		"the delayed packet with lauch time %llu got error %d, origin %u, type %u, code %u",
		(unsigned long long)ltime, serr->ee_errno,
		(unsigned int)serr->ee_origin, (unsigned int)serr->ee_type,
		(unsigned int)serr->ee_code);
	return EAGAIN;
}

/*
 * Get current TAI time, add delta nanoseconds, and return the result as a 64-bit integer
 * (nanoseconds since epoch). Returns 0 on error.
 */
static uint64_t get_tai_time(uint64_t delta)
{
	struct timespec tv;

	if (clock_gettime(CLOCK_TAI, &tv)) {
		syserrmsg("'clock_gettime()' failed");
		return 0;
	}

	return tv.tv_sec * NANO + tv.tv_nsec + delta;
}

/*
 * Get current realtime time and return the result as a 64-bit integer (nanoseconds since epoch).
 * Returns 0 on error.
 */
static uint64_t get_real_time(void)
{
	struct timespec tv;

	if (clock_gettime(CLOCK_REALTIME, &tv)) {
		syserrmsg("'clock_gettime()' failed");
		return 0;
	}

	return tv.tv_sec * NANO + tv.tv_nsec;
}

static uint64_t get_launch_distance(void)
{
	if (launch_range)
		return ((random() % launch_range) + launch_distance) + 1;
	else
		return launch_distance;
}

static int arm(int sock, uint64_t launch_distance)
{
	int err;
	uint64_t packet_buf[2];
	char control[CMSG_SPACE(PACKET_SIZE)];
	struct pollfd pfd;
	struct sockaddr_in addr;
	struct cmsghdr *cmsg;
	struct msghdr msg;
	struct iovec iov;

	packet_buf[0] = get_tai_time(launch_distance);
	if (packet_buf[0] == 0)
		return -1;
	packet_buf[1] = MAGIC;

	memset(&addr, 0, sizeof(addr));
	addr.sin_family = AF_INET;
	addr.sin_addr.s_addr = htonl(INADDR_BROADCAST);
	addr.sin_port = htons(port);

	iov.iov_base = packet_buf;
	iov.iov_len = PACKET_SIZE;

	memset(&msg, 0, sizeof(msg));
	msg.msg_name = &addr;
	msg.msg_namelen = sizeof(addr);
	msg.msg_iov = &iov;
	msg.msg_iovlen = 1;

	memset(control, 0, sizeof(control));
	msg.msg_control = control;
	msg.msg_controllen = sizeof(control);

	cmsg = CMSG_FIRSTHDR(&msg);
	cmsg->cmsg_level = SOL_SOCKET;
	cmsg->cmsg_type = SCM_TXTIME;
	cmsg->cmsg_len = CMSG_LEN(sizeof(uint64_t));
	*((uint64_t *) CMSG_DATA(cmsg)) = packet_buf[0];

	err = sendmsg(sock, &msg, 0);
	if (err != PACKET_SIZE) {
		if (err >= 0)
			syserrmsg("'sendmsg()' returned %d, expected %ld", err, PACKET_SIZE);
		else
			syserrmsg("'sendmsg()' for the delayed packet failed");
		return -1;
	}

	/* Check for errors in socket error queue. */
	pfd.fd = sock;
	if (poll(&pfd, 1, 0) == 1 && pfd.revents & POLLERR)
		return handle_socket_errors(sock, &addr);

	return 0;
}

static unsigned long long strtoll_or_die(const char *str, const char *descr)
{
	char *endptr;
	long long res;

	res = strtoll(str, &endptr, 10);
	if (*endptr != '\0' || endptr == str || res <= 0) {
		errmsg("bad %s value '%s', should be a positive integer", descr, str);
		exit(1);
	}

	return res;
}

/*
 * Print TAI time vs real time offset in seconds. Returns 0 on success and -1 on error.
 */
static int print_tai_offset(void)
{
	uint64_t tai, real;

	/*
	 * Order here is important. If TAI time is taken before real time then the output will round
	 * down and TAI offset will be one second off (smaller).
	 */
	real = get_real_time();
	if (real == 0)
		return -1;

	tai = get_tai_time(0);
	if (tai == 0)
		return -1;

	msg("TAI offset: %llu", (tai - real)/NANO);
}

static void print_help(void)
{
	printf("Usage: ndlrunner [options] ifname\n");
	printf("  ifname - name of the network interface to use\n");
	printf("Options:\n");
	printf("  -l, --ldist - the launch distance in nanoseconds\n");
	printf("  -p, --port - UDP port number to use (default is a random port)\n");
	printf("  -c, --count - number of test iterations. By default runs until stopped by\n");
	printf("		typing 'q'.\n");
	printf("  -T, --tai-offset - print TAI time vs. real time offset in seconds and exit\n");
	printf("  -v, --verbose - be verbose\n");
	printf("  -h, --help - show this help message and exit\n");
	exit(0);
}

static int validate_options(int argc, char * const *argv)
{
	if (!launch_distance) {
		errmsg("please, specify either the launch distance");
		return -1;
	}

	return 0;
}

static int parse_options(int argc, char * const *argv)
{
	int opt, cnt;
	struct option long_opts[] = {
		{"ldist",		required_argument, 0, 'l'},
		{"port",		required_argument, 0, 'p'},
		{"count",		required_argument, 0, 'c'},
		{"tai-offset",		no_argument, 0, 'T'},
		{"verbose",		no_argument, 0, 'v'},
		{"help",		no_argument, 0, 'h'},
		{0, 0, 0, 0 }
	};

	while ((opt = getopt_long(argc, argv, "l:p:c:t:f:Tvh", long_opts, NULL)) != -1) {
		switch (opt) {
			case 'l':
				sscanf(optarg, "%lld,%lld", &launch_distance, &launch_range);
				if (launch_range > launch_distance) {
					launch_range -= launch_distance;
					srandom(time(NULL));
				} else
					launch_range = 0;
				break;
			case 'p':
				if (!port)
					port = strtoll_or_die(optarg, "port number");
				break;
			case 'c':
				dpcnt = strtoll_or_die(optarg, "number of datapoints");
				loop_forever = 0;
				break;
			case 'T':
				print_tai_offset();
				exit(0);
				break;
			case 'v':
				if (!verbose)
					verbose = 1;
				break;
			case 'h':
				print_help();
				exit(0);
				break;
			default:
				errmsg("bad option, use -h for help");
				return -1;
		}
	}

	cnt = argc - optind;
	if (cnt > 2) {
		errmsg("too many arguments");
		return -1;
	}
	if (cnt < 1 && (!ifname)) {
		errmsg("network interface name was not specified");
		return -1;
	}

	ifname = argv[optind];

	return 0;
}

static int read_rtd(uint64_t *rtd)
{
	const char rtdpath[] = "/sys/kernel/debug/ndl/rtd";
	FILE *f = fopen(rtdpath, "r");

	if (!f) {
		syserrmsg("failed to open file %s", rtdpath);
		return -1;
	}
	fscanf(f, "%lu", rtd);
	fclose(f);

	return 0;
}

/*
 * Get the next command for the standard input.
 *
 * Returns a positive command code in case of success and -1 in case of failure.
 */
static int get_command(char *buf, size_t bufsize)
{
	int len;

	len = read(STDIN_FILENO, buf, bufsize-1);
	if (len == -1) {
		if (errno == EAGAIN) {
			return CMD_NONE;
		} else {
			syserrmsg("failed to read command");
			return -1;
		}
	}
	if (len == 0) {
		errmsg("failed to read the command: read 0 bytes");
		return -1;
	}
	if (buf[len - 1] != '\n') {
		errmsg("no newline at the end of input, read '%s'", buf);
		return -1;
	}
	buf[len - 1] = '\0';
	len -= 1;

	if (!strcmp(buf, "q"))
		return CMD_EXIT;

	return CMD_NONE;
}

int main(int argc, char * const *argv)
{
	int zero_rtd_count = 0, arm_fail_count = 0;
	int send_sock, pipes[2], ret = -1;
	uint64_t rtd;
	char *buf;

	ret = parse_options(argc, argv);
	if (ret)
		return -1;

	ret = validate_options(argc, argv);
	if (ret)
		return -1;

	if (setvbuf(stdout, NULL, _IOLBF, 0) || setvbuf(stdin, NULL, _IOLBF, 0)) {
		syserrmsg("failed to set stream buffering mode");
		return -1;
	}

	if (fcntl(STDIN_FILENO, F_SETFL, O_NONBLOCK)) {
		syserrmsg("failed to set O_NONBLOCK for stdin");
		return -1;
	}

	send_sock = create_send_socket();
	if (send_sock < 0)
		return -1;

	buf = malloc(CMD_BUF_SIZE);
	if (!buf) {
		syserrmsg("failed to allocate %d bytes of memory", CMD_BUF_SIZE);
		goto error_out;
	}

	/* Clear read 'RTD' by reading before measure loop */
	ret = read_rtd(&rtd);
	if (ret)
		goto error_out;

	while (dpcnt || loop_forever) {
		struct timespec req = {0, 0};
		uint64_t ldist;

		ret = get_command(buf, CMD_BUF_SIZE);
		if (ret < 0)
			break;
		if (ret == CMD_EXIT) {
			ret = 0;
			break;
		}

		ldist = get_launch_distance();

		ret = arm(send_sock, ldist);
		if (ret < 0)
			break;

		if (ret == EAGAIN) {
			/*
			 * Failed to arm a delayed packet, but re-trying may help. For example, time may
			 * have drifted, or launch distance was too short.
			 */
			arm_fail_count += 1;
			if (arm_fail_count > ARM_FAIL_LIMIT) {
				errmsg("failed to arm a delayed packet for %d times in a row",
				       arm_fail_count);
				errmsg("last attempt was to arm with launch distance %lu, and the error was the following:\n%s",
				       ldist, errqueue_buf);
				ret = -1;
				break;
			}
			continue;
		}
		arm_fail_count = 0;

		req.tv_nsec = ldist*1.1;
		/*
		 * Simply sleeping here until we are sure that NIC has sent the
		 * scheduled packet. Smarter implemention would be to detect
		 * when packet is sent. This was tested by listening outgoing
		 * packets with libpcap. But it doesn't work, because we are
		 * using 'time based packet transmission'. Such packet will go
		 * down to NIC immediately, and HW will delay sending it.
		 * libpcap will detect packet too early, at the time when it is
		 * going down to NIC.
		 */
		nanosleep(&req, NULL);

		ret = read_rtd(&rtd);
		if (ret)
			break;

		if (!rtd) {
			zero_rtd_count += 1;
			if (zero_rtd_count > ZERO_RTD_LIMIT) {
 				/*
				 * If RTD is always zero, then something is misconfigured and we are
				 * not measuring anything.
				 */
				errmsg("'RTD' value zero %d times in a row", zero_rtd_count);
				ret = -1;
				break;
			}
			continue;
		}
		zero_rtd_count = 0;

		msg("datapoint: %lu, %lu", rtd, ldist);
		dpcnt -= 1;
	}

error_out:
	if (buf)
		free(buf);
	close(send_sock);
	return ret;
}
