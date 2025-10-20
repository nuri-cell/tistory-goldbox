pipeline {
    agent any

    environment {
        TISTORY_EMAIL        = credentials('TISTORY_EMAIL')
        TISTORY_PASSWORD     = credentials('TISTORY_PASSWORD')
        COUPANG_ACCESS_KEY   = credentials('COUPANG_ACCESS_KEY')
        COUPANG_SECRET_KEY   = credentials('COUPANG_SECRET_KEY')
        COUPANG_SUB_ID       = credentials('COUPANG_SUB_ID')
        PERPLEXITY_API_KEY   = credentials('PERPLEXITY_API_KEY')

        // Python 설치 경로 직접 지정
        PATH                  = "C:\\Python38\\;C:\\Python38\\Scripts\\;${env.PATH}"
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

        stage('Install Dependencies') {
            steps {
                bat """
                  pip install --upgrade pip
                  pip install --user -r requirements.txt
                """
            }
        }

        stage('Run Scripts') {
            steps {
                bat """
                  echo TISTORY_EMAIL length: !TISTORY_EMAIL:~0,0!
                  echo COUPANG_ACCESS_KEY length: !COUPANG_ACCESS_KEY:~0,0!
                  echo PERPLEXITY_API_KEY length: !PERPLEXITY_API_KEY:~0,0!
                  
                  .venv1\\Scripts\\activate
                  set TISTORY_EMAIL=%TISTORY_EMAIL%
                  set TISTORY_PASSWORD=%TISTORY_PASSWORD%
                  set COUPANG_ACCESS_KEY=%COUPANG_ACCESS_KEY%
                  set COUPANG_SECRET_KEY=%COUPANG_SECRET_KEY%
                  set COUPANG_SUB_ID=%COUPANG_SUB_ID%
                  set PERPLEXITY_API_KEY=%PERPLEXITY_API_KEY%

                  python scripts\\Tstory_golden.py
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
