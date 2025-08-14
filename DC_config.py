# Docker 환경을 위한 데이터베이스 설정
# 이 파일은 Docker Compose로 PostgreSQL을 실행할 때 사용합니다.

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'it_asset_db',
    'user': 'postgres',
    'password': 'postgres123'  # docker-compose.yml에 설정된 비밀번호
}

# Docker 환경 확인
import os
if os.getenv('DOCKER_ENV'):
    # Docker 컨테이너 내부에서 실행될 때
    DB_CONFIG['host'] = 'postgres'
