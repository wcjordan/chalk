#!make
IMAGE_REPO = gcr.io/flipperkid-default
SERVER_IMAGE = $(IMAGE_REPO)/chalk-server-image
UI_IMAGE = $(IMAGE_REPO)/chalk-ui-image-prod
UI_IMAGE_DEV = $(IMAGE_REPO)/chalk-ui-image-dev

# Build containers
.PHONY: build
build:
	DOCKER_BUILDKIT=1 docker build -t $(SERVER_IMAGE):latest server
	DOCKER_BUILDKIT=1 docker build -f ui/Dockerfile.dev -t $(UI_IMAGE_DEV):latest ui
	env $$(grep -v '^#' .prod.env | xargs) sh -c ' \
		DOCKER_BUILDKIT=1 docker build \
			--build-arg sentryDsn=$$SENTRY_DSN \
			-t $(UI_IMAGE):latest ui'

# Test & lint
.PHONY: test
test: build
	docker run --rm -t -w / $(UI_IMAGE_DEV):latest make test
	DB_HOSTNAME=localhost docker run --env-file .env --env DB_HOSTNAME --rm $(SERVER_IMAGE):latest make test

# Start environment for development
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
		--rm -t -w / $(UI_IMAGE_DEV):latest make publish
	docker push $(SERVER_IMAGE):latest
	docker push $(UI_IMAGE):latest
	env $$(grep -v '^#' .prod.env | xargs) sh -c ' \
		helm upgrade --install \
			--set environment=PROD \
			--set server.dbPassword=$$DB_PASSWORD \
			--set server.djangoEmail=$$DJANGO_EMAIL \
			--set server.djangoPassword=$$DJANGO_PASSWORD \
			--set server.djangoUsername=$$DJANGO_USERNAME \
			--set server.secretKey=$$SECRET_KEY \
			--set ui.sentryDsn=$$SENTRY_DSN \
			--set ui.sentryToken=$$SENTRY_TOKEN \
			chalk-prod helm'

# NOTE deploy from built on Jenkins rather than building & pushing here
# Make it so helm to deploy can be used from here and from jenkins for tests
# Probably use a python script to call Helm to add flexibility

# Stops the dev env and deletes the Cloud SQL DB used by dev
# Also deletes _env_id.txt since that DB name won't be reusable for a week
.PHONY: superclean
superclean: stop
	gcloud sql instances delete chalk-dev-$$(cat _env_id.txt) && rm _env_id.txt
