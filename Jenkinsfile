@Library("Shared") _
pipeline {

    agent { label "dev" }

    stages {

        stage("Code Clone") {
            steps {
                script {
                    clone("https://github.com/ShantanuSambhare/Two-Tier-Flask.git", "master")
                }
            }
        }

        stage("Trivy File System Scan") {
            steps {
                script {
                    trivy_fs()
                }
            }
        }

        stage("Build") {
            steps {
                sh "docker build -t two-tier-flask-app ."
            }
        }

        stage("Test") {
            steps {
                echo "Tests will be added here..."
            }
        }

        stage("Push to Docker Hub") {
            steps {
                script {
                    docker_push("dockerHubCreds", "two-tier-flask-app")
                }
            }
        }

        stage("Deploy") {
            steps {
                sh "docker compose up -d --build flask-app"
            }
        }
    }

    post {
        success {
            script {
                emailext(
                    from: 'shantanu@example.com',
                    to: 'shantanu@example.com',
                    body: 'Build SUCCESS for Two-Tier-Flask App',
                    subject: 'Build SUCCESS - Two-Tier-Flask'
                )
            }
        }
        failure {
            script {
                emailext(
                    from: 'shantanu@example.com',
                    to: 'shantanu@example.com',
                    body: 'Build FAILED for Two-Tier-Flask App',
                    subject: 'Build FAILED - Two-Tier-Flask'
                )
            }
        }
    }
}
