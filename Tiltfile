# -*- mode: Python -*-

allow_k8s_contexts(os.environ.get('K8S_CONTEXT'))

POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
env_arr = [
    'server.secretKey=%s' % os.environ.get('SECRET_KEY'),
    'server.dbPassword=%s' % POSTGRES_PASSWORD,
    'ui.sentryDsn=%s' % os.environ.get('SENTRY_DSN'),
    'ui.sentryToken=%s' % os.environ.get('SENTRY_TOKEN'),
    'DEV=true',
]

docker_build('gcr.io/flipperkid-default/chalk-server-image', 'server')
docker_build('gcr.io/flipperkid-default/chalk-ui-image-dev', 'ui', dockerfile='ui/Dockerfile.dev', live_update=[
    fall_back_on(['ui/js/package.json', 'ui/js/yarn.lock']),
    sync('ui/js/public', '/js/public'),
    sync('ui/js/src', '/js/src'),
])

helm = helm('helm', name='chalk-dev', set=env_arr)
k8s_yaml(helm)
k8s_resource('chalk-dev-ui', port_forwards=['19002'], pod_readiness='ignore')
