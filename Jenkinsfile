pipeline {
    agent {
        // Docker를 사용해 Python 환경을 컨테이너로 제공
        docker {
            image 'python:3.8-slim'  // Python 3.8 공식 Docker 이미지
            args '-u root:root'      // 필요시 권한 설정
        }
    }

    environment {
        TISTORY_EMAIL        = credentials('TISTORY_EMAIL')
        TISTORY_PASSWORD     = credentials('TISTORY_PASSWORD')
        COUPANG_ACCESS_KEY   = credentials('COUPANG_ACCESS_KEY')
        COUPANG_SECRET_KEY   = credentials('COUPANG_SECRET_KEY')
        COUPANG_SUB_ID       = credentials('COUPANG_SUB_ID')
        PERPLEXITY_API_KEY   = credentials('PERPLEXITY_API_KEY')
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
                sh '''
                  python -m pip install --upgrade pip
                  python -m pip install -r requirements.txt
                '''
            }
        }

        stage('Run Scripts') {
            steps {
                sh '''
                  export TISTORY_EMAIL=${TISTORY_EMAIL}
                  export TISTORY_PASSWORD=${TISTORY_PASSWORD}
                  export COUPANG_ACCESS_KEY=${COUPANG_ACCESS_KEY}
                  export COUPANG_SECRET_KEY=${COUPANG_SECRET_KEY}
                  export COUPANG_SUB_ID=${COUPANG_SUB_ID}
                  export PERPLEXITY_API_KEY=${PERPLEXITY_API_KEY}

                  # 실제 실행할 스크립트로 변경하세요
                  python scripts/Tstory_golden.py
                '''
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
