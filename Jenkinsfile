def GAR_HOST = 'us-east4-docker.pkg.dev'
def GAR_REPO = "${GAR_HOST}/${env.GCP_PROJECT}/default-gar"

def SERVER_IP = null
def HELM_DEPLOY_NAME = null

pipeline {
    agent none
    options {
        timestamps()
        disableConcurrentBuilds()
    }
    stages {
        stage('Init') {
            agent {
                kubernetes {
                    yamlFile 'jenkins/jenkins-worker-python.yml'
                }
            }
            steps {
                script {
                    SANITIZED_BUILD_TAG = env.BUILD_TAG.replaceAll(/[^a-zA-Z0-9_\-]/, '_')
                }
            }
        }
        stage('Build') {
            parallel {
                stage('UI') {
                    stages {
                        stage('Build UI') {
                            agent {
                                kubernetes {
                                    yamlFile 'jenkins/jenkins-worker-dind.yml'
                                }
                            }
                            options {
                                timeout(time: 20, unit: 'MINUTES')
                            }
                            environment {
                                SENTRY_DSN = credentials('chalk-prod-cd-sentry-dsn')
                            }
                            steps {
                                container('dind') {
                                    script {
                                        def dockerHelper = load "jenkins/dockerHelper.groovy"
                                        dockerHelper.login(GAR_HOST)
                                    }
                                    sh """
                                        export PATH="/root/google-cloud-sdk/bin:\$PATH"
                                        docker buildx create --driver docker-container --name chalk-default --use
                                        docker buildx build --push \
                                            --cache-to type=registry,ref=${GAR_REPO}/chalk-ui-cache:ci_app,mode=max \
                                            --cache-from type=registry,ref=${GAR_REPO}/chalk-ui-cache:ci_app \
                                            --cache-from type=registry,ref=${GAR_REPO}/chalk-ui-cache:ci_test \
                                            --build-arg sentryDsn=\$SENTRY_DSN \
                                            -t ${GAR_REPO}/chalk-ui:${SANITIZED_BUILD_TAG} \
                                            --target js_app_prod \
                                            ui

                                        docker buildx build --push \
                                            --cache-to type=registry,ref=${GAR_REPO}/chalk-ui-cache:ci_test,mode=max \
                                            --cache-from type=registry,ref=${GAR_REPO}/chalk-ui-cache:ci_app \
                                            --cache-from type=registry,ref=${GAR_REPO}/chalk-ui-cache:ci_test \
                                            --build-arg sentryDsn=\$SENTRY_DSN \
                                            -t ${GAR_REPO}/chalk-ui-base:${SANITIZED_BUILD_TAG} \
                                            --target js_test_env \
                                            ui
                                    """
                                }
                            }
                        }
                        stage('Test UI') {
                            agent {
                                kubernetes {
                                    yaml """
                                        apiVersion: v1
                                        kind: Pod
                                        spec:
                                          containers:
                                          - name: jenkins-worker-ui
                                            image: ${GAR_REPO}/chalk-ui-base:${SANITIZED_BUILD_TAG}
                                            command:
                                            - cat
                                            tty: true
                                            resources:
                                              requests:
                                                cpu: "600m"
                                                memory: "3Gi"
                                              limits:
                                                cpu: "1000m"
                                                memory: "3Gi"
                                    """
                                }
                            }
                            options {
                                timeout(time: 10, unit: 'MINUTES')
                            }
                            steps {
                                container('jenkins-worker-ui') {
                                    sh '''
                                        JENKINS_WORKSPACE=$(pwd)
                                        cp ui/Makefile /workspace/
                                        cd /workspace
                                        make test

                                        cd $JENKINS_WORKSPACE
                                        cp /workspace/js/junit.xml .
                                    '''
                                    junit testResults: 'junit.xml'
                                }
                            }
                        }
                        stage('Test UI Storybook') {
                            agent {
                                kubernetes {
                                    yaml """
                                        apiVersion: v1
                                        kind: Pod
                                        spec:
                                          containers:
                                          - name: jenkins-worker-storybook
                                            image: ${GAR_REPO}/chalk-ui-base:${SANITIZED_BUILD_TAG}
                                            command: ["/bin/sh", "-c"]
                                            args:
                                            - cd js && npx http-server -p 9009 /workspace/js/storybook-static
                                            tty: true
                                            ports:
                                            - containerPort: 9009
                                            resources:
                                              requests:
                                                cpu: "200m"
                                                memory: "500Mi"
                                              limits:
                                                cpu: "500m"
                                                memory: "500Mi"
                                          - name: jenkins-worker-storybook-snapshots
                                            image: ${GAR_REPO}/chalk-ui-base:${SANITIZED_BUILD_TAG}
                                            command:
                                            - cat
                                            tty: true
                                            resources:
                                              requests:
                                                cpu: "400m"
                                                memory: "2Gi"
                                              limits:
                                                cpu: "1000m"
                                                memory: "2Gi"
                                    """
                                }
                            }
                            options {
                                timeout(time: 10, unit: 'MINUTES')
                            }
                            steps {
                                container('jenkins-worker-storybook-snapshots') {
                                    sh '''
                                        JENKINS_WORKSPACE=$(pwd)
                                        cp ui/Makefile /workspace/
                                        cd /workspace
                                        make test-storybook-inner TEST_ARGS="--junit --url http://127.0.0.1:9009"

                                        cd $JENKINS_WORKSPACE
                                        cp /workspace/js/junit.xml .
                                    '''
                                    junit testResults: 'junit.xml'
                                }
                            }
                        }
                    }
                }
                stage('Server') {
                    stages {
                        stage('Build Server') {
                            agent {
                                kubernetes {
                                    yamlFile 'jenkins/jenkins-worker-dind.yml'
                                }
                            }
                            options {
                                timeout(time: 10, unit: 'MINUTES')
                            }
                            steps {
                                container('dind') {
                                    script {
                                        def dockerHelper = load "jenkins/dockerHelper.groovy"
                                        dockerHelper.login(GAR_HOST)
                                    }
                                    sh """
                                        export PATH="/root/google-cloud-sdk/bin:\$PATH"
                                        docker buildx create --driver docker-container --name chalk-default --use
                                        docker buildx build --push \
                                            --cache-to type=registry,ref=${GAR_REPO}/chalk-server-cache:ci_server,mode=max \
                                            --cache-from type=registry,ref=${GAR_REPO}/chalk-server-cache:ci_server \
                                            -t ${GAR_REPO}/chalk-server:${SANITIZED_BUILD_TAG} \
                                            server
                                    """
                                }
                            }
                        }
                        stage('Test Server') {
                            agent {
                                kubernetes {
                                    yamlFile 'jenkins/jenkins-worker-python.yml'
                                }
                            }
                            options {
                                timeout(time: 10, unit: 'MINUTES')
                            }
                            steps {
                                container('jenkins-worker-python') {
                                    dir('server') {
                                        sh 'pip install --no-cache-dir -r dev-requirements.txt'
                                        sh 'env $(grep -v "^#" ../.env_default | xargs) DOMAIN=localhost SECRET_KEY=testkey make test'
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        stage('Integration Tests') {
            agent {
                kubernetes {
                    yaml """
                        apiVersion: v1
                        kind: Pod
                        spec:
                          containers:
                          - name: jenkins-helm
                            image: ${GAR_REPO}/gcloud-helm:latest
                            command:
                            - cat
                            tty: true
                            resources:
                              requests:
                                cpu: "600m"
                                memory: "1Gi"
                              limits:
                                cpu: "1000m"
                                memory: "1Gi"
                          - name: jenkins-worker-python
                            image: python:3.10
                            command:
                            - cat
                            tty: true
                            resources:
                              requests:
                                cpu: "600m"
                                memory: "1.5Gi"
                              limits:
                                cpu: "1000m"
                                memory: "1.5Gi"
                    """
                }
            }
            options {
                throttle(['chalk-ci'])
            }
            stages {
                stage('Deploy Integration Server') {
                    options {
                        timeout(time: 10, unit: 'MINUTES')
                    }
                    steps {
                        container('jenkins-helm') {
                            withCredentials([
                                file(credentialsId: 'jenkins-gke-sa', variable: 'GKE_SA_FILE'),
                                file(credentialsId: 'chalk-prod-cd-oauth-web-client-json', variable: 'OAUTH_WEB_SECRET')
                            ]) {
                                sh 'gcloud auth activate-service-account --key-file $GKE_SA_FILE'
                                sh "gcloud container clusters get-credentials ${env.GCP_PROJECT_NAME}-gke --project ${env.GCP_PROJECT} --zone us-east4-c"
                                script {
                                    HELM_DEPLOY_NAME = sh (
                                        script: """#!/bin/bash
                                            set -x
                                            parts=(\$(echo ${SANITIZED_BUILD_TAG} | tr _- "\n"))
                                            part_len=\$(echo \${#parts[@]})
                                            branch_part=\$(echo "\${parts[@]:2:\$part_len-3}" | tr " " - | head -c 12)
                                            echo \${parts[0]}-\${parts[1]}-\$branch_part-\${parts[-1]}
                                        """,
                                        returnStdout: true
                                    ).trim().toLowerCase()
                                }
                                sh """
                                    mkdir helm/secrets;
                                    cp \$OAUTH_WEB_SECRET helm/secrets/oauth_web_client_secret.json
                                    helm install \
                                        --namespace test \
                                        --set domain=chalk-ci.${env.ROOT_DOMAIN} \
                                        --set environment=CI \
                                        --set gcpProject=${env.GCP_PROJECT} \
                                        --set imageTag=${SANITIZED_BUILD_TAG} \
                                        --set permittedUsers=flipperkid.tester@gmail.com \
                                        --set server.dbPassword=\$(head -c 32 /dev/urandom | base64) \
                                        --set server.secretKey=\$(head -c 32 /dev/urandom | base64) \
                                        ${HELM_DEPLOY_NAME} helm
                                    """
                                sh """
                                    until [ ! -z \$ready_replicas ] && [ \$ready_replicas -ge 1 ]
                                    do
                                        sleep 15
                                        ready_replicas=\$(kubectl --namespace test get deployments ${HELM_DEPLOY_NAME}-server -o jsonpath='{.status.readyReplicas}')
                                    done

                                    until [ ! -z \$todos_ready ] && [ \$todos_ready -eq 200 ]
                                    do
                                        sleep 15
                                        todos_ready=\$(curl -o /dev/null -Isw '%{http_code}' https://chalk-ci.${env.ROOT_DOMAIN}/api/todos/healthz/ || true)
                                    done

                                    until [ ! -z \$html_ready ] && [ \$html_ready -eq 302 ]
                                    do
                                        sleep 5
                                        html_ready=\$(curl -o /dev/null -Isw '%{http_code}' https://chalk-ci.${env.ROOT_DOMAIN}/ || true)
                                    done
                                """
                            }
                        }
                    }
                }
                stage('Playwright Tests') {
                    options {
                        timeout(time: 20, unit: 'MINUTES')
                    }
                    steps {
                        browserstack(credentialsId: 'browserstack_key') {
                            container('jenkins-worker-python') {
                                withCredentials([
                                    string(credentialsId: 'chalk-prod-cd-oauth-refresh-token', variable: 'CHALK_OAUTH_REFRESH_TOKEN'),
                                ]) {
                                    dir('tests') {
                                        sh 'pip install "playwright==1.50.0" "pytest==8.3.5"'
                                        sh "pytest . --server_domain chalk-ci.${env.ROOT_DOMAIN} --junitxml=playwright_results.xml || true"

                                        junit testResults: 'playwright_results.xml'
                                        browserStackReportPublisher 'automate'
                                    }
                                }
                            }
                        }
                    }
                }
            }
            post {
                always {
                    container('jenkins-helm') {
                        withCredentials([file(credentialsId: 'jenkins-gke-sa', variable: 'FILE')]) {
                            sh 'gcloud auth activate-service-account --key-file $FILE'
                            sh 'gcloud container clusters get-credentials ${GCP_PROJECT_NAME}-gke --project ${GCP_PROJECT} --zone us-east4-c'
                            sh "helm uninstall --namespace test ${HELM_DEPLOY_NAME}"
                        }
                    }
                }
            }
        }
        stage('Continuous Deployment') {
            agent {
                kubernetes {
                    yaml """
                        apiVersion: v1
                        kind: Pod
                        spec:
                          containers:
                          - name: jenkins-helm
                            image: ${GAR_REPO}/gcloud-helm:latest
                            command:
                            - cat
                            tty: true
                            resources:
                              requests:
                                cpu: "600m"
                                memory: "1Gi"
                              limits:
                                cpu: "1000m"
                                memory: "1Gi"
                    """
                }
            }
            when {
                branch 'main'
                beforeAgent true
            }
            stages {
                stage('Deploy K8s') {
                    options {
                        timeout(time: 10, unit: 'MINUTES')
                    }
                    environment {
                        DB_PASSWORD = credentials('chalk-prod-cd-server-db-password')
                        PERMITTED_USERS = credentials('chalk-prod-cd-permitted-users')
                        SECRET_KEY = credentials('chalk-prod-cd-server-secret-key')
                    }
                    steps {
                        container('jenkins-helm') {
                            withCredentials([
                                file(credentialsId: 'jenkins-gke-sa', variable: 'GKE_SA_FILE'),
                                file(credentialsId: 'chalk-prod-cd-oauth-web-client-json', variable: 'OAUTH_WEB_SECRET')
                            ]) {
                                sh 'gcloud auth activate-service-account --key-file $GKE_SA_FILE'
                                sh "gcloud container clusters get-credentials ${env.GCP_PROJECT_NAME}-gke --project ${env.GCP_PROJECT} --zone us-east4-c"

                                sh """
                                    mkdir helm/secrets;
                                    cp \$OAUTH_WEB_SECRET helm/secrets/oauth_web_client_secret.json
                                    helm upgrade --install \
                                        --namespace default \
                                        --set domain=chalk.${env.ROOT_DOMAIN} \
                                        --set environment=PROD \
                                        --set gcpProject=${env.GCP_PROJECT} \
                                        --set imageTag=${SANITIZED_BUILD_TAG} \
                                        --set permittedUsers=\$PERMITTED_USERS \
                                        --set server.dbPassword=\$DB_PASSWORD \
                                        --set server.secretKey=\$SECRET_KEY \
                                        chalk-prod helm
                                    """
                                sh """
                                    until [ ! -z \$ready_replicas ] && [ \$ready_replicas -ge 1 ]
                                    do
                                        sleep 15
                                        ready_replicas=\$(kubectl --namespace default get deployments chalk-prod-server -o jsonpath='{.status.readyReplicas}')
                                    done

                                    until [ ! -z \$todos_ready ] && [ \$todos_ready -eq 200 ]
                                    do
                                        sleep 15
                                        todos_ready=\$(curl -o /dev/null -Isw '%{http_code}' https://chalk.${env.ROOT_DOMAIN}/api/todos/healthz/ || true)
                                    done

                                    until [ ! -z \$html_ready ] && [ \$html_ready -eq 302 ]
                                    do
                                        sleep 5
                                        html_ready=\$(curl -o /dev/null -Isw '%{http_code}' https://chalk.${env.ROOT_DOMAIN}/ || true)
                                    done
                                """
                            }
                        }
                    }
                }
            }
        }
    }
}
