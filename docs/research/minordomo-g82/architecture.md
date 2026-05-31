# Research: minordomo-g82 — Use jenkins-shared-library for dind bootstrap

## Key Files

- `Jenkinsfile` — Main CI pipeline (Build UI, Build Server, Integration Tests, CD)
- `jenkins/Jenkinsfile.base` — Separate Jenkins pipeline that builds and pushes `gcloud-helm:latest` from `jenkins/gcloud_helm.Dockerfile`
- `jenkins/gcloud_helm.Dockerfile` — Local Dockerfile for the helm image (gcloud-cli + kubectl + helm)
- `jenkins/dockerHelper.groovy` — ~12-line dind bootstrap helper (installs gcloud, authenticates, waits for docker)

## Current dind Stages

### Jenkinsfile.base — "Build Helm" stage
- Builds `${GAR_REPO}/gcloud-helm:latest` from `jenkins/gcloud_helm.Dockerfile`
- This is the "Build and Push Helm Image" stage the issue refers to
- This file only contains this one stage; deleting it entirely is appropriate

### Jenkinsfile — "Build UI" stage (jenkins-worker-dind.yml)
- Calls `dockerHelper.login(GAR_HOST)` for bootstrap
- Creates buildx builder `chalk-default`
- Builds TWO images in sequence:
  1. `chalk-ui:${SANITIZED_BUILD_TAG}` with `--target js_app_prod`, `--build-arg sentryDsn=...`, context `ui`
     - cache-to: `chalk-ui-cache:ci_app`
     - cache-from: `chalk-ui-cache:ci_app` AND `chalk-ui-cache:ci_test`
  2. `chalk-ui-base:${SANITIZED_BUILD_TAG}` with `--target js_test_env`, `--build-arg sentryDsn=...`, context `ui`
     - cache-to: `chalk-ui-cache:ci_test`
     - cache-from: `chalk-ui-cache:ci_app` AND `chalk-ui-cache:ci_test`

### Jenkinsfile — "Build Server" stage (jenkins-worker-dind.yml)
- Calls `dockerHelper.login(GAR_HOST)` for bootstrap
- Creates buildx builder `chalk-default`
- Builds ONE image: `chalk-server:${SANITIZED_BUILD_TAG}` with context `server`
  - cache-to/from: `chalk-server-cache:ci_server`
  - No `--build-arg` or `--target`

## buildAndPushImage Step (from gcp-setup)

Signature:
```groovy
buildAndPushImage(
    garHost: ...,       // required
    cacheRef: ...,      // required (single ref, used for both --cache-to and --cache-from)
    dockerfile: ...,    // required
    imageTag: ...,      // required
    builderName: ...,   // optional (default: 'default-builder')
    credentialsId: ..., // optional (default: 'jenkins-gke-sa')
    containerName: ..., // optional (default: 'dind')
)
```

The step always:
- Installs gcloud from scratch (full bootstrap)
- Uses `.` as the build context (hardcoded)
- Supports only ONE cache ref (same for cache-to and cache-from)
- Does NOT support `--build-arg`, `--target`, multiple cache-from refs, or custom build context

## Incompatibility with chalk's UI build

`buildAndPushImage` as currently designed cannot handle chalk's UI build because:
1. Context is hardcoded to `.` — UI build uses `ui` context
2. No `--build-arg` support — UI build needs `--build-arg sentryDsn=...`
3. No `--target` support — UI builds use `--target js_app_prod` and `--target js_test_env`
4. Single `cacheRef` — UI builds use multiple cross-build cache-from refs
5. Two images per stage — running full gcloud bootstrap twice per dind session is wasteful

The server build is also incompatible (uses `server` context), but only requires a `context` parameter to be added.

## Image Name Change

- Current Jenkinsfile uses `${GAR_REPO}/gcloud-helm:latest` for Jenkins-helm container
- gcp-setup's shared weekly build will publish as `jenkins-helm:latest`
- References in Integration Tests and CD stages need to be updated

## Cross-Repo Dependency

Task 1 (gcp-setup) must be merged and the weekly job run before this change is safe to merge.
The `buildAndPushImage` step in gcp-setup was designed for simple, single-image builds.
