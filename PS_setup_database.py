#!/usr/bin/env python3
"""
PostgreSQL 데이터베이스 설정 스크립트
이 스크립트는 IT 자산 관리 시스템을 위한 데이터베이스를 설정합니다.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os

def create_database():
    """데이터베이스를 생성합니다."""
    # 기본 연결 (postgres 데이터베이스에 연결)
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="postgres",
            user="postgres",
            password="your_password"  # 실제 비밀번호로 변경하세요
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # 데이터베이스 존재 여부 확인
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'it_asset_db'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE it_asset_db")
            print("✅ 데이터베이스 'it_asset_db'가 생성되었습니다.")
        else:
            print("ℹ️  데이터베이스 'it_asset_db'가 이미 존재합니다.")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ 데이터베이스 생성 중 오류가 발생했습니다: {e}")
        return False
    
    return True

def create_tables():
    """테이블들을 생성합니다."""
    try:
        # it_asset_db에 연결
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="it_asset_db",
            user="postgres",
            password="your_password"  # 실제 비밀번호로 변경하세요
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
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
        
        print("✅ 테이블과 트리거가 생성되었습니다.")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ 테이블 생성 중 오류가 발생했습니다: {e}")
        return False
    
    return True

def insert_sample_data():
    """샘플 데이터를 삽입합니다."""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="it_asset_db",
            user="postgres",
            password="your_password"  # 실제 비밀번호로 변경하세요
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # 기존 데이터 확인
        cursor.execute("SELECT COUNT(*) FROM assets")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # 샘플 데이터 삽입
            sample_data = [
                ('HW', 'Dell OptiPlex 7090', '2024-01-15', '3년', '운영', '본사 서버실', '개발팀 업무용'),
                ('SW', 'Visual Studio Code', '2024-02-01', '1년', '운영', '개인지급', '개발자 코딩 도구'),
                ('NW', 'Cisco Catalyst 2960', '2023-12-10', '5년', '운영', '본사 서버실', '네트워크 스위치'),
                ('STORAGE', 'Seagate IronWolf 4TB', '2024-01-20', '3년', '입고', '본사 서버실', '백업 저장소'),
                ('HW', 'HP EliteBook 840', '2024-03-01', '3년', '대기', '개인지급', '신입사원 지급 예정')
            ]
            
            insert_query = """
            INSERT INTO assets (asset_type, model, purchase_date, warranty, status, location, reason)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.executemany(insert_query, sample_data)
            print("✅ 샘플 데이터가 삽입되었습니다.")
        else:
            print(f"ℹ️  이미 {count}개의 자산 데이터가 존재합니다.")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ 샘플 데이터 삽입 중 오류가 발생했습니다: {e}")
        return False
    
    return True

def test_connection():
    """데이터베이스 연결을 테스트합니다."""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="it_asset_db",
            user="postgres",
            password="your_password"  # 실제 비밀번호로 변경하세요
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"✅ 데이터베이스 연결 성공!")
        print(f"PostgreSQL 버전: {version[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ 데이터베이스 연결 테스트 실패: {e}")
        return False

def main():
    """메인 함수"""
    print("🚀 PostgreSQL 데이터베이스 설정을 시작합니다...")
    print("=" * 50)
    
    # 1. 데이터베이스 생성
    print("\n1️⃣ 데이터베이스 생성 중...")
    if not create_database():
        print("❌ 데이터베이스 생성에 실패했습니다.")
        sys.exit(1)
    
    # 2. 테이블 생성
    print("\n2️⃣ 테이블 생성 중...")
    if not create_tables():
        print("❌ 테이블 생성에 실패했습니다.")
        sys.exit(1)
    
    # 3. 샘플 데이터 삽입
    print("\n3️⃣ 샘플 데이터 삽입 중...")
    if not insert_sample_data():
        print("❌ 샘플 데이터 삽입에 실패했습니다.")
        sys.exit(1)
    
    # 4. 연결 테스트
    print("\n4️⃣ 연결 테스트 중...")
    if not test_connection():
        print("❌ 연결 테스트에 실패했습니다.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 PostgreSQL 데이터베이스 설정이 완료되었습니다!")
    print("\n📝 다음 단계:")
    print("1. PS_config.py 파일에서 데이터베이스 비밀번호를 설정하세요")
    print("2. PS_Asset_Management.py를 실행하여 애플리케이션을 시작하세요")
    print("\n💡 문제가 발생하면 PostgreSQL 서비스가 실행 중인지 확인하세요")

if __name__ == "__main__":
    main()

