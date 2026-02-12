#!make
ifneq (,$(wildcard .env))
    include .env
else ifneq (,$(wildcard ../.env))
    include ../.env
else
    # When running within a container, we don't want to leak any credentials by including a .env file
    # and we don't need the GCP_PROJECT
    GCP_PROJECT = SKIPPED_INCLUDING_PROJECT
endif

IMAGE_REPO = us-east4-docker.pkg.dev/$(GCP_PROJECT)/default-gar
SERVER_IMAGE = $(IMAGE_REPO)/chalk-server

PARENT_DIR = $(dir $(PWD))

# Test w/ PyTest & lint Django app
.PHONY: test
test:
	flake8 .
	PYTHONPATH=$(PWD) pylint -j 0 --load-plugins pylint_django chalk

	# Unit tests
	DJANGO_SETTINGS_MODULE=chalk.settings.testing python manage.py test chalk.todos

# Yapf formatting
.PHONY: format
format:
	docker run --rm -v $(PWD)/server:/usr/src/app $(SERVER_IMAGE):local-latest yapf -ri .
	echo "Server formatting complete.  Please review changes and commit."

# Make migrations for server
.PHONY: create-migrations
create-migrations:
	DJANGO_SETTINGS_MODULE=chalk.settings.testing DOMAIN=localhost docker run --rm -t \
		--env-file ../.env \
		--env DJANGO_SETTINGS_MODULE \
		--env DOMAIN \
		-v $(PWD):/usr/src/app \
		$(SERVER_IMAGE):local-latest \
		python manage.py makemigrations --verbosity 3

# Update starter data for server
.PHONY: update-starter-data
update-starter-data:
	exit 1
	# TODO (jordan) old version below.  Need a k8s compatible version
	# echo "Rerun if failed w/ could not connect to server: Connection refused"
	# cd ../; docker-compose run --rm -v $(PARENT_DIR)db/starter_db:/starter_db server pg_dump -h db -U postgres -f /starter_db/starter_db.sql chalk
	#
	# Also can build on gcloud commands
	# Requires creating bucket and adding CloudSQL service account w/ read & write permissions
	# gcloud sql export sql chalk-prod gs://default-323301-db-backups/test.gz -d chalk-prod
	# gcloud sql databases delete chalk-prod --instance chalk-prod && \
	# gcloud sql databases create chalk-prod --instance chalk-prod && \
	# gcloud sql import sql chalk-prod gs://default-323301-db-backups/test.gz -d chalk-prod --user=chalk-prod
