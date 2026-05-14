pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Python') {
            steps {
                bat '''
                where python >nul 2>nul
                if %errorlevel% neq 0 (
                    echo Python not found, installing...
                    choco install python --version=3.10.0 -y
                ) else (
                    echo Python is already installed
                )
                '''
            }
        }

        stage('Install dependencies') {
            steps {
                bat 'C:\\Python310\\python.exe -m pip install --upgrade pip'
                bat 'C:\\Python310\\python.exe -m pip install -r requirements.txt'
            }
        }

        stage('Run tests') {
            steps {
                bat 'C:\\Python310\\python.exe -m pytest tests/'
            }
        }

        stage('Run comparison') {
            steps {
                bat 'C:\\Python310\\python.exe compare/default_vs_ai.py'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'output/**/*.png', allowEmptyArchive: true
        }
    }
}


