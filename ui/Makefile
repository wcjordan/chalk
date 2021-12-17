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
UI_IMAGE_DEV = $(IMAGE_REPO)/chalk-ui-dev

# Test w/ Jest
.PHONY: test
test:
	# Lint
	cd js; yarn eslint --max-warnings=0 --ext='js,jsx,ts,tsx' .
	# Typecheck
	cd js; yarn tsc
	# Unit & snapshot tests for UI
	cd js; yarn test
	# Build as a sanity check
	cd js; yarn build

# ESLint & Prettier JS formatting
.PHONY: format
format:
	cd js; npx lint-staged

.PHONY: storybook
storybook:
	docker run --rm -v $(PWD)/js/src:/js/src -p 127.0.0.1:9009:9009 \
		-a stdin -a stdout -i -t \
		$(UI_IMAGE_DEV):local-latest yarn run storybook

# Update snapshot tests
.PHONY: update-snapshots
update-snapshots:
	docker run --rm -v $(PWD)/js/src:/js/src $(UI_IMAGE_DEV):local-latest yarn jest -u

# Fix import ordering
.PHONY: fix-imports
fix-imports:
	cd js; npx eslint --fix "**/*.{ts,tsx,js,jsx}" --ignore-pattern "build"

# Publish Expo
.PHONY: publish
publish:
	cd js; npx expo login --non-interactive -u $$EXPO_USERNAME && npx expo publish --non-interactive

# Hard clean which fixes some react-native issues
# Use yarn install and yarn start --clean after this
.PHONY: clean
clean:
	cd js; rm -rf node_modules && rm -f yarn.lock && yarn cache clean
