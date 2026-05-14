pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install dependencies') {
            steps {
                bat 'python -m pip install --upgrade pip'
                bat 'python -m pip install -r requirements.txt'
            }
        }

        stage('Run tests') {
            steps {
                bat 'pytest tests/'
            }
        }

        stage('Run comparison') {
            steps {
                bat 'python compare/default_vs_ai.py'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'output/**/*.png', allowEmptyArchive: true
            junit 'tests/**/*.xml'
        }
    }
}
