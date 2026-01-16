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

.PHONY: test
test:
	set -e
	$(ACTIVATE_VENV)
# 	python -m pytest --cov=. --cov-report=html -v */tests
	python -m pytest --cov=. --cov-report=html -v rrweb_ingest/tests
	python -m pytest --cov=. --cov-report=html -v rrweb_util/dom_state/tests
	python -m pytest --cov=. --cov-report=html -v rrweb_util/user_interaction/tests

.PHONY: update-snapshots
update-snapshots:
	set -e
	$(ACTIVATE_VENV)
# 	python -m pytest --snapshot-update */tests
	python -m pytest --snapshot-update rrweb_ingest/tests
	python -m pytest --snapshot-update rrweb_util/dom_state/tests

