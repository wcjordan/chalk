# -*- mode: Python -*-

allow_k8s_contexts (['docker-desktop'])

env = read_yaml('.env')
env_arr = ['env.{}={}'.format(key, val) for key, val in env.items()]

load('ext://helm_remote', 'helm_remote')
helm_remote('postgresql',
            repo_name='bitnami',
            repo_url='https://charts.bitnami.com/bitnami',
            set=['postgresqlPassword=cG9zdGdyZXM=%', 'postgresqlDatabase=chalk'])

docker_build('chalk-server-image', 'server')
docker_build('chalk-ui-image', 'ui')
helm = helm('helm', name='chart-chalk', set=env_arr)
k8s_yaml(helm)
# k8s_resource('chart-chalk-server', port_forwards=8283)
k8s_resource('chart-chalk-ui', port_forwards='8080')
