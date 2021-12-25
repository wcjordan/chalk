#!make
include .env

IMAGE_REPO = gcr.io/$(GCP_PROJECT)
SERVER_IMAGE = $(IMAGE_REPO)/chalk-server
UI_IMAGE = $(IMAGE_REPO)/chalk-ui
UI_IMAGE_DEV = $(IMAGE_REPO)/chalk-ui-dev

# Build containers
.PHONY: build
build:
	DOCKER_BUILDKIT=1 docker build -t $(SERVER_IMAGE):local-latest server
	DOCKER_BUILDKIT=1 docker build -f ui/Dockerfile.dev --build-arg "GCP_PROJECT=$(GCP_PROJECT)" -t $(UI_IMAGE_DEV):local-latest ui
	env $$(grep -v '^#' .prod.env | xargs) sh -c ' \
		DOCKER_BUILDKIT=1 docker build \
			--build-arg sentryDsn=$$SENTRY_DSN \
			--build-arg "GCP_PROJECT=$(GCP_PROJECT)" \
			-t $(UI_IMAGE):local-latest ui'

# Test & lint
.PHONY: test
test: build
	docker run --env-file .env --rm $(SERVER_IMAGE):local-latest make test
	docker run --rm -t -w / $(UI_IMAGE_DEV):local-latest make test

# Run integration tests
# Requires dev env to be running (make start)
# make integration-test TEST_TO_RUN=label_filtering_test.py
TEST_TO_RUN ?= ""
.PHONY: integration-test
integration-test:
	env $$(grep -v '^#' .env | xargs) sh -c ' \
		pytest tests/$(TEST_TO_RUN) --server_domain chalk-dev.$$ROOT_DOMAIN'

# Start environment for development
# Note, you need to manually navigate to <host>:19000/debugger-ui/ to get Expo to work on mobile
.PHONY: start
start:
	env $$(grep -v '^#' .env | xargs) tilt up

# Stop environment
.PHONY: stop
stop:
	env $$(grep -v '^#' .env | xargs) tilt down

# Format code
.PHONY: format
format:
	$(MAKE) -C ui format
	$(MAKE) -C server format

# Deploy to production
# To delete: helm delete chalk-prod
.PHONY: deploy
deploy: build
	docker run --env-file .prod.env --env ENVIRONMENT=prod --env DEBUG=false \
		--rm -t -w / $(UI_IMAGE_DEV):local-latest make publish
	docker push $(SERVER_IMAGE):local-latest
	docker push $(UI_IMAGE):local-latest
	env $$(grep -v '^#' .prod.env | xargs) sh -c ' \
		helm upgrade --install \
			--set domain=chalk.$$ROOT_DOMAIN \
			--set environment=PROD \
			--set gcpProject=$$GCP_PROJECT \
			--set server.dbPassword=$$DB_PASSWORD \
			--set server.djangoEmail=$$DJANGO_EMAIL \
			--set server.djangoPassword=$$DJANGO_PASSWORD \
			--set server.djangoUsername=$$DJANGO_USERNAME \
			--set server.secretKey=$$SECRET_KEY \
			chalk-prod helm'

# NOTE deploy from built on Jenkins rather than building & pushing here
# Make it so helm to deploy can be used from here and from jenkins for tests
# Probably use a python script to call Helm to add flexibility

# Stops the dev env and deletes the Cloud SQL DB used by dev
# Also deletes _env_id.txt since that DB name won't be reusable for a week
.PHONY: superclean
superclean: stop
	gcloud sql instances delete chalk-dev-$$(cat _env_id.txt) && rm _env_id.txt
