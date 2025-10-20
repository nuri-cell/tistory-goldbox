pipeline {
    agent any

    environment {
        TISTORY_EMAIL      = credentials('TISTORY_EMAIL')
        TISTORY_PASSWORD   = credentials('TISTORY_PASSWORD')
        COUPANG_ACCESS_KEY = credentials('COUPANG_ACCESS_KEY')
        COUPANG_SECRET_KEY = credentials('COUPANG_SECRET_KEY')
        COUPANG_SUB_ID     = credentials('COUPANG_SUB_ID')
        PERPLEXITY_API_KEY = credentials('PERPLEXITY_API_KEY')
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

        stage('Run Scripts') {
            steps {
                bat """
                  REM 가상환경 활성화
                  call .venv1\\Scripts\\activate.bat
                  
                  REM 환경 변수 설정
                  set TISTORY_EMAIL=%TISTORY_EMAIL%
                  set TISTORY_PASSWORD=%TISTORY_PASSWORD%
                  set COUPANG_ACCESS_KEY=%COUPANG_ACCESS_KEY%
                  set COUPANG_SECRET_KEY=%COUPANG_SECRET_KEY%
                  set COUPANG_SUB_ID=%COUPANG_SUB_ID%
                  set PERPLEXITY_API_KEY=%PERPLEXITY_API_KEY%

                  REM 아래를 실행할 Python 스크립트 경로로 변경하세요
                  python Tstory_golden.py
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
