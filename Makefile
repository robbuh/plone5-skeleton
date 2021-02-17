get-image-name = $(firstword $(subst IMAGE=, ,$1))
image-name-split = $(firstword $(subst :, ,$1))

DOCKERIMAGE_FILE = ".env"
IMAGE = $(call get-image-name,$(shell cat $(DOCKERIMAGE_FILE)), 1)
NAME = $(call image-name-split,$(IMAGE), 1)

DOCKERCOMPOSE_DEV = docker-compose.dev.yml

MAKEFLAGS += --no-print-directory

.DEFAULT_GOAL := help

SHELL := /bin/bash

.PHONY: build
build:		## Just (re)build docker image
	@echo "Building new docker image: $(IMAGE)";
	docker build . -t $(IMAGE);
	@echo "Image built."

.PHONY: build-no-cache
build-no-cache:		## Just (re)build docker image with --no-cache option
	@echo "Building new docker image: $(IMAGE) ";
	docker build --no-cache . -t $(IMAGE);
	@echo "Image built."

.PHONY: push
push:		## Push image in repo. Image name is in .env file
	docker push $(IMAGE)
	docker tag $(IMAGE) $(NAME):latest
	docker push $(NAME):latest

.PHONY: pull
pull:		## Pull image from repo. Image name is in .env file
	docker pull $(IMAGE)

.PHONY: plone-start
plone-start: stop plone-start		## Start Plone cluster
	docker-compose up -d
	docker-compose scale plone=4

.PHONY: buildout
buildout:
	docker-compose exec plone buildout -c buildout.cfg

.PHONY: plone-buildout
plone-buildout:	stop plone-start buildout fix-permissions restart	## Run buildout and start Plone cluster

.PHONY: plone_install
plone_install: 
	#sudo chown -R 1000 src
	#sudo chown -R `whoami` src/
	docker-compose exec plone gosu plone /docker-initialize.py
	docker-compose exec plone buildout -c develop.cfg
	#docker-compose exec plone bin/develop rebuild

.PHONY: fix-permissions
fix-permissions:
	docker-compose exec plone find /data  -not -user plone -exec chown plone:plone {} \+
	docker-compose exec plone find /plone -not -user plone -exec chown plone:plone {} \+

.PHONY: plone-fg
plone-fg:		## Start Plone process in foreground mode
	docker-compose exec plone gosu plone bin/instance fg

.PHONY: plone-start-dev
plone-start-dev:
	docker-compose -f $(DOCKERCOMPOSE_DEV) up -d

.PHONY: plone-restart-dev
plone-restart-dev:
	docker-compose -f $(DOCKERCOMPOSE_DEV) restart

.PHONY: plone-dev
plone-dev:stop plone-start-dev plone_install fix-permissions plone-restart-dev  		## Setup needed for Plone develop

.PHONY: plone-shell
plone-shell:		## Start a shell on Plone service as plone user
	docker-compose exec plone gosu plone bash

.PHONY: sudo-shell
sudo-shell:	## Start a shell on Plone service as sudo
	docker-compose exec plone bash

.PHONY: stop
stop:		## Stop all services
	docker-compose stop

.PHONY: start
start:		## Start all services
	docker-compose start

.PHONY: restart
restart:		## Restart all services
	docker-compose restart

.PHONY: shell
shell:		## Start a shell with proper env set
	$(SHELL)

.PHONY: help
help:		## Show this help
	@echo -e "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/\\x1b[36m\1\\x1b[m:\2/' | column -c2 -t -s :)"
