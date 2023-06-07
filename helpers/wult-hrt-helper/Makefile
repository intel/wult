# SPDX-License-Identifier: GPL-2.0
#
# Copyright (C) 2022 Intel Corporation

PREFIX ?= /tmp/wult-hrt-helper
BINDIR := $(PREFIX)/bin
TOOLNAME = wult-hrt-helper

KSRC := /lib/modules/$(shell uname -r)/source
BPFTOOL ?= bpftool
# Path to static 'libbpf.a' library.
LIBBPF ?=
# Paths to include when compiling eBPF code.
BPF_INC := -I$(KSRC)/include \
	   -I$(KSRC)/usr/include \
	   -I$(KSRC)/libbpf/include \
	   -I$(KSRC)/tools/lib
# Paths to include when compiling the userspace code.
U_INC := -I$(KSRC)/tools/include \
	 -I$(KSRC)/tools/lib

BPFOBJS = hrt-bpf.o
UOBJS = wult-hrt-helper.o

CFLAGS ?= -Wall -O2 -Wmissing-prototypes -Wstrict-prototypes -Wformat -Werror=format-security
BPF_CFLAGS ?= -O2 -g -target bpf
LDFLAGS ?=

# If static 'libbpf' library was not provided, use the dynamic one.
ifeq ($(LIBBPF),)
LDFLAGS := $(LDFLAGS) -lbpf
endif

CLANG ?= clang

all: $(TOOLNAME)

# Problem: if "bpftool gen skeleton > file.h" fails, then 'file.h' is created,
# but it is empty. Re-running 'make' in will then assume that the 'file.h' does
# not need to be re-built. The below special target fixes the problem.
.DELETE_ON_ERROR:

$(BPFOBJS): %.o: %.c
	$(CLANG) $(BPF_INC) \
		-D__KERNEL__ -D__BPF_TRACING__ -D__TARGET_ARCH_x86 \
		-Wno-unused-value -Wno-pointer-sign \
		-Wno-compare-distinct-pointer-types \
		-Wno-gnu-variable-sized-type-not-at-end \
		-Wno-address-of-packed-member -Wno-tautological-compare \
		-Wno-unknown-warning-option \
		-fno-asynchronous-unwind-tables \
		-fno-stack-protector \
		$(BPF_CFLAGS) \
		-c $< -o $@
	$(BPFTOOL) gen skeleton $@ > $(subst .o,.h,$@)

$(UOBJS): %.o: %.c
	$(CC) -Wno-unused-variable $(U_INC) -c -o $@ $< $(CFLAGS)

$(TOOLNAME): $(UOBJS)
	$(CC) -o $@ $(UOBJS) $(CFLAGS) $(LIBBPF) $(LDFLAGS)

bpf: $(BPFOBJS)

clean:
	rm -f $(BPFOBJS) $(UOBJS) $(TOOLNAME)

clean-bpf:
	rm -f $(subst .o,.h,$(BPFOBJS))

install:
	mkdir -p $(BINDIR)
	cp $(TOOLNAME) $(BINDIR)

uninstall:
	rm -f $(BINDIR)/$(TOOLNAME)
	rmdir --ignore-fail-on-non-empty $(BINDIR)
