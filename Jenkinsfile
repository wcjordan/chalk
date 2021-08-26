pipeline {
    agent none
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
            stages {
                stage('Deploy Integration Server') {
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
                    options {
                        timeout(time: 10, unit: 'MINUTES')
                    }
                    steps {
                        container('jenkins-helm') {
                            withCredentials([file(credentialsId: 'jenkins-gke-sa', variable: 'FILE')]) {
                                sh "gcloud auth activate-service-account account_name --key-file $FILE"
                                sh "gcloud container clusters get-credentials ${env.GCP_PROJECT_NAME} --project ${env.GCP_PROJECT}"
                                sh "kubectl get deployments"
                                sh "kubectl config get-contexts"
                            }

                            // sh 'helm install test-chart helm'
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
                                    sh 'pytest .'
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
        }
    }
}
