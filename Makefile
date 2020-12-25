#!make
IMAGE_REPO = gcr.io/flipperkid-default
SERVER_IMAGE = $(IMAGE_REPO)/chalk-server-image
UI_IMAGE = $(IMAGE_REPO)/chalk-ui-image-prod
UI_IMAGE_DEV = $(IMAGE_REPO)/chalk-ui-image-dev

# Build containers
.PHONY: build
build:
	DOCKER_BUILDKIT=1 docker build -f ui/Dockerfile.dev -t $(UI_IMAGE_DEV):latest ui
	DOCKER_BUILDKIT=1 docker build -t $(UI_IMAGE):latest ui
	DOCKER_BUILDKIT=1 docker build -t $(SERVER_IMAGE):latest server

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
	docker push $(SERVER_IMAGE):latest
	docker push $(UI_IMAGE):latest
	env $$(grep -v '^#' .prod.env | xargs) sh -c ' \
		helm upgrade --install \
			--set server.secretKey=$$SECRET_KEY \
			--set server.dbPassword=$$POSTGRES_PASSWORD \
			chalk-prod helm'

# Create Kind for local k8s development
# requires Tilt's ctlptl
.PHONY: create-kind
create-kind:
	ctlptl create cluster kind --registry=ctlptl-registry

# Delete Kind for local k8s development
.PHONY: delete-kind
delete-kind:
	ctlptl delete cluster kind-kind
