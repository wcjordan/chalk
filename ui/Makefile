#!make

# Test w/ Jest
.PHONY: test
test:
	# Lint & typecheck by building
	yarn run build
	# Unit & snapshot tests for UI
	yarn jest

# ESLint & Prettier JS formatting
.PHONY: format
format:
	cd js; npx lint-staged

.PHONY: storybook
storybook:
	docker run --rm -p 127.0.0.1:9009:9009 --rm chalk-ui-image:latest npm run storybook

# Update snapshot tests
.PHONY: update-snapshots
update-snapshots:
	docker run --rm -v $(PWD)/js/src:/js_app/src chalk-ui-image:latest yarn jest -u

# Fix import ordering
.PHONY: fix-imports
fix-imports:
	cd js; npx eslint --fix "**/*.{ts,tsx,js,jsx}"
