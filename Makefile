#!make
ENVIRONMENT ?= PROD
ifeq ($(ENVIRONMENT),STAGING)
  PROD_ENV_FILE = .staging.env
else
  PROD_ENV_FILE = .prod.env
endif

export PROD_ENV_FILE
include $(PROD_ENV_FILE)

IMAGE_REPO = us-east4-docker.pkg.dev/$(GCP_PROJECT)/default-gar
SERVER_IMAGE = $(IMAGE_REPO)/chalk-server
UI_IMAGE = $(IMAGE_REPO)/chalk-ui
UI_IMAGE_BASE = $(IMAGE_REPO)/chalk-ui-base

# Build containers
.PHONY: build
build:
	DOCKER_BUILDKIT=1 docker build -t $(SERVER_IMAGE):local-latest server
	env $$(grep -v '^#' $(PROD_ENV_FILE) | xargs) sh -c ' \
		DOCKER_BUILDKIT=1 docker build \
			--build-arg sentryDsn=$$SENTRY_DSN \
			--target js_app_prod \
			-t $(UI_IMAGE):local-latest ui'
	env $$(grep -v '^#' $(PROD_ENV_FILE) | xargs) sh -c ' \
		DOCKER_BUILDKIT=1 docker build \
			--build-arg sentryDsn=$$SENTRY_DSN \
			--target js_test_env \
			-t $(UI_IMAGE_BASE):local-latest ui'

# Test & lint
.PHONY: test
test: build
	DOMAIN=localhost docker run --env-file .env --env DOMAIN --rm -t $(SERVER_IMAGE):local-latest make test
	$(MAKE) -C ui containerized-test

# Run integration tests
# Requires dev env to be running (make start)
# make integration-test TEST_TO_RUN=label_filtering_test.py
TEST_TO_RUN ?= ""
.PHONY: integration-test
integration-test:
	cd tests; env $$(grep -v '^#' ../.env | xargs) sh -c ' \
		pytest -vv $(TEST_TO_RUN) --server_domain chalk-dev.$$ROOT_DOMAIN'

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
# Note, this shouldn't be needed as we deploy to prod in the Jenkinsfile
.PHONY: deploy-k8s
deploy-k8s: build
	if [ "$$(kubectl config current-context)" != "$(K8S_CONTEXT)" ]; then \
		exit 1; \
	fi

	docker push $(SERVER_IMAGE):local-latest
	docker push $(UI_IMAGE):local-latest
	env $$(grep -v '^#' $(PROD_ENV_FILE) | xargs) sh -c ' \
		helm upgrade --install \
			--set domain=chalk.$$ROOT_DOMAIN \
			--set environment=$(ENVIRONMENT) \
			--set gcpProject=$$GCP_PROJECT \
			--set permittedUsers=$$PERMITTED_USERS \
			--set server.dbPassword=$$DB_PASSWORD \
			--set server.secretKey=$$SECRET_KEY \
			chalk-prod helm'

.PHONY: deploy-mobile-app
deploy-mobile-app:
	if [ "$(ENVIRONMENT)" = "PROD" ]; then \
		$(MAKE) -C ui publish; \
	fi

# NOTE deploy from built on Jenkins rather than building & pushing here
# Make it so helm to deploy can be used from here and from jenkins for tests
# Probably use a python script to call Helm to add flexibility

.PHONY: setup-continuous-delivery
setup-continuous-delivery:
	cd ui/js; npx eas secret:push --force --scope project --env-file ../../$(PROD_ENV_FILE)
	env $$(grep -v '^#' $(PROD_ENV_FILE) | xargs) \
		$$(grep '^CHALK_OAUTH_REFRESH_TOKEN' .env | xargs) \
		sh -c ' \
		helm upgrade --install \
			--set environment=$(ENVIRONMENT) \
			--set permittedUsers=$$PERMITTED_USERS \
			--set sentry_dsn=$$SENTRY_DSN \
			--set sentry_token=$$SENTRY_TOKEN \
			--set server.dbPassword=$$DB_PASSWORD \
			--set server.secretKey=$$SECRET_KEY \
			--set chalk_oauth_refresh_token=$$CHALK_OAUTH_REFRESH_TOKEN \
			chalk-prod-cd continuous_delivery_setup'

# Stops the dev env and deletes _env_id.txt
.PHONY: superclean
superclean: stop
	rm _env_id.txt
