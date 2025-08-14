#!/usr/bin/env python3
"""
엑셀 데이터를 PostgreSQL로 마이그레이션하는 스크립트
기존 Asset Management.xlsx 파일의 데이터를 PostgreSQL 데이터베이스로 이전합니다.
"""

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExcelToPostgreSQLMigrator:
    def __init__(self, excel_file_path, db_config):
        self.excel_file_path = excel_file_path
        self.db_config = db_config
        self.connection = None
    
    def connect_database(self):
        """PostgreSQL 데이터베이스에 연결합니다."""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            logger.info("데이터베이스에 성공적으로 연결되었습니다.")
            return True
        except psycopg2.Error as e:
            logger.error(f"데이터베이스 연결 실패: {e}")
            return False
    
    def read_excel_data(self):
        """엑셀 파일에서 데이터를 읽어옵니다."""
        try:
            if not os.path.exists(self.excel_file_path):
                logger.error(f"엑셀 파일을 찾을 수 없습니다: {self.excel_file_path}")
                return None
            
            # 엑셀 파일 읽기
            df = pd.read_excel(self.excel_file_path)
            logger.info(f"엑셀 파일에서 {len(df)}개의 행을 읽었습니다.")
            
            # 컬럼명 확인 및 매핑
            expected_columns = ["ID", "Type", "Model", "Purchase Date", "Warranty", "Status", "Location", "Reason"]
            
            if not all(col in df.columns for col in expected_columns):
                logger.warning("일부 예상 컬럼이 없습니다. 사용 가능한 컬럼:")
                logger.warning(f"사용 가능한 컬럼: {list(df.columns)}")
                
                # 컬럼명이 다른 경우 매핑 시도
                column_mapping = {}
                for expected_col in expected_columns:
                    # 대소문자 구분 없이 매핑
                    for actual_col in df.columns:
                        if expected_col.lower() == actual_col.lower():
                            column_mapping[expected_col] = actual_col
                            break
                
                if len(column_mapping) >= 6:  # 최소 6개 컬럼은 필요
                    logger.info("컬럼 매핑을 시도합니다.")
                    df = df.rename(columns=column_mapping)
                else:
                    logger.error("충분한 컬럼을 매핑할 수 없습니다.")
                    return None
            
            # 데이터 정리
            df = df.dropna(subset=['Type', 'Model', 'Status', 'Location'])  # 필수 필드가 비어있는 행 제거
            
            # ID 컬럼이 숫자가 아닌 경우 처리
            if 'ID' in df.columns:
                try:
                    df['ID'] = pd.to_numeric(df['ID'], errors='coerce')
                    df = df.dropna(subset=['ID'])
                except:
                    logger.warning("ID 컬럼을 숫자로 변환할 수 없습니다. 새 ID를 생성합니다.")
                    df = df.drop('ID', axis=1)
            
            # 날짜 컬럼 처리
            if 'Purchase Date' in df.columns:
                df['Purchase Date'] = pd.to_datetime(df['Purchase Date'], errors='coerce')
            
            logger.info(f"정리 후 {len(df)}개의 유효한 행이 남았습니다.")
            return df
            
        except Exception as e:
            logger.error(f"엑셀 파일 읽기 실패: {e}")
            return None
    
    def validate_data(self, df):
        """데이터 유효성을 검증합니다."""
        try:
            # 필수 컬럼 확인
            required_columns = ["Type", "Model", "Status", "Location"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                logger.error(f"필수 컬럼이 누락되었습니다: {missing_columns}")
                return False
            
            # 데이터 타입 검증
            valid_types = ['HW', 'SW', 'NW', 'STORAGE']
            valid_statuses = ['입고', '대기', '운영', '유휴', '폐기']
            valid_locations = ['본사 서버실', '개인지급', '프로젝트장소', '기타']
            
            # Type 검증
            invalid_types = df[~df['Type'].isin(valid_types)]['Type'].unique()
            if len(invalid_types) > 0:
                logger.warning(f"유효하지 않은 Type 값이 있습니다: {invalid_types}")
                # 유효하지 않은 값은 '기타'로 변경
                df.loc[~df['Type'].isin(valid_types), 'Type'] = 'HW'
            
            # Status 검증
            invalid_statuses = df[~df['Status'].isin(valid_statuses)]['Status'].unique()
            if len(invalid_statuses) > 0:
                logger.warning(f"유효하지 않은 Status 값이 있습니다: {invalid_statuses}")
                # 유효하지 않은 값은 '대기'로 변경
                df.loc[~df['Status'].isin(valid_statuses), 'Status'] = '대기'
            
            # Location 검증
            invalid_locations = df[~df['Location'].isin(valid_locations)]['Location'].unique()
            if len(invalid_locations) > 0:
                logger.warning(f"유효하지 않은 Location 값이 있습니다: {invalid_locations}")
                # 유효하지 않은 값은 '기타'로 변경
                df.loc[~df['Location'].isin(valid_locations), 'Location'] = '기타'
            
            logger.info("데이터 검증이 완료되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"데이터 검증 실패: {e}")
            return False
    
    def migrate_data(self, df):
        """데이터를 PostgreSQL로 마이그레이션합니다."""
        try:
            cursor = self.connection.cursor()
            
            # 기존 데이터 확인
            cursor.execute("SELECT COUNT(*) FROM assets")
            existing_count = cursor.fetchone()[0]
            logger.info(f"기존 데이터 수: {existing_count}")
            
            # 마이그레이션 시작
            migrated_count = 0
            skipped_count = 0
            
            for index, row in df.iterrows():
                try:
                    # 데이터 준비
                    asset_data = {
                        'asset_type': row['Type'],
                        'model': str(row['Model']),
                        'purchase_date': row['Purchase Date'] if pd.notna(row['Purchase Date']) else None,
                        'warranty': str(row['Warranty']) if pd.notna(row['Warranty']) else '',
                        'status': row['Status'],
                        'location': row['Location'],
                        'reason': str(row['Reason']) if pd.notna(row['Reason']) else ''
                    }
                    
                    # 중복 체크 (Model과 Type으로)
                    cursor.execute(
                        "SELECT id FROM assets WHERE model = %s AND asset_type = %s",
                        (asset_data['model'], asset_data['asset_type'])
                    )
                    
                    if cursor.fetchone():
                        logger.debug(f"중복 데이터 건너뛰기: {asset_data['model']} ({asset_data['asset_type']})")
                        skipped_count += 1
                        continue
                    
                    # 데이터 삽입
                    insert_query = """
                    INSERT INTO assets (asset_type, model, purchase_date, warranty, status, location, reason)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    cursor.execute(insert_query, (
                        asset_data['asset_type'],
                        asset_data['model'],
                        asset_data['purchase_date'],
                        asset_data['warranty'],
                        asset_data['status'],
                        asset_data['location'],
                        asset_data['reason']
                    ))
                    
                    migrated_count += 1
                    
                    if migrated_count % 10 == 0:
                        logger.info(f"진행률: {migrated_count}/{len(df)}")
                
                except Exception as e:
                    logger.error(f"행 {index} 마이그레이션 실패: {e}")
                    skipped_count += 1
                    continue
            
            # 변경사항 커밋
            self.connection.commit()
            
            logger.info(f"마이그레이션 완료: {migrated_count}개 성공, {skipped_count}개 건너뜀")
            
            # 최종 데이터 수 확인
            cursor.execute("SELECT COUNT(*) FROM assets")
            final_count = cursor.fetchone()[0]
            logger.info(f"최종 데이터 수: {final_count}")
            
            cursor.close()
            return migrated_count
            
        except Exception as e:
            logger.error(f"데이터 마이그레이션 실패: {e}")
            self.connection.rollback()
            return 0
    
    def close_connection(self):
        """데이터베이스 연결을 종료합니다."""
        if self.connection:
            self.connection.close()
            logger.info("데이터베이스 연결이 종료되었습니다.")
    
    def run_migration(self):
        """전체 마이그레이션 프로세스를 실행합니다."""
        logger.info("엑셀 데이터 마이그레이션을 시작합니다...")
        
        try:
            # 1. 데이터베이스 연결
            if not self.connect_database():
                return False
            
            # 2. 엑셀 데이터 읽기
            df = self.read_excel_data()
            if df is None or len(df) == 0:
                logger.error("읽을 수 있는 데이터가 없습니다.")
                return False
            
            # 3. 데이터 검증
            if not self.validate_data(df):
                logger.error("데이터 검증에 실패했습니다.")
                return False
            
            # 4. 데이터 마이그레이션
            migrated_count = self.migrate_data(df)
            
            if migrated_count > 0:
                logger.info(f"✅ 마이그레이션이 성공적으로 완료되었습니다! {migrated_count}개 데이터 이전")
                return True
            else:
                logger.error("❌ 마이그레이션에 실패했습니다.")
                return False
                
        except Exception as e:
            logger.error(f"마이그레이션 중 예상치 못한 오류 발생: {e}")
            return False
        finally:
            self.close_connection()

def main():
    """메인 함수"""
    print("🚀 엑셀 데이터를 PostgreSQL로 마이그레이션합니다...")
    print("=" * 60)
    
    # 설정
    excel_file_path = input("엑셀 파일 경로를 입력하세요 (기본값: Asset Management.xlsx): ").strip()
    if not excel_file_path:
        excel_file_path = "Asset Management.xlsx"
    
    # 데이터베이스 설정
    print("\n📊 데이터베이스 연결 정보를 입력하세요:")
    db_host = input("호스트 (기본값: localhost): ").strip() or "localhost"
    db_port = input("포트 (기본값: 5432): ").strip() or "5432"
    db_name = input("데이터베이스명 (기본값: it_asset_db): ").strip() or "it_asset_db"
    db_user = input("사용자명 (기본값: postgres): ").strip() or "postgres"
    db_password = input("비밀번호: ").strip()
    
    if not db_password:
        print("❌ 비밀번호는 필수입니다.")
        return
    
    db_config = {
        'host': db_host,
        'port': int(db_port),
        'database': db_name,
        'user': db_user,
        'password': db_password
    }
    
    # 마이그레이션 실행
    migrator = ExcelToPostgreSQLMigrator(excel_file_path, db_config)
    
    if migrator.run_migration():
        print("\n🎉 마이그레이션이 성공적으로 완료되었습니다!")
        print("\n📝 다음 단계:")
        print("1. PS_Asset_Management.py를 실행하여 애플리케이션을 시작하세요")
        print("2. 마이그레이션된 데이터를 확인하세요")
    else:
        print("\n❌ 마이그레이션에 실패했습니다.")
        print("로그를 확인하여 문제를 파악하세요.")

if __name__ == "__main__":
    main()

