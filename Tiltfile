# -*- mode: Python -*-
allow_k8s_contexts(os.environ.get('K8S_CONTEXT'))

GCP_PROJECT = os.environ.get('GCP_PROJECT')
env_arr = [
    'domain=chalk-dev.%s' % os.environ.get('ROOT_DOMAIN'),
    'environment=DEV',
    'gcpProject=%s' % GCP_PROJECT,
    'server.dbPassword=%s' % os.environ.get('DB_PASSWORD'),
    'server.djangoEmail=%s' % os.environ.get('DJANGO_EMAIL'),
    'server.djangoPassword=%s' % os.environ.get('DJANGO_PASSWORD'),
    'server.djangoUsername=%s' % os.environ.get('DJANGO_USERNAME'),
    'server.secretKey=%s' % os.environ.get('SECRET_KEY'),
]

docker_build('gcr.io/%s/chalk-server' % GCP_PROJECT, 'server')
docker_build(
    'gcr.io/%s/chalk-ui' % GCP_PROJECT,
    'ui',
    build_args={'GCP_PROJECT': GCP_PROJECT})

RANDOM_TAG = str(local('cat _env_id.txt || true')).strip()
if not RANDOM_TAG:
    RANDOM_TAG = str(local('date | shasum | head -c5')).strip()
    local('echo %s > _env_id.txt' % RANDOM_TAG)

RELEASE_NAME = 'chalk-dev-%s' % RANDOM_TAG
helm = helm('helm', name=RELEASE_NAME, set=env_arr)
k8s_yaml(helm)
