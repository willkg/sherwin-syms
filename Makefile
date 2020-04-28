# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Include my.env and export it so variables set in there are available
# in the Makefile.
include my.env
export

# Set these in the environment to override them. This is helpful for
# development if you have file ownership problems because the user in the
# container doesn't match the user on your host.
APP_UID ?= 10001
APP_GID ?= 10001

.PHONY: help
help:
	@echo "Sherwin Syms available rules:"
	@echo ""
	@fgrep -h "##" Makefile | fgrep -v fgrep | sed 's/\(.*\):.*##/\1:/'

my.env:
	@if [ ! -f my.env ]; \
	then \
	echo "Copying my.env.dist to my.env..."; \
	cp my.env.dist my.env; \
	fi

.PHONY: build
build: my.env  ## Build docker image
	docker-compose build --build-arg userid=${APP_UID} --build-arg groupid=${APP_GID} app

.PHONY: run
run: my.env  ## Run app container in development mode
	docker-compose up app

.PHONY: shell
shell: my.env  ## Create a shell in the app image
	docker-compose run app shell

test: my.env  ## Run tests
	docker-compose run app test
