#!make
IMAGE_REPO = gcr.io/flipperkid-default
UI_IMAGE_DEV = $(IMAGE_REPO)/chalk-ui-image-dev

# Test w/ Jest
.PHONY: test
test:
	# Lint
	cd js; yarn eslint --ext 'js,jsx,ts,tsx' .
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
		$(UI_IMAGE_DEV):latest yarn run storybook

# Update snapshot tests
.PHONY: update-snapshots
update-snapshots:
	docker run --rm -v $(PWD)/js/src:/js/src $(UI_IMAGE_DEV):latest yarn jest -u

# Fix import ordering
.PHONY: fix-imports
fix-imports:
	cd js; npx eslint --fix "**/*.{ts,tsx,js,jsx}"
