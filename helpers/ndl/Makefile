PREFIX ?= /tmp/ndl
BINDIR := $(PREFIX)/bin
CC ?= $(CROSS_COMPILE)gcc
TOOLNAME = ndlrunner

all: $(TOOLNAME)

%: %.c
	$(CC) $(CFLAGS) -fstack-protector -lpthread $< -o $@

clean:
	rm -rf $(TOOLNAME)

install:
	mkdir -p $(BINDIR)
	cp $(TOOLNAME) $(BINDIR)

uninstall:
	rm -f $(BINDIR)/$(TOOLNAME)
	rmdir --ignore-fail-on-non-empty $(BINDIR)

list_deployables:
	@echo $(TOOLNAME)
