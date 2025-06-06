# -*- mode: Python -*-
allow_k8s_contexts(os.environ.get('K8S_CONTEXT'))

GCP_PROJECT = os.environ.get('GCP_PROJECT')
env_arr = [
    'domain=chalk-dev.%s' % os.environ.get('ROOT_DOMAIN'),
    'environment=DEV',
    'gcpProject=%s' % GCP_PROJECT,
    'permittedUsers=%s' % os.environ.get('PERMITTED_USERS'),
    'server.dbPassword=%s' % os.environ.get('DB_PASSWORD'),
    'server.secretKey=%s' % os.environ.get('SECRET_KEY'),
    'useStarterData=true',
]

docker_build('us-east4-docker.pkg.dev/%s/default-gar/chalk-server' % GCP_PROJECT, 'server')
docker_build(
    'us-east4-docker.pkg.dev/%s/default-gar/chalk-ui' % GCP_PROJECT,
    'ui',
    build_args={'sentryDsn': os.environ.get('SENTRY_DSN')})
docker_build('us-east4-docker.pkg.dev/%s/default-gar/chalk-db-restorer' % GCP_PROJECT, 'misc_containers/db_restorer')

RANDOM_TAG = str(local('cat _env_id.txt || true')).strip()
if not RANDOM_TAG:
    RANDOM_TAG = str(local('date | shasum | head -c5')).strip()
    local('echo %s > _env_id.txt' % RANDOM_TAG)

RELEASE_NAME = 'chalk-dev-%s' % RANDOM_TAG
helm = helm('helm', name=RELEASE_NAME, namespace='dev', set=env_arr)
k8s_yaml(helm)
k8s_resource(objects=[
    '%s:ServiceAccount' % RELEASE_NAME,
    '%s:IAMServiceAccount' % RELEASE_NAME,
    '%s:IAMPolicy' % RELEASE_NAME,
    '%s-project-iam-policy:IAMPolicyMember' % RELEASE_NAME,
    '%s-db-backup-bucket-iam-policy:iampolicymember' % RELEASE_NAME,
], new_name='GCloud Svc Acct')
k8s_resource('%s-ui' % RELEASE_NAME, trigger_mode=TRIGGER_MODE_MANUAL)
# Make server depend on DB restorer to avoid foreign key constraint errors when restoring & DB migration conflicts
k8s_resource('%s-server' % RELEASE_NAME, resource_deps=['%s-db-restorer' % RELEASE_NAME])
k8s_resource('%s-db-restorer' % RELEASE_NAME)
k8s_resource(objects=['%s:ingress' % RELEASE_NAME], new_name='Ingress')

expo_env = {
    'DEBUG': 'true',
    'UI_ENVIRONMENT': 'DEV',
    'SENTRY_DSN': os.environ.get('SENTRY_DSN'),
}
local_resource('expo',
               serve_cmd='bash start.sh',
               serve_dir='ui',
               serve_env=expo_env,
               auto_init=False,
               trigger_mode=TRIGGER_MODE_MANUAL,
               readiness_probe=probe(
                  http_get=http_get_action(port=8081, path="/")
               ))
local_resource('local_nginx',
               serve_cmd='nginx -c %s/dev_nginx.conf' % os.getcwd(),
               deps='dev_nginx.conf',
               links=link('http://localhost:8080/', 'Chalk Web'),
               readiness_probe=probe(
                  http_get=http_get_action(port=8080, path="/healthz/")
               ))
