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
                container('bumper') {
                    sh '''
                        set -euo pipefail

                        pip install --quiet pur

                        curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
                          | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
                        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
                          | tee /etc/apt/sources.list.d/github-cli.list > /dev/null
                        apt-get update -qq && apt-get install -y -qq gh

                        export GH_TOKEN="${GH_APP_PSW}"
                        gh auth setup-git

                        git config user.email "jenkins@minordomo"
                        git config user.name "Jenkins"

                        bash jenkins/bump-python-deps.sh
                    '''
                }
            }
        }
    }
    post {
        failure { notifyFailure() }
    }
}
