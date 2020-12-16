get-image-name = $(firstword $(subst IMAGE=, ,$1))
image-name-split = $(firstword $(subst :, ,$1))

DOCKERIMAGE_FILE=".env"
IMAGE=$(call get-image-name,$(shell cat $(DOCKERIMAGE_FILE)), 1)
NAME := $(call image-name-split,$(shell cat $(IMAGE)), 1)

DOCKERCOMPOSE_DEV=docker-compose.dev.yml

MAKEFLAGS += --no-print-directory

.DEFAULT_GOAL := help

SHELL := /bin/bash

.PHONY: build-image
build-image:		## Just (re)build docker image
	@echo "Building new docker image: $(IMAGE)";
	docker build . -t $(IMAGE);
	@echo "Image built."

.PHONY: stop start-plone
start-plone:docker-compose.yml		## Start plone cluster
	docker-compose up -d
	docker-compose scale plone=4

.PHONY: buildout-plone fix-permissions
buildout-plone:		## Run buildout -c buildout.cfg in container
	docker-compose exec plone buildout -c buildout.cfg

.PHONY: plone_install
plone_install:
	#sudo chown -R 1000 src
	#sudo chown -R `whoami` src/
	docker-compose exec plone gosu plone /docker-initialize.py
	docker-compose exec plone buildout -c develop.cfg
	#docker-compose exec plone gosu plone bin/develop rb

.PHONY: fix-permissions
fix-permissions:
	docker-compose exec plone find /data  -not -user plone -exec chown plone:plone {} \+
	docker-compose exec plone find /plone -not -user plone -exec chown plone:plone {} \+

.PHONY: plone-fg
plone-fg:docker-compose.yml		## Start the plone process in foreground
	docker-compose exec plone gosu plone bin/instance fg

.PHONY: start-plone-dev
start-plone-dev:
	docker-compose -f $(DOCKERCOMPOSE_DEV) up -d

.PHONY: restart-plone-dev
restart-plone-dev:
	docker-compose -f $(DOCKERCOMPOSE_DEV) restart

.PHONY: setup-plone-dev
setup-plone-dev:stop start-plone-dev plone_install fix-permissions restart-plone-dev  		## Setup needed for Plone developing

.PHONY: plone-shell
plone-shell:docker-compose.yml		## Start a shell on the plone service
	docker-compose exec plone gosu plone bash

.PHONY: stop
stop:		## Stop all services
	docker-compose stop

.PHONY: shell
shell:		## Starts a shell with proper env set
	$(SHELL)

.PHONY: help
help:		## Show this help.
	@echo -e "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/\\x1b[36m\1\\x1b[m:\2/' | column -c2 -t -s :)"
