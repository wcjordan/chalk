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
helm = helm('helm', set=env_arr)
k8s_yaml(helm)
k8s_resource('chart-chalk', port_forwards=8283)
