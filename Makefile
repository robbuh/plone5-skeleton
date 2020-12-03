MAKEFLAGS += --no-print-directory

.DEFAULT_GOAL := help

SHELL := /bin/bash

.PHONY: rebuild-plone
build-plone:		## Run buildout -c buildout.cfg in container
	docker-compose exec plone buildout -c buildout.cfg

.PHONY: start-plone
start-plone:docker-compose.yml		## Start plone cluster
	docker-compose stop haproxy
	docker-compose stop plone
	docker-compose up -d
	docker-compose scale plone=4

.PHONY: start-plone-fg
start-plone-fg:docker-compose.yml		## Start the plone process in foreground
	docker-compose stop plone
	docker-compose up -d
	docker-compose exec plone gosu plone /docker-initialize.py || true
	docker-compose exec plone gosu plone bin/instance fg

.PHONY: plone_install
plone_install:data
	mkdir -p src
	sudo chown -R 500 src
	docker-compose up -d
	docker-compose exec plone gosu plone bin/develop rb
	docker-compose exec plone gosu plone /docker-initialize.py
	sudo chown -R `whoami` src/

.PHONY: setup-plone-dev
setup-plone-dev:plone_install 		## Setup needed for Plone developing

.PHONY: plone-shell
plone-shell:docker-compose.yml		## Start a shell on the plone service
	docker-compose up -d
	docker-compose exec plone gosu plone /docker-initialize.py || true
	docker-compose exec plone bash

.PHONY: stop
stop:		## Stop all services
	docker-compose stop

.PHONY: shell
shell:		## Starts a shell with proper env set
	$(SHELL)

.PHONY: help
help:		## Show this help.
	@echo -e "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/\\x1b[36m\1\\x1b[m:\2/' | column -c2 -t -s :)"
