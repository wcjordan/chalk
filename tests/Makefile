#!make

.ONESHELL:
ACTIVATE_VENV:=. .venv/bin/activate

.PHONY: init
init:
	set -e
	test -d .venv || python3 -m venv .venv
	$(ACTIVATE_VENV)
	pip install -r dev-requirements.txt

.PHONY: lint
lint:
	set -e
	$(ACTIVATE_VENV)
	black --check .
	flake8 .
	pylint -j 0 .

.PHONY: format
format:
	set -e
	$(ACTIVATE_VENV)
	black .

# Run integration tests
# Requires dev env to be running (make start)
# make integration-test TEST_TO_RUN=label_filtering_test.py
TEST_TO_RUN ?= ""
.PHONY: integration-test
integration-test:
	set -e
	$(ACTIVATE_VENV)
	env $$(grep -v '^#' ../.env | xargs) sh -c ' \
		pytest -vv $(TEST_TO_RUN) --server_domain chalk-dev.$$ROOT_DOMAIN'
