# Chalk - Todo app

## Env Setup
Copy .env_default to .env & .prod.env  
Set SECRET_KEY & DB_PASSWORD in .env  
  These should be random secure strings  
  e.g. head -c 32 /dev/urandom | base64  

## Allocate static IPs & create DNS entries
Explore doing this w/ Config Connector once [#101](https://github.com/GoogleCloudPlatform/k8s-config-connector/issues/101) is resolved.

```
PROJECT_NAME=<PROJECT_NAME>
ZONE_NAME=$PROJEC_NAME-dns
DOMAIN_NAME=<DOMAIN_NAME>

gcloud compute addresses create chalk-ip --global
gcloud compute addresses create chalk-dev-ip --global

DEV_IP=gcloud compute addresses describe chalk-dev-ip --global --format json | jq .address | tr -d '"'
PROD_IP=gcloud compute addresses describe chalk-ip --global --format json | jq .address | tr -d '"'

gcloud beta dns record-sets transaction start --zone=$ZONE_NAME
gcloud beta dns record-sets transaction add $DEV_IP --name=chalk-dev.$DOMAIN_NAME. --ttl=300 --type=A --zone=$ZONE_NAME
gcloud beta dns record-sets transaction add $PROD_IP --name=chalk.$DOMAIN_NAME. --ttl=1800 --type=A --zone=$ZONE_NAME
gcloud beta dns record-sets transaction execute --zone=$ZONE_NAME

```

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
