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

IMAGE_REPO = gcr.io/$(GCP_PROJECT)
SERVER_IMAGE = $(IMAGE_REPO)/chalk-server-image

PARENT_DIR = $(dir $(PWD))

# Test w/ PyTest & lint Django app
.PHONY: test
test:
	flake8 chalk/todos  # TODO change to .
	# TODO (jordan) remove need to hardcode apps
	pylint -j 0 --load-plugins pylint_django chalk

	# Unit tests
	DJANGO_SETTINGS_MODULE=chalk.settings.testing python manage.py test chalk.todos

# Yapf formatting
.PHONY: format
format:
	docker run --rm -v $(PWD)/server:/usr/src/app $(SERVER_IMAGE):latest yapf -ri .

# Make migrations for server
.PHONY: create-migrations
create-migrations:
	DJANGO_SETTINGS_MODULE=chalk.settings.testing docker run --rm \
		--env-file ../.env --env DJANGO_SETTINGS_MODULE \
		-v $(PWD):/usr/src/app $(SERVER_IMAGE):latest \
		python manage.py makemigrations --verbosity 3

# Add an admin to Django
# For production env:  make create-superuser ENV_NAME=prod
ENV_NAME ?= dev-$(shell cat ../_env_id.txt)
YQ_EXPRESSION = '.metadata.name = "create-superuser-chalk-$(ENV_NAME)" \
  | .spec.template.spec.containers[0].command[1] = "-instances=$(GCP_PROJECT):us-east4:chalk-$(ENV_NAME)=tcp:5432" \
  | .spec.template.spec.containers[1].image = "gcr.io/$(GCP_PROJECT)/chalk-server-image:latest" \
  | .spec.template.spec.containers[1].env[].valueFrom.secretKeyRef.name = "chalk-$(ENV_NAME)-server-secrets"'

.PHONY: create-superuser
create-superuser:
	yq eval $(YQ_EXPRESSION) jobs/create_superuser.yaml | kubectl apply -f -

# Update starter data for server
.PHONY: update-starter-data
update-starter-data:
	exit 1
	# TODO (jordan) old version below.  Need a k8s compatible version
	# echo "Rerun if failed w/ could not connect to server: Connection refused"
	# cd ../; docker-compose run --rm -v $(PARENT_DIR)db/starter_db:/starter_db server pg_dump -h db -U postgres -f /starter_db/starter_db.sql chalk
