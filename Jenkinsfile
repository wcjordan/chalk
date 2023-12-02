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
                                timeout(time: 15, unit: 'MINUTES')
                            }
                            steps {
                                container('dind') {
                                    script {
                                        def dockerHelper = load "jenkins/dockerHelper.groovy"
                                        dockerHelper.login(GAR_HOST)
                                    }
                                    sh """
                                        export PATH="/root/google-cloud-sdk/bin:\$PATH"
                                        docker buildx create --driver docker-container --name chalk-default
                                        docker buildx use chalk-default
                                        docker buildx build --push \
                                            --cache-to type=registry,ref=${GAR_REPO}/chalk-ui,mode=max \
                                            --cache-from type=registry,ref=${GAR_REPO}/chalk-ui \
                                            -t ${GAR_REPO}/chalk-ui:${env.BUILD_TAG} \
                                            ui

                                        docker buildx build --push \
                                            --cache-to type=registry,ref=${GAR_REPO}/chalk-ui,mode=max \
                                            --cache-from type=registry,ref=${GAR_REPO}/chalk-ui \
                                            -t ${GAR_REPO}/chalk-ui-base:${env.BUILD_TAG} \
                                            --target base \
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
                                            image: ${GAR_REPO}/chalk-ui-base:${env.BUILD_TAG}
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
                                    dir('ui/js') {
                                        sh 'cp -r /js/node_modules .'
                                    }
                                    dir('ui') {
                                        sh 'make test'
                                        junit testResults: 'js/junit.xml'
                                    }
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
                                        docker buildx create --driver docker-container --name chalk-default
                                        docker buildx use chalk-default
                                        docker buildx build --push \
                                            --cache-to type=registry,ref=${GAR_REPO}/chalk-server,mode=max \
                                            --cache-from type=registry,ref=${GAR_REPO}/chalk-server \
                                            -t ${GAR_REPO}/chalk-server:${env.BUILD_TAG} \
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
                                sh "gcloud auth activate-service-account --key-file \$GKE_SA_FILE"
                                sh "gcloud container clusters get-credentials ${env.GCP_PROJECT_NAME}-gke --project ${env.GCP_PROJECT} --zone us-east4-c"
                                script {
                                    HELM_DEPLOY_NAME = sh (
                                        script: """#!/bin/bash
                                            set -x
                                            parts=(\$(echo ${env.BUILD_TAG} | tr _- "\n"))
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
                                        --set domain=_ \
                                        --set environment=CI \
                                        --set gcpProject=${env.GCP_PROJECT} \
                                        --set imageTag=${env.BUILD_TAG} \
                                        --set permittedUsers=flipperkid.tester@gmail.com \
                                        --set server.dbPassword=\$(head -c 32 /dev/urandom | base64) \
                                        --set server.secretKey=\$(head -c 32 /dev/urandom | base64) \
                                        ${HELM_DEPLOY_NAME} helm
                                    """
                                script {
                                    SERVER_IP = sh (
                                        script: """
                                            until [ ! -z \$ready_replicas ] && [ \$ready_replicas -ge 1 ]
                                            do
                                                sleep 15
                                                ready_replicas=\$(kubectl --namespace test get deployments ${HELM_DEPLOY_NAME}-server -o jsonpath='{.status.readyReplicas}')
                                            done

                                            until [ ! -z \$server_ip ]
                                            do
                                                sleep 5
                                                server_ip=\$(kubectl --namespace test get ingress ${HELM_DEPLOY_NAME} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
                                            done
                                            echo \$server_ip

                                            until [ ! -z \$todos_ready ] && [ \$todos_ready -eq 200 ]
                                            do
                                                sleep 15
                                                todos_ready=\$(curl -o /dev/null -Isw '%{http_code}' http://\${server_ip}/api/todos/healthz/ || true)
                                            done

                                            until [ ! -z \$html_ready ] && [ \$html_ready -eq 302 ]
                                            do
                                                sleep 5
                                                html_ready=\$(curl -o /dev/null -Isw '%{http_code}' http://\${server_ip}/ || true)
                                            done
                                        """,
                                        returnStdout: true
                                    ).trim()
                                }
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
                                        sh 'pip install "playwright==1.39.0" "pytest==7.4.3"'
                                        sh "pytest . --server_domain ${SERVER_IP} --junitxml=playwright_results.xml || true"

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
    }
}
