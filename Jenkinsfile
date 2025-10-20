pipeline {
    agent any

    environment {
        // Credentials IDs must match the ones registered in Jenkins
        TISTORY_EMAIL        = credentials('TISTORY_EMAIL')
        TISTORY_PASSWORD     = credentials('TISTORY_PASSWORD')
        COUPANG_ACCESS_KEY   = credentials('COUPANG_ACCESS_KEY')
        COUPANG_SECRET_KEY   = credentials('COUPANG_SECRET_KEY')
        COUPANG_SUB_ID       = credentials('COUPANG_SUB_ID')
        PERPLEXITY_API_KEY   = credentials('PERPLEXITY_API_KEY')
    }

    triggers {
        // 매일 오전 7시 30분에 실행 (서버 로컬 타임존 기준)
        cron('30 7 * * *')
    }

    stages {
        stage('Checkout') {
            steps {
                // 본인의 Git 저장소 URL로 변경하세요
                git branch: 'main', url: 'https://github.com/username/repo.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                // 예: Python 가상 환경 설정 및 패키지 설치
                sh '''
                  python3 -m venv venv
                  . venv/bin/activate
                  pip install -r requirements.txt
                '''
            }
        }

        stage('Run Scripts') {
            steps {
                // 환경 변수로 키가 제대로 로드됐는지 확인 (길이 출력 예시)
                sh '''
                  echo "TISTORY_EMAIL length: ${#TISTORY_EMAIL}"
                  echo "COUPANG_ACCESS_KEY length: ${#COUPANG_ACCESS_KEY}"
                  echo "PERPLEXITY_API_KEY length: ${#PERPLEXITY_API_KEY}"
                '''
                
                // 실제 스크립트 실행 예시
                sh '''
                  . venv/bin/activate
                  export TISTORY_EMAIL=${TISTORY_EMAIL}
                  export TISTORY_PASSWORD=${TISTORY_PASSWORD}
                  export COUPANG_ACCESS_KEY=${COUPANG_ACCESS_KEY}
                  export COUPANG_SECRET_KEY=${COUPANG_SECRET_KEY}
                  export COUPANG_SUB_ID=${COUPANG_SUB_ID}
                  export PERPLEXITY_API_KEY=${PERPLEXITY_API_KEY}

                  # 예: Python 스크립트 실행
                  python3 scripts/daily_task.py
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
