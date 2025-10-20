pipeline {
    agent any
    environment {
        // Credentials에 등록한 ID 사용
        MY_API_KEY = credentials('API_KEY')
    }
    triggers {
        // 매일 오전 7시30분 실행 (UTC 기준 아닐 경우 조정)
        cron('30 7 * * *')
    }
    stages {
        stage('Checkout') {
            steps {
                // Git URL은 실제 저장소 주소로 변경
                git branch: 'main', url: 'https://github.com/nuri-cell/repo.git'
            }
        }
        stage('Build & Run') {
            steps {
                // 예시: 스크립트 실행 시 환경 변수로 API 키 전달
                sh '''
                  echo "Running daily job..."
                  export API_KEY=${MY_API_KEY}
                  # 예: Python 스크립트 실행
                  python3 scripts/daily_task.py
                '''
            }
        }
    }
    post {
        success {
            echo '빌드 및 스크립트 실행 성공'
        }
        failure {
            echo '빌드 또는 스크립트 실행 실패'
        }
    }
}
