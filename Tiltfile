# -*- mode: Python -*-

allow_k8s_contexts('kind-kind-jordan')

env = read_yaml('.env')
env_arr = ['env.{}={}'.format(key, val) for key, val in env.items()]

k8s_yaml(local('helm template ingress stable/nginx-ingress')) #, quiet=True))

load('ext://helm_remote', 'helm_remote')
helm_remote('postgresql',
            repo_name='bitnami',
            repo_url='https://charts.bitnami.com/bitnami',
            set=['postgresqlPassword=cG9zdGdyZXM=%', 'postgresqlDatabase=chalk'])

docker_build('chalk-server-image', 'server')
docker_build('chalk-ui-image', 'ui', dockerfile='ui/Dockerfile.dev', live_update=[
    fall_back_on(['ui/js/package.json', 'ui/js/yarn.lock']),
    sync('ui/js/public', '/js_app/public'),
    sync('ui/js/src', '/js_app/src'),
])

helm = helm('helm', name='chart-chalk', set=env_arr)
k8s_yaml(helm)
k8s_resource('ingress-nginx-ingress-controller', port_forwards='8000')
