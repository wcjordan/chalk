def SERVER_IP = null
def HELM_DEPLOY_NAME = null

pipeline {
    agent none
    stages {
        stage('Testing') {
            agent {
                kubernetes {
                    yamlFile 'jenkins/jenkins-worker-dind.yml'
                }
            }
            steps {
                container('dind') {
                    script {
                        HELM_DEPLOY_NAME = sh (
                            script: """
                                #!/bin/bash
                                hmm=sh --version
                                hmm2=\$(echo \$hmm)
                                multi_parts=\$(echo ${env.BUILD_TAG} | tr _- "\n")
                                declare -a parts=(echo \$multi_parts)
                                part_len=\$(echo \${#parts[@]})
                                branch_part=\$(echo "\${parts[@]:2:\$part_len-3}" | tr " " - | head -c 12)
                                echo \$parts[1]-\$parts[2]-\$branch_part-\$parts[-1]
                            """,
                            returnStdout: true
                        ).trim()
                    }
                    sh "echo ${HELM_DEPLOY_NAME}"
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
                                timeout(time: 15, unit: 'MINUTES')
                            }
                            steps {
                                container('dind') {
                                    withDockerRegistry(credentialsId: "gcr:gke_key", url: "https://gcr.io/${env.GCP_PROJECT}") {
                                        sh "docker build -f ui/Dockerfile --build-arg 'GCP_PROJECT=${env.GCP_PROJECT}' -t gcr.io/${env.GCP_PROJECT}/chalk-ui:${env.BUILD_TAG} ui"
                                        sh "docker push gcr.io/${env.GCP_PROJECT}/chalk-ui:${env.BUILD_TAG}"
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
                                            image: gcr.io/${env.GCP_PROJECT}/chalk-ui-base:latest
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
                                        sh 'yarn install --pure-lockfile'
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
                                    withDockerRegistry(credentialsId: "gcr:gke_key", url: "https://gcr.io/${env.GCP_PROJECT}") {
                                        sh "docker build -f server/Dockerfile --build-arg 'GCP_PROJECT=${env.GCP_PROJECT}' -t gcr.io/${env.GCP_PROJECT}/chalk-server:${env.BUILD_TAG} server"
                                        sh "docker push gcr.io/${env.GCP_PROJECT}/chalk-server:${env.BUILD_TAG}"
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
                                        sh 'env $(grep -v "^#" ../.env_default | xargs) SECRET_KEY=testkey make test'
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
                            withCredentials([file(credentialsId: 'jenkins-gke-sa', variable: 'FILE')]) {
                                sh "gcloud auth activate-service-account default-jenkins@${env.GCP_PROJECT}.iam.gserviceaccount.com --key-file $FILE"
                                sh "gcloud container clusters get-credentials ${env.GCP_PROJECT_NAME}-gke --project ${env.GCP_PROJECT} --zone us-east4-c"

                                script {
                                    HELM_DEPLOY_NAME = sh (
                                        script: """
                                            parts=(\$(echo ${env.BUILD_TAG} | tr _- "\n"))
                                            part_len=\$(echo \${#parts[@]})
                                            branch_part=\$(echo "\${parts[@]:2:\$part_len-3}" | tr " " - | head -c 12)
                                            echo \$parts[1]-\$parts[2]-\$branch_part-\$parts[-1]
                                        """,
                                        returnStdout: true
                                    ).trim()
                                }
                                sh """
                                    helm install \
                                        --set environment=CI \
                                        --set gcpProject=${env.GCP_PROJECT} \
                                        --set imageTag=${env.BUILD_TAG} \
                                        --set server.dbPassword=\$(head -c 32 /dev/urandom | base64) \
                                        --set server.djangoEmail="test@testmail.com" \
                                        --set server.djangoPassword=\$(head -c 32 /dev/urandom | base64) \
                                        --set server.djangoUsername=\$(head -c 32 /dev/urandom | base64) \
                                        --set server.secretKey=\$(head -c 32 /dev/urandom | base64) \
                                        --set ui.sentryDsn=${env.SENTRY_DSN} \
                                        --set ui.sentryToken=${env.SENTRY_TOKEN} \
                                        ${HELM_DEPLOY_NAME} helm
                                    """
                                script {
                                    SERVER_IP = sh (
                                        script: """
                                            until [ ! -z \$server_ip ]
                                            do
                                                server_ip=\$(kubectl get ingress ${HELM_DEPLOY_NAME} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
                                            done
                                            echo \$server_ip
                                        """,
                                        returnStdout: true
                                    ).trim()
                                }
                            }
                        }
                    }
                }
                stage('Selenium Tests') {
                    agent {
                        kubernetes {
                            yamlFile 'jenkins/jenkins-worker-python.yml'
                        }
                    }
                    options {
                        timeout(time: 20, unit: 'MINUTES')
                    }
                    steps {
                        browserstack(credentialsId: 'browserstack_key') {
                            container('jenkins-worker-python') {
                                dir('tests') {
                                    sh 'pip install "selenium==3.141.0" "pytest==6.2.2"'
                                    sh "pytest . --server_domain ${SERVER_IP}"
                                }
                            }
                        }
                    }
                    post {
                        always {
                            browserStackReportPublisher 'automate'
                        }
                    }
                }
            }
            post {
                always {
                    container('jenkins-helm') {
                        withCredentials([file(credentialsId: 'jenkins-gke-sa', variable: 'FILE')]) {
                            sh "gcloud auth activate-service-account default-jenkins@${env.GCP_PROJECT}.iam.gserviceaccount.com --key-file $FILE"
                            sh "gcloud container clusters get-credentials ${env.GCP_PROJECT_NAME}-gke --project ${env.GCP_PROJECT} --zone us-east4-c"
                            sh "helm uninstall ${HELM_DEPLOY_NAME}"
                        }
                    }
                }
            }
        }
    }
}
