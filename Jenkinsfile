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
                                    yamlFile 'jenkins-worker-dind.yml'
                                }
                            }
                            options {
                                timeout(time: 10, unit: 'MINUTES')
                            }
                            steps {
                                container('dind') {
                                    withDockerRegistry(credentialsId: 'gcr:flipperkid-default', url: 'https://gcr.io/flipperkid-default') {
                                        sh "docker build -f ui/Dockerfile -t gcr.io/flipperkid-default/chalk-ui:${env.BUILD_TAG} ui"
                                        sh "docker push gcr.io/flipperkid-default/chalk-ui:${env.BUILD_TAG}"
                                    }
                                }
                            }
                        }
                        stage('Test UI') {
                            agent {
                                kubernetes {
                                    yamlFile 'jenkins-worker-ui.yml'
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
                                    yamlFile 'jenkins-worker-dind.yml'
                                }
                            }
                            options {
                                timeout(time: 10, unit: 'MINUTES')
                            }
                            steps {
                                container('dind') {
                                    withDockerRegistry(credentialsId: 'gcr:flipperkid-default', url: 'https://gcr.io/flipperkid-default') {
                                        sh "docker build -f server/Dockerfile -t gcr.io/flipperkid-default/chalk-server:${env.BUILD_TAG} server"
                                        sh "docker push gcr.io/flipperkid-default/chalk-server:${env.BUILD_TAG}"
                                    }
                                }
                            }
                        }
                        stage('Test Server') {
                            agent {
                                kubernetes {
                                    yamlFile 'jenkins-worker-python.yml'
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
        stage('Selenium Tests') {
            agent {
                kubernetes {
                    yamlFile 'jenkins-worker-python.yml'
                }
            }
            options {
                timeout(time: 10, unit: 'MINUTES')
            }
            steps {
                browserstack(credentialsId: 'f5043d10-054c-41a9-94e5-4e81c0b56f01') {
                    container('jenkins-worker-python') {
                        dir('tests') {
                            sh 'pip install "selenium==3.141.0"'
                            sh 'python sample.py'
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
