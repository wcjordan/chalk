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
