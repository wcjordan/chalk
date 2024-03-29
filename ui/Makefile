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

# Test w/ Jest
.PHONY: test
test:
	# Lint
	cd js; yarn eslint --max-warnings=0 --ext='js,jsx,ts,tsx' .
	# Typecheck
	cd js; yarn tsc
	# Unit & snapshot tests for UI
	cd js; JEST_JUNIT_CLASSNAME="ui_unit_tests.{classname} {title}" yarn jest

.PHONY: containerized-test
containerized-test:
	docker run --rm -t -w / \
		-v $(CURDIR)/Makefile:/Makefile \
		-v $(CURDIR)/js/src:/js/src \
		-v $(CURDIR)/js/assets:/js/assets \
		-v $(CURDIR)/js/.eslintrc:/js/.eslintrc \
		-v $(CURDIR)/js/babel.config.js:/js/babel.config.js \
		-v $(CURDIR)/js/jest.config.js:/js/jest.config.js \
		-v $(CURDIR)/js/tsconfig.json:/js/tsconfig.json \
		-v $(CURDIR)/js/.storybook:/js/.storybook \
		-v $(CURDIR)/js/__mocks__:/js/__mocks__ \
		$(UI_IMAGE_BASE):local-latest \
		make test

# ESLint & Prettier JS formatting
.PHONY: format
format:
	cd js; npx lint-staged

.PHONY: storybook
storybook:
	docker run --rm -p 127.0.0.1:9009:9009 \
		-a stdin -a stdout -i -t \
		-v $(PWD)/js/src:/js/src \
		-v $(PWD)/js/__mocks__:/js/__mocks__ \
		-v $(PWD)/js/assets:/js/assets \
		-v $(PWD)/js/babel.config.js:/js/babel.config.js \
		-v $(PWD)/js/.storybook:/js/.storybook \
		$(UI_IMAGE_BASE):local-latest \
		yarn run storybook

# Update snapshot tests
.PHONY: update-snapshots
update-snapshots:
	docker run --rm -t \
		-v $(PWD)/js/src:/js/src \
		-v $(PWD)/js/assets:/js/assets \
		-v $(PWD)/js/babel.config.js:/js/babel.config.js \
		-v $(PWD)/js/jest.config.js:/js/jest.config.js \
		-v $(PWD)/js/.storybook:/js/.storybook \
		-v $(PWD)/js/__mocks__:/js/__mocks__ \
		$(UI_IMAGE_BASE):local-latest \
		yarn jest -u

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
