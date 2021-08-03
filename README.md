# Chalk - Todo app

## Setup
Copy .env_default to .env & .prod.env
Set SECRET_KEY & POSTGRES_PASSWORD in .env
  These should be random secure strings
  e.g. head -c 32 /dev/urandom | base64

## Setup Jenkins Builds
### Chalk Build
Create a Multibranch Pipeline build named `Chalk`

Add source Github
Set repository URL to `https://github.com/wcjordan/chalk`

Delete the Behaviors and just add 1 for Discover Branches set to `All Branches`

Build by Jenkinsfile
Set Scan Periodically to `1 day`
Discard old builds, keep max of 5 old items

### Chalk Base Build
Create a Pipeline build named `Chalk Base`

Enable `Discard old builds`, set max # of builds to keep to `50`.
Enable `Build periodically`, set schedule to `H 0 * * 0`.

Set Pipeline config as `Pipeline script from SCM`.
Set SCM to git w/ URL `https://github.com/wcjordan/chalk`.

Use `Add Branch` under Branch Specifier and set it to `*/jenkins`.
This means a jenkins branch can be use to create a new base build.

Set script path to `Jenkinsfile.base`
Enable lightweight checkout

## TODO
Add instructions for other env setup
Add setup instructions for static IP claim
