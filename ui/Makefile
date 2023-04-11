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
UI_IMAGE_BASE = $(IMAGE_REPO)/chalk-ui-base

# Test w/ Jest
.PHONY: test
test:
	# Lint
	cd js; yarn eslint --max-warnings=0 --ext='js,jsx,ts,tsx' .
	# Typecheck
	cd js; yarn tsc
	# Unit & snapshot tests for UI
	cd js; yarn test

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
	cd js && \
	npx eas secret:push --force --scope project --env-file ../../$(PROD_ENV_FILE) && \
	CI=1 npx eas-cli build --platform android --profile preview

# Hard clean which fixes some react-native issues
# Use yarn install and yarn start --clean after this
.PHONY: clean
clean:
	cd js; rm -rf node_modules && rm -f yarn.lock && yarn cache clean
