#!make

# Test w/ Jest
.PHONY: test
test:
	# Unit & snapshot tests for UI
	cd js; yarn jest
	# Lint & typecheck by building
	cd js; yarn run build

# ESLint & Prettier JS formatting
.PHONY: format
format:
	cd js; npx lint-staged

.PHONY: storybook
storybook:
	docker run --rm -v $(PWD)/js/src:/js/src -p 127.0.0.1:9009:9009 \
		chalk-ui-image:latest npm run storybook

# Update snapshot tests
.PHONY: update-snapshots
update-snapshots:
	docker run --rm -v $(PWD)/js/src:/js/src chalk-ui-image:latest yarn jest -u

# Fix import ordering
.PHONY: fix-imports
fix-imports:
	cd js; npx eslint --fix "**/*.{ts,tsx,js,jsx}"
