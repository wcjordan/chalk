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
                                    withCredentials([
                                        file(credentialsId: 'jenkins-gke-sa', variable: 'GKE_SA_FILE'),
                                    ]) {
                                        sh """
                                            apk --no-cache add bash curl python3
                                            curl https://sdk.cloud.google.com > install.sh
                                            bash install.sh --disable-prompts
                                            export PATH="/root/google-cloud-sdk/bin:\$PATH"

                                            gcloud auth activate-service-account --key-file \$GKE_SA_FILE
                                            gcloud auth configure-docker us-east4-docker.pkg.dev

                                            while (! docker stats --no-stream ); do
                                                echo "Waiting for Docker to launch..."
                                                sleep 1
                                            done

                                            docker buildx create --driver docker-container --name chalk-default
                                            docker buildx use chalk-default
                                            docker buildx build --push \
                                                --cache-to type=registry,ref=us-east4-docker.pkg.dev/${env.GCP_PROJECT}/default-gar/chalk-ui,mode=max \
                                                --cache-from type=registry,ref=us-east4-docker.pkg.dev/${env.GCP_PROJECT}/default-gar/chalk-ui \
                                                -t us-east4-docker.pkg.dev/${env.GCP_PROJECT}/default-gar/chalk-ui:${env.BUILD_TAG} \
                                                ui

                                            docker buildx build --push \
                                                --cache-to type=registry,ref=us-east4-docker.pkg.dev/${env.GCP_PROJECT}/default-gar/chalk-ui,mode=max \
                                                --cache-from type=registry,ref=us-east4-docker.pkg.dev/${env.GCP_PROJECT}/default-gar/chalk-ui \
                                                -t us-east4-docker.pkg.dev/${env.GCP_PROJECT}/default-gar/chalk-ui-base:${env.BUILD_TAG} \
                                                --target base \
                                                ui
                                        """
                                    }
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
                                            image: us-east4-docker.pkg.dev/${env.GCP_PROJECT}/default-gar/chalk-ui-base:${env.BUILD_TAG}
                                            command:
                                            - cat
                                            tty: true
                                            resources:
                                              requests:
                                                cpu: "500m"
                                                memory: "3.0Gi"

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
                                        sh 'yarn --silent install --immutable --prefer-offline'
                                    }
                                    dir('ui') {
                                        sh 'make test'
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
                                    withCredentials([
                                        file(credentialsId: 'jenkins-gke-sa', variable: 'GKE_SA_FILE'),
                                    ]) {
                                        sh """
                                            apk --no-cache add bash curl python3
                                            curl https://sdk.cloud.google.com > install.sh
                                            bash install.sh --disable-prompts
                                            export PATH="/root/google-cloud-sdk/bin:\$PATH"

                                            gcloud auth activate-service-account --key-file \$GKE_SA_FILE
                                            gcloud auth configure-docker us-east4-docker.pkg.dev

                                            while (! docker stats --no-stream ); do
                                                echo "Waiting for Docker to launch..."
                                                sleep 1
                                            done

                                            docker buildx create --driver docker-container --name chalk-default
                                            docker buildx use chalk-default
                                            docker buildx build --push \
                                                --cache-to type=registry,ref=us-east4-docker.pkg.dev/${env.GCP_PROJECT}/default-gar/chalk-server,mode=max \
                                                --cache-from type=registry,ref=us-east4-docker.pkg.dev/${env.GCP_PROJECT}/default-gar/chalk-server \
                                                -t us-east4-docker.pkg.dev/${env.GCP_PROJECT}/default-gar/chalk-server:${env.BUILD_TAG} \
                                                server
                                        """
                                    }
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
                            image: gcr.io/${env.GCP_PROJECT}/gcloud-helm:latest
                            command:
                            - cat
                            tty: true
                            resources:
                              requests:
                                cpu: "500m"
                                memory: "1Gi"
                          - name: jenkins-worker-python
                            image: python:3.10
                            command:
                            - cat
                            tty: true
                            resources:
                              requests:
                                cpu: "300m"
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
                                file(credentialsId: 'chalk-oauth-web-secret', variable: 'OAUTH_WEB_SECRET')
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
                                    ).trim()
                                }
                                sh """
                                    mkdir helm/secrets;
                                    cp \$OAUTH_WEB_SECRET helm/secrets/oauth_web_client_secret.json
                                    helm install \
                                        --set domain=_ \
                                        --set environment=CI \
                                        --set gcpProject=${env.GCP_PROJECT} \
                                        --set imageTag=${env.BUILD_TAG} \
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
                                                ready_replicas=\$(kubectl get deployments ${HELM_DEPLOY_NAME}-server -o jsonpath='{.status.readyReplicas}')
                                            done

                                            until [ ! -z \$server_ip ]
                                            do
                                                sleep 5
                                                server_ip=\$(kubectl get ingress ${HELM_DEPLOY_NAME} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
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
                                dir('tests') {
                                    sh 'pip install "playwright==1.32.1" "pytest==7.3.1"'
                                    sh "pytest . --server_domain ${SERVER_IP} --junitxml=playwright_results.xml || true"

                                    junit testResults: 'playwright_results.xml'
                                    browserStackReportPublisher 'automate'
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
                            sh "gcloud auth activate-service-account --key-file $FILE"
                            sh "gcloud container clusters get-credentials ${env.GCP_PROJECT_NAME}-gke --project ${env.GCP_PROJECT} --zone us-east4-c"
                            sh "helm uninstall ${HELM_DEPLOY_NAME}"
                            retry(5) {
                                sleep 10
                                sh "gcloud sql users delete ${HELM_DEPLOY_NAME} --instance=chalk-ci --quiet"
                            }
                        }
                    }
                }
            }
        }
    }
}
