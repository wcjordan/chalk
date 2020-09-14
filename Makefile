#!make

# Build containers
.PHONY: build
build:
	DOCKER_BUILDKIT=1 docker build -f ui/Dockerfile.dev -t chalk-ui-image:latest ui
	DOCKER_BUILDKIT=1 docker build -t chalk-server-image:latest server

# Test & lint
.PHONY: test
test: build
	docker run --rm chalk-ui-image:latest make test
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
