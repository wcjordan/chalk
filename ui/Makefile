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
UI_IMAGE_BASE = $(IMAGE_REPO)/chalk-ui-base

.PHONY: run-test-container
run-test-container:
	docker pull $(UI_IMAGE_BASE):local-latest
	docker run --rm -t \
		$(DOCKER_ARGS) \
		-v $(CURDIR)/Makefile:/workspace/Makefile \
		-v $(CURDIR)/js/__mocks__:/workspace/js/__mocks__ \
		-v $(CURDIR)/js/.eslintrc:/workspace/js/.eslintrc \
		-v $(CURDIR)/js/.storybook:/workspace/js/.storybook \
		-v $(CURDIR)/js/assets:/workspace/js/assets \
		-v $(CURDIR)/js/babel.config.js:/jworkspace/s/babel.config.js \
		-v $(CURDIR)/js/jest.config.js:/workspace/js/jest.config.js \
		-v $(CURDIR)/js/src:/workspace/js/src \
		-v $(CURDIR)/js/tsconfig.json:/workspace/js/tsconfig.json \
		$(UI_IMAGE_BASE):local-latest \
		$(TEST_CMD) TEST_ARGS="$(TEST_ARGS)"

.PHONY: containerized-test
containerized-test:
	make run-test-container TEST_CMD="make test" TEST_ARGS="" DOCKER_ARGS=""
	make test-storybook

# Targets to be run instide the test container
.PHONY: test
test:
	# Lint
	cd js; yarn eslint --max-warnings=0 --ext='js,jsx,ts,tsx' .
	# Typecheck
	cd js; yarn tsc
	# Unit tests
	make test-jest TEST_ARGS=""

.PHONY: test-jest
test-jest:
	cd js; JEST_JUNIT_CLASSNAME="ui_unit_tests.{classname} {title}" NODE_OPTIONS="$$NODE_OPTIONS --experimental-vm-modules" yarn jest $(TEST_ARGS)

.PHONY: test-storybook-inner
test-storybook-inner:
	cd js; JEST_JUNIT_CLASSNAME="ui_storybook_tests.{classname} {title}" npx test-storybook --no-index-json $(TEST_ARGS)

# Storybook tests
.PHONY: test-storybook
test-storybook:
	# Create network
	docker network create storybook-network

	# NOTE stderr is suppressed here to avoid confusing messages from SIGKILL when finished.  Remove if debugging
	timeout 180 make run-test-container TEST_CMD="npx http-server --silent -p 9009 /workspace/js/storybook-static" TEST_ARGS="" \
		DOCKER_ARGS="-w /workspace/js -p 9009 --network storybook-network --name storybook-test-instance" 2> /dev/null &
	sleep 10

	# Capture output, but stop the storybook container before exiting with the result
	make run-test-container TEST_CMD="make test-storybook-inner" \
		TEST_ARGS="--url http://storybook-test-instance:9009 $(TEST_ARGS)" \
		DOCKER_ARGS="--network storybook-network" || \
		RESULT=`echo $$?`; \
		docker container stop --signal SIGKILL storybook-test-instance; \
		docker network rm storybook-network; \
		exit $$RESULT

.PHONY: storybook
storybook:
	make run-test-container TEST_CMD="yarn run storybook" TEST_ARGS="" \
		DOCKER_ARGS="-w /workspace/js -p 127.0.0.1:9009:9009 -a stdin -a stdout -i"

# Update snapshot tests
.PHONY: update-snapshots
update-snapshots:
	make run-test-container TEST_CMD="make test-jest" TEST_ARGS="--updateSnapshot" DOCKER_ARGS=""
	make test-storybook TEST_ARGS="--updateSnapshot"

# ESLint & Prettier JS formatting
# was cd js; npx lint-staged
.PHONY: format
format:
	cd js; npx prettier --write "**/*.{ts,tsx,js,jsx,json,css,scss}" && npx eslint "**/*.{ts,tsx,js,jsx}"

# Fix import ordering
.PHONY: fix-imports
fix-imports:
	cd js; npx eslint --fix "**/*.{ts,tsx,js,jsx}" --ignore-pattern "build"

# Publish Expo
.PHONY: publish
publish:
	cd js; CI=1 npx eas-cli build --platform android --profile preview

# Publish Expo Development Build
.PHONY: publish-dev
publish-dev:
	cd js; npx eas-cli build --platform android --profile development


# Hard clean which fixes some react-native issues
# Use yarn install and yarn start --clean after this
.PHONY: clean
clean:
	cd js; rm -rf node_modules && rm -f yarn.lock && yarn cache clean
