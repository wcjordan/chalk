@Library('jenkins-shared-library') _

pipeline {
    agent none
    options {
        timestamps()
        disableConcurrentBuilds()
    }
    triggers {
        cron(env.BRANCH_NAME == 'main' ? 'H H * * 1' : '')
    }
    stages {
        stage('Bump Python Deps') {
            agent {
                kubernetes {
                    yaml """
                        apiVersion: v1
                        kind: Pod
                        spec:
                          containers:
                          - name: bumper
                            image: python:3.12-bookworm
                            command:
                            - cat
                            tty: true
                    """
                }
            }
            environment {
                GH_APP = credentials('github-app')
            }
            options {
                timeout(time: 30, unit: 'MINUTES')
            }
            steps {
                checkout scm
                container('bumper') {
                    sh '''
                        bash jenkins/bump-python-deps.sh
                    '''
                }
            }
        }
    }
}
