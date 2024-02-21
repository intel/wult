PREFIX ?= /tmp/wult-freq-helper
BINDIR := $(PREFIX)/bin
TOOLNAME = wult-freq-helper

all:

clean:

install:
	mkdir -p $(BINDIR)
	cp $(TOOLNAME).standalone $(BINDIR)/$(TOOLNAME)

uninstall:
	rm -f $(BINDIR)/$(TOOLNAME)
	rmdir --ignore-fail-on-non-empty $(BINDIR)
