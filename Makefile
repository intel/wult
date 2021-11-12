PELICAN?=pelican
PELICANOPTS=

BASEDIR=$(CURDIR)
INPUTDIR=$(BASEDIR)/content
OUTPUTDIR=$(BASEDIR)/output
CONFFILE=$(BASEDIR)/pelicanconf.py
PUBLISHCONF=$(BASEDIR)/publishconf.py

GITHUB_PAGES_BRANCH=gh-pages
WEB_BRANCH=web
SERVER ?= "0.0.0.0"
PORT ?= 8000

DEBUG ?= 0
ifeq ($(DEBUG), 1)
	PELICANOPTS += -D
endif

RELATIVE ?= 0
ifeq ($(RELATIVE), 1)
	PELICANOPTS += --relative-urls
endif

all:
	"$(PELICAN)" "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS)

help:
	@echo 'Makefile for a pelican Web site.'
	@echo ''
	@echo 'Usage:'
	@echo '   make                                     (re)generate the web site'
	@echo '   make clean                               remove the generated files'
	@echo '   make serve [PORT=8000] [SERVER=0.0.0.0]  serve site at 0.0.0.0:8000'
	@echo '   make publishconf                         generate using publishconf.py'
	@echo '   make publish                             publish on github'
	@echo ''
	@echo 'Set the DEBUG variable to 1 to enable debugging, e.g. make DEBUG=1 html '
	@echo 'Set the RELATIVE variable to 1 to enable relative urls'
	@echo 'Set the PORT variable to 1 to specify the port to serve at'
	@echo 'Set the SERVER variable to 1 to specify the IP/HOSTNAME port to serve at'
	@echo ''
clean:
	rm -rf "$(OUTPUTDIR)" "__pycache__"

serve: clean all
	"$(PELICAN)" -l "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" -b $(SERVER) -p "$(PORT)" $(PELICANOPTS)

publishconf:
	"$(PELICAN)" "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(PUBLISHCONF)" $(PELICANOPTS)

publish: publishconf
	ghp-import -m "Re-generate Pelican site" -b $(GITHUB_PAGES_BRANCH) "$(OUTPUTDIR)"
	git push --force origin $(GITHUB_PAGES_BRANCH):$(GITHUB_PAGES_BRANCH)
	git push --force public $(GITHUB_PAGES_BRANCH):$(GITHUB_PAGES_BRANCH)
	git push --force upstream $(GITHUB_PAGES_BRANCH):$(GITHUB_PAGES_BRANCH)
	git push origin $(WEB_BRANCH):$(WEB_BRANCH)
	git push public $(WEB_BRANCH):$(WEB_BRANCH)
	git push upstream $(WEB_BRANCH):$(WEB_BRANCH)

#.PHONY: all html help clean serve publish github
