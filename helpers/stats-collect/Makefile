PREFIX ?= /tmp/stats-collect
BINDIR := $(PREFIX)/bin
PREPARE_STANDALONE = prepare-standalone.sh
TOOLNAMES = stats-collect ipmi-helper

all:
	./prepare-standalone.sh

clean:
	./prepare-standalone.sh clean

install:
	mkdir -p $(BINDIR)
	cp stats-collect.standalone $(BINDIR)/stats-collect
	cp ipmi-helper.standalone $(BINDIR)/ipmi-helper

uninstall:
	rm -f $(BINDIR)/$(TOOLNAME)
	rmdir --ignore-fail-on-non-empty $(BINDIR)

list_deployables:
	@echo $(TOOLNAMES)
