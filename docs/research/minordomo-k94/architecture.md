# Research: Add Jenkins Job to Bump Python Deps (minordomo-k94)

## Issue Summary

Weekly Jenkins job to bump Python deps via `pur` across three directories:
- `/server` — `requirements.txt` + `dev-requirements.txt`
- `/test_gen` — `requirements.txt` + `dev-requirements.txt`
- `/tests` — `requirements.txt` only, skip `playwright`

## Existing Requirements Files

### server/requirements.txt
```
Django==6.0.7, djangorestframework==3.17.1, django-simple-history==3.12.0,
google-auth-oauthlib==1.4.0, google-cloud-storage==3.12.1, gunicorn==26.0.0,
psycopg2-binary==2.9.12, requests==2.34.2
```

### server/dev-requirements.txt
```
-r requirements.txt
flake8==7.3.0, pylint==4.0.6, pylint-django==2.8.0, pytest==9.1.1, yapf==0.43.0
```

### test_gen/requirements.txt
```
google-cloud-storage==3.12.1, PyYAML==6.0.3
```

### test_gen/dev-requirements.txt
```
-r requirements.txt
black==26.5.1, flake8==7.3.0, pylint==4.0.6, pytest==9.1.1, pytest-cov==7.1.0, syrupy==5.5.3
```

### tests/requirements.txt
```
pytest==9.1.1, playwright==1.52.0
```
(playwright must be skipped with `pur --skip playwright`)

## Existing Jenkins Infrastructure

- `jenkins/jenkins-worker-python.yml` — pod spec using `python:3.12-bookworm`
- `Jenkinsfile` — main build/test/deploy pipeline, uses `@Library('jenkins-shared-library') _`
- `notifyFailure()` — available from the globally configured Jenkins shared library

## Credential Pattern

From minordomo `shared/setup-env.sh`: `GH_APP` credential is username-password type.
- `GH_APP_USR` = GitHub app username/email
- `GH_APP_PSW` = GitHub token (used as `GH_TOKEN`)
- After setting `GH_TOKEN`, run `gh auth setup-git` to configure git HTTPS credentials

## gh CLI Installation

`python:3.12-bookworm` does not include `gh` CLI. Install at runtime via official GitHub apt repo:
```bash
mkdir -p -m 755 /etc/apt/keyrings
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    | dd of=/etc/apt/keyrings/githubcli-archive-keyring.gpg
chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
    | tee /etc/apt/sources.list.d/github-cli.list > /dev/null
apt-get update -qq && apt-get install -y -qq gh
```

## Files to Create

1. `jenkins/bump-python-deps.Jenkinsfile` — Weekly cron pipeline definition
2. `jenkins/bump-python-deps.sh` — Script: runs pur, creates branch, opens PR

## Cron Pattern

Following the librarian job pattern: `cron(env.BRANCH_NAME == 'main' ? 'H H * * 1' : '')`
(weekly, Mondays; only fires on the main branch of a multibranch pipeline)

## pur Commands Per Directory

```bash
# server
(cd server && pur -r requirements.txt && pur -r dev-requirements.txt)

# test_gen
(cd test_gen && pur -r requirements.txt && pur -r dev-requirements.txt)

# tests — skip playwright
(cd tests && pur --skip playwright -r requirements.txt)
```

## No Existing Precedent

This is the first chalk-specific scheduled job. The chalk repo has no scheduled pipeline.
The job does not go in minordomo/shared since it operates on chalk.
