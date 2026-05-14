pipeline {
    agent any

    tools {
        python 'Python 3.10'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install dependencies') {
            steps {
                sh 'python -m pip install --upgrade pip'
                sh 'python -m pip install -r requirements.txt'
            }
        }

        stage('Run tests') {
            steps {
                sh 'pytest tests/'
            }
        }

        stage('Run comparison') {
            steps {
                sh 'python compare/default_vs_ai.py'
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
