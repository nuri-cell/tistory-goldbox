pipeline {
    agent any

    environment {
        TISTORY_EMAIL      = credentials('TISTORY_EMAIL')
        TISTORY_PASSWORD   = credentials('TISTORY_PASSWORD')
        COUPANG_ACCESS_KEY = credentials('COUPANG_ACCESS_KEY')
        COUPANG_SECRET_KEY = credentials('COUPANG_SECRET_KEY')
        COUPANG_SUB_ID     = credentials('COUPANG_SUB_ID')
        PERPLEXITY_API_KEY = credentials('PERPLEXITY_API_KEY')
        // 필요하다면 Python 설치 경로를 직접 등록해주세요 (예시):
        PATH = "C:\\Users\\mypak\\AppData\\Local\\Programs\\Python\\Python38\\Scripts;${env.PATH}"
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
                // Windows 에이전트에서 python 명령 존재 여부 확인
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
                  // python 설치 경로가 여러 개라면 경로 지정 예시:
                  // "C:\\Python38\\python.exe" -m pip install --upgrade pip
                  pip install --upgrade pip || echo pip not found!
                  pip install --user -r requirements.txt || echo Failed pip install
                """
            }
        }

        stage('Run Script') {
            steps {
                bat """
                  echo ===== Activate and Run =====
                  call .venv1\\Scripts\\activate.bat || echo venv activation failed
                  
                  set TISTORY_EMAIL=%TISTORY_EMAIL%
                  set TISTORY_PASSWORD=%TISTORY_PASSWORD%
                  set COUPANG_ACCESS_KEY=%COUPANG_ACCESS_KEY%
                  set COUPANG_SECRET_KEY=%COUPANG_SECRET_KEY%
                  set COUPANG_SUB_ID=%COUPANG_SUB_ID%
                  set PERPLEXITY_API_KEY=%PERPLEXITY_API_KEY%
                  
                  echo Running script: Tstory_golden.py
                  python Tstory_golden.py || echo Script execution failed
                """
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
