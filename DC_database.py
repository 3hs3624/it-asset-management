import psycopg2
from psycopg2.extras import RealDictCursor
from DC_config import DB_CONFIG
import logging
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DockerDatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect_with_retry()
    
    def connect_with_retry(self, max_retries=30, delay=2):
        """Docker 컨테이너가 완전히 시작될 때까지 재시도하며 연결합니다."""
        for attempt in range(max_retries):
            try:
                self.connection = psycopg2.connect(**DB_CONFIG)
                logger.info("✅ PostgreSQL 데이터베이스에 성공적으로 연결되었습니다!")
                return
            except psycopg2.OperationalError as e:
                if attempt < max_retries - 1:
                    logger.info(f"⏳ 데이터베이스 연결 대기 중... ({attempt + 1}/{max_retries})")
                    time.sleep(delay)
                else:
                    logger.error(f"❌ 데이터베이스 연결 실패: {e}")
                    raise
    
    def test_connection(self):
        """데이터베이스 연결을 테스트합니다."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            logger.info(f"PostgreSQL 버전: {version[0]}")
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"연결 테스트 실패: {e}")
            return False
    
    def close(self):
        """데이터베이스 연결을 종료합니다."""
        if self.connection:
            self.connection.close()
            logger.info("데이터베이스 연결이 종료되었습니다.")
    
    def execute_query(self, query, params=None):
        """쿼리를 실행하고 결과를 반환합니다."""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                self.connection.commit()
                result = cursor.rowcount
            
            cursor.close()
            return result
            
        except psycopg2.Error as e:
            logger.error(f"쿼리 실행 실패: {e}")
            self.connection.rollback()
            raise
    
    def get_connection(self):
        """데이터베이스 연결 객체를 반환합니다."""
        return self.connection

# Docker 데이터베이스 매니저 인스턴스 생성
db_manager = DockerDatabaseManager()
