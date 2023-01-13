PREFIX ?= /tmp/ndl-helper
BINDIR := $(PREFIX)/bin
TOOLNAME = ndl-helper

all: $(TOOLNAME)

%: %.c
	$(CC) $(CFLAGS) $(LDFLAGS) $< -o $@

clean:
	rm -rf $(TOOLNAME)

install:
	mkdir -p $(BINDIR)
	cp $(TOOLNAME) $(BINDIR)

uninstall:
	rm -f $(BINDIR)/$(TOOLNAME)
	rmdir --ignore-fail-on-non-empty $(BINDIR)
