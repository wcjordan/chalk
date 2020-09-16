# -*- mode: Python -*-

allow_k8s_contexts('kind-kind-jordan')

POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
POSTGRES_DB = os.environ.get('POSTGRES_DB')
env_arr = [
    'env.SECRET_KEY=%s' % os.environ.get('SECRET_KEY'),
    'env.GUNICORN_WORKERS=%s' % os.environ.get('GUNICORN_WORKERS'),
    'env.POSTGRES_DB=%s' % POSTGRES_DB,
    'env.POSTGRES_USER=%s' % os.environ.get('POSTGRES_USER'),
    'env.POSTGRES_PASSWORD=%s' % POSTGRES_PASSWORD,
    'env.DB_HOSTNAME=%s' % os.environ.get('DB_HOSTNAME'),
    'env.DB_PORT=%s' % os.environ.get('DB_PORT'),
    'env.PG_SHARED_BUFFERS=%s' % os.environ.get('PG_SHARED_BUFFERS'),
    'env.PG_EFFECTIVE_CACHE_SIZE=%s' % os.environ.get('PG_EFFECTIVE_CACHE_SIZE'),
]

k8s_yaml(local('helm template ingress stable/nginx-ingress')) #, quiet=True))

load('ext://helm_remote', 'helm_remote')
helm_remote('postgresql',
            repo_name='bitnami',
            repo_url='https://charts.bitnami.com/bitnami',
            set=['postgresqlPassword=%s' % POSTGRES_PASSWORD,
                 'postgresqlDatabase=%s' % POSTGRES_DB])

docker_build('chalk-server-image', 'server')
docker_build('chalk-ui-image', 'ui', dockerfile='ui/Dockerfile.dev', live_update=[
    fall_back_on(['ui/js/package.json', 'ui/js/yarn.lock']),
    sync('ui/js/public', '/js/public'),
    sync('ui/js/src', '/js/src'),
])

helm = helm('helm', name='chart-chalk', set=env_arr)
k8s_yaml(helm)
k8s_resource('ingress-nginx-ingress-controller', port_forwards='8000')
