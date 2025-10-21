pipeline {
    agent any

    environment {
        TISTORY_EMAIL      = credentials('TISTORY_EMAIL')
        TISTORY_PASSWORD   = credentials('TISTORY_PASSWORD')
        COUPANG_ACCESS_KEY = credentials('COUPANG_ACCESS_KEY')
        COUPANG_SECRET_KEY = credentials('COUPANG_SECRET_KEY')
        COUPANG_SUB_ID     = credentials('COUPANG_SUB_ID')
        PERPLEXITY_API_KEY = credentials('PERPLEXITY_API_KEY')
        PATH = "C:\\Users\\mypak\\AppData\\Local\\Programs\\Python\\Python38;C:\\Users\\mypak\\AppData\\Local\\Programs\\Python\\Python38\\Scripts;${env.PATH}"
    }

    triggers {
        cron('30 7 * * *')
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'master', url: 'https://github.com/nuri-cell/tistory-goldbox.git'
            }
        }

        stage('Validate Python') {
            steps {
                bat """
                  echo ===== Check Python =====
                  where python || echo Python executable not found!
                  python --version || echo Failed to run python
                """
            }
        }

        stage('Install Dependencies') {
            steps {
                bat """
                  echo ===== Install Dependencies =====
                  pip install --upgrade pip || echo pip not found!
                  
                  if exist requirements.txt (
                      pip install --user -r requirements.txt || echo Failed pip install
                  ) else (
                      echo requirements.txt not found, skipping...
                  )
                """
            }
        }

        stage('Run Script') {
            steps {
                bat """
                  echo ===== Activate and Run =====
                  
                  if exist .venv1\\Scripts\\activate.bat (
                      call .venv1\\Scripts\\activate.bat
                  ) else (
                      echo venv not found, using system Python
                  )

                  REM -- 프로젝트 루트를 PYTHONPATH에 추가
                  set PYTHONPATH=%WORKSPACE%;%PYTHONPATH%

                  set TISTORY_EMAIL=%TISTORY_EMAIL%
                  set TISTORY_PASSWORD=%TISTORY_PASSWORD%
                  set COUPANG_ACCESS_KEY=%COUPANG_ACCESS_KEY%
                  set COUPANG_SECRET_KEY=%COUPANG_SECRET_KEY%
                  set COUPANG_SUB_ID=%COUPANG_SUB_ID%
                  set PERPLEXITY_API_KEY=%PERPLEXITY_API_KEY%
                  
                  echo Running script: Tistory\\Tstory_golden.py
                  python Tistory\\Tstory_golden.py || echo Script execution failed
                """
            }
        }

        stage('List Workspace') {
            steps {
                bat 'echo ===== Workspace Files ====='
                bat 'dir /B /S'
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline completed successfully.'
        }
        failure {
            echo '❌ Pipeline failed. Check console output for details.'
        }
    }
}
