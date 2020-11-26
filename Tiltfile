# -*- mode: Python -*-

allow_k8s_contexts('kind-kind-jordan')

POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
env_arr = [
    'server.secretKey=%s' % os.environ.get('SECRET_KEY'),
    'server.dbPassword=%s' % POSTGRES_PASSWORD,
    'DEV=true',
]

k8s_yaml(local('helm template ingress stable/nginx-ingress', quiet=True))

load('ext://helm_remote', 'helm_remote')
helm_remote('postgresql',
            repo_name='bitnami',
            repo_url='https://charts.bitnami.com/bitnami',
            set=['postgresqlPassword=%s' % POSTGRES_PASSWORD,
                 'postgresqlDatabase=chalk'])

docker_build('gcr.io/flipperkid-default/chalk-server-image', 'server')
docker_build('gcr.io/flipperkid-default/chalk-ui-image-dev', 'ui', dockerfile='ui/Dockerfile.dev', live_update=[
    fall_back_on(['ui/js/package.json', 'ui/js/yarn.lock']),
    sync('ui/js/public', '/js/public'),
    sync('ui/js/src', '/js/src'),
])

helm = helm('helm', name='chart-chalk', set=env_arr)
k8s_yaml(helm)
k8s_resource('ingress-nginx-ingress-controller', port_forwards='8000')
