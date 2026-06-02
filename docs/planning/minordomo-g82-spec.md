# Spec: Use jenkins-shared-library for dind bootstrap, remove local Dockerfile.helm

## Overview

Migrate chalk's Jenkins pipeline to use the `buildAndPushImage` step from the
`jenkins-shared-library` (published by gcp-setup). Remove the local helm image build and
related files, and update all dind-based build stages to use the shared library step.

**Prerequisite:** gcp-setup PR #32 (Extend buildAndPushImage with context, target,
extraBuildArgs, and additionalCacheFrom) and the weekly gcp-setup job have both merged and
the `jenkins-helm:latest` image is published to GAR.

**Files changed:**
- `Jenkinsfile` — add `@Library`, update image refs, migrate build stages
- `jenkins/gcloud_helm.Dockerfile` — delete
- `jenkins/Jenkinsfile.base` — delete
- `jenkins/dockerHelper.groovy` — delete

**Important post-merge follow-up (infra, not code):** The Jenkins job that runs
`jenkins/Jenkinsfile.base` will fail once that file is deleted. That job should be
retired/disabled in Jenkins after this PR merges, since the helm image is now built by
gcp-setup's weekly job.

---

## Stage 1: Load shared library, update helm image references, and remove helm build files

### Description

Add the shared library import, replace the local `gcloud-helm:latest` pod image references
with `jenkins-helm:latest`, and remove the files that supported chalk's local helm image
build.

1. Add `@Library('jenkins-shared-library') _` as the first line of `Jenkinsfile` (before
   the `def GAR_HOST` line).
2. In the "Integration Tests" and "Continuous Deployment" stage pod spec YAML strings,
   change every occurrence of `${GAR_REPO}/gcloud-helm:latest` to
   `${GAR_REPO}/jenkins-helm:latest`.
3. Delete `jenkins/gcloud_helm.Dockerfile`.
4. Delete `jenkins/Jenkinsfile.base`.
5. Commit.

No build-stage behaviour changes in this stage; `jenkins/dockerHelper.groovy` stays (still
used by Build UI and Build Server).

### Acceptance Criteria

- `Jenkinsfile` begins with `@Library('jenkins-shared-library') _`
- `git grep 'gcloud-helm'` returns no matches in `Jenkinsfile`
- `git grep 'jenkins-helm'` matches exactly two pod specs in `Jenkinsfile` (Integration
  Tests and Continuous Deployment)
- `jenkins/gcloud_helm.Dockerfile` does not exist
- `jenkins/Jenkinsfile.base` does not exist
- `make test` passes (unit tests don't exercise the Jenkinsfile; this is a sanity check
  only — real verification is the next CI run after merge)

---

## Stage 2: Migrate server build stage to `buildAndPushImage`

### Description

Replace the "Build Server" stage's manual bootstrap + `sh` block with a single
`buildAndPushImage(...)` call from the shared library.

The `buildAndPushImage` step handles container selection (defaults to `containerName:
'dind'`), gcloud install + auth, buildx builder creation, and the `docker buildx build
--push` command. The surrounding `container('dind') { script { ... } sh """ ... ``` """}`
block is removed entirely.

Replacement call:

```groovy
steps {
    buildAndPushImage(
        garHost: GAR_HOST,
        cacheRef: "${GAR_REPO}/chalk-server-cache:ci_server",
        dockerfile: 'server/Dockerfile',   // path from repo root, not from inside context
        imageTag: "${GAR_REPO}/chalk-server:${SANITIZED_BUILD_TAG}",
        builderName: 'chalk-default',
        context: 'server'
    )
}
```

Commit after migration.

### Acceptance Criteria

- "Build Server" `steps` block contains a single `buildAndPushImage(...)` call with the
  parameters above
- No `container('dind')`, no `dockerHelper`, no `sh """...docker buildx build...server"""`
  in the Build Server stage
- `jenkins/dockerHelper.groovy` still exists (still referenced by Build UI stage)
- `make test` passes

---

## Stage 3: Migrate UI build stage to `buildAndPushImage` and remove dockerHelper

### Description

Replace the "Build UI" stage's manual bootstrap + `sh` block with two sequential
`buildAndPushImage(...)` calls — one per image target. Then delete
`jenkins/dockerHelper.groovy`.

The `SENTRY_DSN` credential binding in the stage `environment {}` block is kept; its value
is passed to each call via `extraBuildArgs`. Use `\$SENTRY_DSN` (with literal backslash-
dollar) so the variable is resolved by the shell at runtime rather than in Groovy, matching
the existing pattern and keeping the value out of Groovy console logs.

Replacement calls:

```groovy
environment {
    SENTRY_DSN = credentials('chalk-prod-cd-sentry-dsn')
}
steps {
    buildAndPushImage(
        garHost: GAR_HOST,
        cacheRef: "${GAR_REPO}/chalk-ui-cache:ci_app",
        additionalCacheFrom: ["${GAR_REPO}/chalk-ui-cache:ci_test"],
        dockerfile: 'ui/Dockerfile',   // path from repo root, not from inside context
        imageTag: "${GAR_REPO}/chalk-ui:${SANITIZED_BUILD_TAG}",
        target: 'js_app_prod',
        extraBuildArgs: "--build-arg sentryDsn=\$SENTRY_DSN",
        builderName: 'chalk-default',
        context: 'ui'
    )
    buildAndPushImage(
        garHost: GAR_HOST,
        cacheRef: "${GAR_REPO}/chalk-ui-cache:ci_test",
        additionalCacheFrom: ["${GAR_REPO}/chalk-ui-cache:ci_app"],
        dockerfile: 'ui/Dockerfile',
        imageTag: "${GAR_REPO}/chalk-ui-base:${SANITIZED_BUILD_TAG}",
        target: 'js_test_env',
        extraBuildArgs: "--build-arg sentryDsn=\$SENTRY_DSN",
        builderName: 'chalk-default',
        context: 'ui'
    )
}
```

Note: The second `buildAndPushImage` call re-runs the gcloud bootstrap inside the same
dind container. This is mildly wasteful but correct — the `docker buildx create ... || true`
in the function handles the already-existing builder gracefully.

After updating the stage, delete `jenkins/dockerHelper.groovy`.

Commit.

### Acceptance Criteria

- "Build UI" `steps` block contains exactly two `buildAndPushImage(...)` calls as shown
- `SENTRY_DSN` credential binding remains in the stage `environment {}` block
- `extraBuildArgs` uses `\$SENTRY_DSN` (shell-resolved, not Groovy-resolved)
- `git grep 'dockerHelper'` returns no matches anywhere in the repo
- `jenkins/dockerHelper.groovy` does not exist
- `make test` passes
- (Real verification is the next CI run after merge)
