#!make

# Build containers
.PHONY: build
build:
	DOCKER_BUILDKIT=1 docker build -f ui/Dockerfile.dev -t chalk-ui-image:latest ui
	DOCKER_BUILDKIT=1 docker build -t chalk-server-image:latest server

# Test & lint
.PHONY: test
test: build
	docker run --rm -t -w / chalk-ui-image:latest make test
	DB_HOSTNAME=localhost docker run --env-file .env --env DB_HOSTNAME --rm chalk-server-image:latest make test

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

.PHONY: deploy
deploy:
	env $$(grep -v '^#' .prod.env | xargs) sh -c ' \
		helm upgrade --install --namespace chalk-namespace \
			--set server.secretKey=$$SECRET_KEY \
			--set server.dbPassword=$$POSTGRES_PASSWORD \
			chalk-staging helm'

# Create Kind for local k8s development
# requires Tilt's ctlptl
.PHONY: create-kind
create-kind:
	ctlptl create cluster kind --registry=ctlptl-registry

# Delete Kind for local k8s development
.PHONY: delete-kind
delete-kind:
	ctlptl delete cluster kind-kind
