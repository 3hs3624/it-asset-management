import psycopg2
from psycopg2.extras import RealDictCursor
from PS_config import DB_CONFIG
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """데이터베이스에 연결합니다."""
        try:
            self.connection = psycopg2.connect(**DB_CONFIG)
            logger.info("Database connected successfully")
        except psycopg2.Error as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def create_tables(self):
        """필요한 테이블들을 생성합니다."""
        try:
            cursor = self.connection.cursor()
            
            # IT 자산 테이블 생성
            create_assets_table = """
            CREATE TABLE IF NOT EXISTS assets (
                id SERIAL PRIMARY KEY,
                asset_type VARCHAR(10) NOT NULL CHECK (asset_type IN ('HW', 'SW', 'NW', 'STORAGE')),
                model VARCHAR(255) NOT NULL,
                purchase_date DATE,
                warranty VARCHAR(255),
                status VARCHAR(20) NOT NULL CHECK (status IN ('입고', '대기', '운영', '유휴', '폐기')),
                location VARCHAR(100) NOT NULL CHECK (location IN ('본사 서버실', '개인지급', '프로젝트장소', '기타')),
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            # 자산 이력 테이블 생성
            create_history_table = """
            CREATE TABLE IF NOT EXISTS asset_history (
                id SERIAL PRIMARY KEY,
                asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE,
                action VARCHAR(20) NOT NULL,
                old_values JSONB,
                new_values JSONB,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            cursor.execute(create_assets_table)
            cursor.execute(create_history_table)
            
            # updated_at 트리거 함수 생성
            create_trigger_function = """
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
            """
            
            # updated_at 트리거 생성
            create_trigger = """
            CREATE TRIGGER update_assets_updated_at 
                BEFORE UPDATE ON assets 
                FOR EACH ROW 
                EXECUTE FUNCTION update_updated_at_column();
            """
            
            cursor.execute(create_trigger_function)
            cursor.execute(create_trigger)
            
            self.connection.commit()
            logger.info("Tables created successfully")
            
        except psycopg2.Error as e:
            logger.error(f"Error creating tables: {e}")
            self.connection.rollback()
            raise
        finally:
            cursor.close()
    
    def close(self):
        """데이터베이스 연결을 종료합니다."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
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
            logger.error(f"Query execution failed: {e}")
            self.connection.rollback()
            raise
    
    def get_connection(self):
        """데이터베이스 연결 객체를 반환합니다."""
        return self.connection

# 데이터베이스 매니저 인스턴스 생성
db_manager = DatabaseManager()

