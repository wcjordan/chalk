#!make
include .env

IMAGE_REPO = gcr.io/$(GCP_PROJECT)
SERVER_IMAGE = $(IMAGE_REPO)/chalk-server
UI_IMAGE = $(IMAGE_REPO)/chalk-ui
UI_IMAGE_BASE = $(IMAGE_REPO)/chalk-ui-base

# Build containers
.PHONY: build
build:
	DOCKER_BUILDKIT=1 docker build -t $(SERVER_IMAGE):local-latest server
	DOCKER_BUILDKIT=1 docker build -f ui/Dockerfile.base -t $(UI_IMAGE_BASE):local-latest ui
	env $$(grep -v '^#' .prod.env | xargs) sh -c ' \
		DOCKER_BUILDKIT=1 docker build \
			--build-arg expoClientId=$$EXPO_CLIENT_ID \
			--build-arg sentryDsn=$$SENTRY_DSN \
			--build-arg "GCP_PROJECT=$(GCP_PROJECT)" \
			--build-arg "BASE_IMAGE_TAG=local-latest" \
			-t $(UI_IMAGE):local-latest ui'

# Test & lint
.PHONY: test
test: build
	DOMAIN=localhost docker run --env-file .env --env DOMAIN --rm -t $(SERVER_IMAGE):local-latest make test
	docker run --rm -t -w / \
		-v $(PWD)/ui/Makefile:/Makefile \
		-v $(PWD)/ui/js/src:/js/src \
		-v $(PWD)/ui/js/.eslintrc:/js/.eslintrc \
		-v $(PWD)/ui/js/babel.config.js:/js/babel.config.js \
		-v $(PWD)/ui/js/jest.config.js:/js/jest.config.js \
		-v $(PWD)/ui/js/tsconfig.json:/js/tsconfig.json \
		-v $(PWD)/ui/js/.storybook:/js/.storybook \
		-v $(PWD)/ui/js/__mocks__:/js/__mocks__ \
		$(UI_IMAGE_BASE):local-latest \
		make test

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
		--rm -t -w / \
		-v $(PWD)/ui/Makefile:/Makefile \
		-v $(PWD)/ui/js/src:/js/src \
		-v $(PWD)/ui/js/web:/js/web \
		-v $(PWD)/ui/js/app.config.js:/js/app.config.js \
		-v $(PWD)/ui/js/App.tsx:/js/App.tsx \
		-v $(PWD)/ui/js/assets:/js/assets \
		-v $(PWD)/ui/js/babel.config.js:/js/babel.config.js \
		$(UI_IMAGE_BASE):local-latest \
		make publish
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
