# Chalk - Todo app

## Install tools for dev env
On Mac:  
`brew install nginx`  
`brew install coreutils`  

## Env Setup
Copy .env_default to .env & .prod.env  

Set GCP_PROJECT with the project ID from GCP  
Set ROOT_DOMAIN with a domain such as `mydomain.com`  
Set PERMITTED_USERS to a list of emails who should be allowed to use the app  
Commas in PERMITTED_USERS should be double escaped like: bob@home.com\\,bill@home.com  

Set SECRET_KEY & DB_PASSWORD in .env  
  These should be random secure strings  
  e.g. `python -c "import secrets; print(secrets.token_urlsafe())"`  
  or `head -c 32 /dev/urandom | base64`  

Set K8S_CONTEXT to the name of the config from `kubectl config get-contexts` for the cluster that you plan to use.  

### Sentry config
Set SENTRY_DSN - A Sentry.io DSN.  https://sentry.io/settings/<ORG_ID>/projects/<PROJECT_ID>/keys/  
Set SENTRY_TOKEN (prod only) - A [Sentry.io auth token](https://sentry.io/settings/account/api/auth-tokens/)  

### Expo config
EXPO_USERNAME & EXPO_CLI_PASSWORD (prod only) - Set from your expo.dev account  
OAUTH_CLIENT_ID - See the OAuth Setup section below  

# Browserstack config
See username & access key under [Automate section of settings](https://www.browserstack.com/accounts/settings)  
Delete BROWSERSTACK_USERNAME & BROWSERSTACK_ACCESS_KEY in prod.env  

# CI OAuth config
See the OAuth Setup section below  
Delete CHALK_OAUTH_REFRESH_TOKEN in prod.env  

## Allocate static IPs & create DNS entries
Explore doing this w/ Config Connector once [#101](https://github.com/GoogleCloudPlatform/k8s-config-connector/issues/101) is resolved.

```
PROJECT_NAME=<PROJECT_NAME>
ZONE_NAME=$PROJECT_NAME-dns
DOMAIN_NAME=<DOMAIN_NAME>

gcloud compute addresses create chalk-ip --global
gcloud compute addresses create chalk-dev-ip --global

DEV_IP=$(gcloud compute addresses describe chalk-dev-ip --global --format json | jq .address | tr -d '"')
PROD_IP=$(gcloud compute addresses describe chalk-ip --global --format json | jq .address | tr -d '"')

gcloud beta dns record-sets transaction start --zone=$ZONE_NAME
gcloud beta dns record-sets transaction add $DEV_IP --name=chalk-dev.$DOMAIN_NAME. --ttl=300 --type=A --zone=$ZONE_NAME
gcloud beta dns record-sets transaction add $PROD_IP --name=chalk.$DOMAIN_NAME. --ttl=1800 --type=A --zone=$ZONE_NAME
gcloud beta dns record-sets transaction execute --zone=$ZONE_NAME

```

## Secrets: OAuth Setup
Create 2 [OAuth client IDs](https://console.cloud.google.com/apis/credentials)  
See [instructions](https://docs.expo.dev/guides/authentication/#google)  

1) for Web  
Name: chalk-dev-web  
Authorized URIs:  
- http://chalk.flipperkid.com  
- http://chalk-dev.flipperkid.com  
- http://localhost:8080  
Authorized redirect URIs:   
- http://chalk.flipperkid.com/api/todos/auth_callback/  
- http://chalk-dev.flipperkid.com/api/todos/auth_callback/  
- http://localhost:8080/api/todos/auth_callback/  

Download the client ID / secret as JSON and place at helm/secrets/oauth_web_client_secret.json  
and continuous_delivery_setup/secrets/oauth_web_client_secret.json  
Also set OAUTH_CLIENT_ID to the client ID in .env & .prod.env

2) OAuth refresh token for Playwright tests
Also run a dev server and login using a tester account to capture the refresh token for Jenkins integration tests to use.  
Fill in CHALK_OAUTH_REFRESH_TOKEN in .env  
Generating this token is tricky since it is never sent to the browser.  
See oauth.py and look for a print statement to uncomment in the \_get_authorized_session method.  
Also edit the get_authorization_url function to pass access_type='offline' in the flow.authorization_url call.  
A final gotcha is the refresh token will only be returned when the app is initially authorized.  
Visit https://myaccount.google.com/u/0/permissions to revoke authorization.  

3) for Android (staging & prod)  
Name: chalk-prod-android  
Package Name: com.<DOMAIN_NAME w/o .com>.chalk  
SHA-1 Certificate Fingerprint: get from running `npx eas credentials` in ui/js directory  

4) for Android (dev)  
Name: chalk-dev-android  
Package Name: com.<DOMAIN_NAME w/o .com>.chalk.dev  
SHA-1 Certificate Fingerprint: get from running `npx eas credentials` in ui/js directory  

## Setup Jenkins Builds
Run `make setup-continuous-delivery` to add the secrets needed for builds and continuous delivery  
to Jenkins.

### Chalk Build
Create a Multibranch Pipeline build named `chalk`  
Set the Display Name to `Chalk`

Add source Github  
Set repository URL to `https://github.com/wcjordan/chalk`  
Set credentials to Github app.  
Ensure the Github app has permissions on the repo under its installation configuration.  

Delete `Discover pull requests from forks` from the Behaviors  
Ensure Behaviors has:  
- `Discover branches`: `Exclude branches that are also filed as PRs`
- `Discover pull requests from origin`: `The current pull request revision`

Build by Jenkinsfile  
Set Scan Periodically to `1 hour`.  The webhook will handle building on pushes & PRs.  
Discard old builds, keep `60` days of old items.  

### Chalk Base Build
Create a Pipeline build named `chalk_base`
Set the Display Name to `Chalk Base` (under Advanced)

Enable `Discard old builds`, set max # of builds to keep to `50`.  
Enable `Build periodically`, set schedule to `H 0 * * 0`.  

Set Pipeline config as `Pipeline script from SCM`.  
Set SCM to git w/ URL `https://github.com/wcjordan/chalk`.  

Update the branch to build to `*/main`.  
Use `Add Branch` under Branch Specifier and set it to `*/jenkins-base`.  
This means a `jenkins-base` branch can be use to create a new base build in addition to `master`.  

Set script path to `jenkins/Jenkinsfile.base`  
Enable lightweight checkout  

### Add Github Webhook
Under the repo settings on Github -> Webhooks, click `Add a webhook``
Payload URL: `http://jenkins.flipperkid.com/github-webhook/`
Content type: `application/json`
Which events...?: `Just the push event`
