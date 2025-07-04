#!make

.ONESHELL:
ACTIVATE_VENV:=. .venv/bin/activate

.PHONY: init
init:
	test -d .venv || python3 -m venv .venv
	$(ACTIVATE_VENV)
	pip install -r dev-requirements.txt

.PHONY: lint
lint:
	$(ACTIVATE_VENV)
	black --check .
	flake8 .
	pylint -j 0 .

.PHONY: format
format:
	$(ACTIVATE_VENV)
	black .

.PHONY: test
test:
	$(ACTIVATE_VENV)
	python -m pytest --cov=. --cov-report=html  -v feature_extraction/tests rrweb_ingest/tests session_stitching/tests
