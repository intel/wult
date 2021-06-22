PREFIX ?= /tmp/stats-collect
BINDIR := $(PREFIX)/bin
TOOLNAMES = stats-collect ipmi-helper

all:
	

clean:
	

install:
	mkdir -p $(BINDIR)
	cp stats-collect.standalone $(BINDIR)/stats-collect
	cp ipmi-helper.standalone $(BINDIR)/ipmi-helper

uninstall:
	rm -f $(BINDIR)/stats-collect $(BINDIR)/ipmi-helper
	rmdir --ignore-fail-on-non-empty $(BINDIR)

list_deployables:
	@echo $(TOOLNAMES)
