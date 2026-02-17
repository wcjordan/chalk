#!make
ENVIRONMENT ?= PROD
ifeq ($(ENVIRONMENT),STAGING)
  PROD_ENV_FILE = .staging.env
else
  PROD_ENV_FILE = .prod.env
endif

export PROD_ENV_FILE
include $(PROD_ENV_FILE)

IMAGE_REPO = us-east4-docker.pkg.dev/$(GCP_PROJECT)/default-gar
SERVER_IMAGE = $(IMAGE_REPO)/chalk-server
UI_IMAGE = $(IMAGE_REPO)/chalk-ui
UI_IMAGE_BASE = $(IMAGE_REPO)/chalk-ui-base

# Build containers
.PHONY: build
build:
	docker buildx create --driver docker-container --name chalk-default --use || true
	docker buildx build --push \
		--cache-to type=registry,ref=${IMAGE_REPO}/chalk-server-cache:dev_server,mode=max \
		--cache-from type=registry,ref=${IMAGE_REPO}/chalk-server-cache:dev_server \
		-t ${SERVER_IMAGE}:local-latest \
		server
	env $$(grep -v '^#' $(PROD_ENV_FILE) | xargs) sh -c ' \
		docker buildx build --push \
			--cache-to type=registry,ref=${IMAGE_REPO}/chalk-ui-cache:dev_app,mode=max \
			--cache-from type=registry,ref=${IMAGE_REPO}/chalk-ui-cache:dev_app \
			--cache-from type=registry,ref=${IMAGE_REPO}/chalk-ui-cache:dev_test \
			--build-arg sentryDsn=$$SENTRY_DSN \
			-t ${UI_IMAGE}:local-latest \
			--target js_app_prod \
			ui'
	env $$(grep -v '^#' $(PROD_ENV_FILE) | xargs) sh -c ' \
		docker buildx build --push \
			--cache-to type=registry,ref=${IMAGE_REPO}/chalk-ui-cache:dev_test,mode=max \
			--cache-from type=registry,ref=${IMAGE_REPO}/chalk-ui-cache:dev_app \
			--cache-from type=registry,ref=${IMAGE_REPO}/chalk-ui-cache:dev_test \
			--build-arg sentryDsn=$$SENTRY_DSN \
			-t ${UI_IMAGE_BASE}:local-latest \
			--target js_test_env \
			ui'

# Test & lint
.PHONY: test
test: build
	$(MAKE) -C server test
	$(MAKE) -C ui test
	$(MAKE) -C tests lint

# Start environment for development
# Note, you need to manually navigate to <host>:19000/debugger-ui/ to get Expo to work on mobile
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
	$(MAKE) -C tests format

# Stops the dev env and deletes _env_id.txt
.PHONY: superclean
superclean: stop
	rm _env_id.txt

###
# Deployment targets
###

.PHONY: deploy-mobile-app
deploy-mobile-app:
	if [ "$(ENVIRONMENT)" = "PROD" ]; then \
		$(MAKE) -C ui publish; \
	fi

# NOTE deploy from built on Jenkins rather than building & pushing here
# Make it so helm to deploy can be used from here and from jenkins for tests
# Probably use a python script to call Helm to add flexibility

.PHONY: setup-continuous-delivery
setup-continuous-delivery:
	cd ui/js; npx eas secret:push --force --scope project --env-file ../../$(PROD_ENV_FILE)
	env $$(grep -v '^#' $(PROD_ENV_FILE) | xargs) \
		$$(grep '^CHALK_OAUTH_REFRESH_TOKEN' .env | xargs) \
		sh -c ' \
		helm upgrade --install \
			--set environment=$(ENVIRONMENT) \
			--set permittedUsers=$$PERMITTED_USERS \
			--set sentry_dsn=$$SENTRY_DSN \
			--set sentry_token=$$SENTRY_TOKEN \
			--set server.dbPassword=$$DB_PASSWORD \
			--set server.secretKey=$$SECRET_KEY \
			--set chalk_oauth_refresh_token=$$CHALK_OAUTH_REFRESH_TOKEN \
			chalk-prod-cd continuous_delivery_setup'

###
# Worktree management for targets
###
WORKTREE_BRANCH ?= ""

# Creates a worktree for Claude to work in and starts claude there.
# Call with a branch name to work under in a new worktree.
# Usage: make claude-worktree WORKTREE_BRANCH=branch_name
.PHONY: claude-worktree
claude-worktree:
	./helpers/create_worktree.sh $(WORKTREE_BRANCH)
	(cd $(HOME)/git/chalk-worktrees/$(WORKTREE_BRANCH) && claude)
	echo "After pushing cleanup the worktree with: make remove-worktree WORKTREE_BRANCH=$(WORKTREE_BRANCH)"

# Checks a worktree branch out after detaching the worktree's HEAD.
# Call with a branch name to checkout in the primary repo
# Usage: make absorb-worktree WORKTREE_BRANCH=branch_name
.PHONY: absorb-worktree
absorb-worktree:
	(cd $(HOME)/git/chalk-worktrees/$(WORKTREE_BRANCH) && git switch --detach)
	git checkout $(WORKTREE_BRANCH)

# Call with a branch name to delete a branch and worktree.
# Usage: make remove-worktree WORKTREE_BRANCH=branch_name
.PHONY: remove-worktree
remove-worktree:
	@if [ -d $(HOME)/git/chalk-worktrees/$(WORKTREE_BRANCH) ]; then \
		git worktree remove $(HOME)/git/chalk-worktrees/$(WORKTREE_BRANCH); \
	fi
	git branch -D $(WORKTREE_BRANCH)
