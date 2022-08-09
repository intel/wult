PREFIX ?= /tmp/stc-agent
BINDIR := $(PREFIX)/bin
TOOLNAMES = stc-agent ipmi-helper

all:
	

clean:
	

install:
	mkdir -p $(BINDIR)
	cp stc-agent.standalone $(BINDIR)/stc-agent
	cp ipmi-helper.standalone $(BINDIR)/ipmi-helper

uninstall:
	rm -f $(BINDIR)/stc-agent $(BINDIR)/ipmi-helper
	rmdir --ignore-fail-on-non-empty $(BINDIR)

list_deployables:
	@echo $(TOOLNAMES)
