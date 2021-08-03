# Chalk - Todo app

## Setup
Copy .env_default to .env & .prod.env
Set SECRET_KEY & POSTGRES_PASSWORD in .env
  These should be random secure strings
  e.g. head -c 32 /dev/urandom | base64

To prevent docker conflicting with the corporate subnet
As root, create /etc/docker/daemon.json with the content
{
  "bip": "10.1.10.1/24"
}

## TODO
Add instructions for other env setup
Add setup instructions for static IP claim


## Setup Jenkins Builds
### Chalk Build
Repository URL `https://github.com/wcjordan/chalk`
Select Github Credentials

Build by Jenkinsfile
Scan every 1 day if not otherwise run
Discard old builds, keep max of 5 old items

### Chalk Base Build
Enable `Discard old builds`, set max # of builds to keep to `50`.
Enable `Build periodically`, set schedule to `H 0 * * 0`.

Set Pipeline config as `Pipeline script from SCM`.
Set SCM to git w/ URL `https://github.com/wcjordan/chalk`.
Set credentials to your github credentials.

Use `Add Branch` under Branch Specifier and set it to `*/jenkins`.
This means a jenkins branch can be use to create a new base build.

Set script path to `Jenkinsfile.base`
Enable lightweight checkout
