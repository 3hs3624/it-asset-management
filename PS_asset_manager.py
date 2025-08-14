from PS_database import db_manager
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ITAssetManager:
    def __init__(self):
        self.db = db_manager
    
    def add_asset(self, asset_data):
        """새로운 자산을 추가합니다."""
        try:
            query = """
            INSERT INTO assets (asset_type, model, purchase_date, warranty, status, location, reason)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """
            
            params = (
                asset_data["Type"],
                asset_data["Model"],
                asset_data["Purchase Date"],
                asset_data["Warranty"],
                asset_data["Status"],
                asset_data["Location"],
                asset_data["Reason"]
            )
            
            result = self.db.execute_query(query, params)
            
            # 이력 기록
            if result:
                asset_id = result[0]['id']
                self._log_history(asset_id, 'INSERT', None, asset_data)
                logger.info(f"Asset added successfully with ID: {asset_id}")
                return asset_id
            
        except Exception as e:
            logger.error(f"Error adding asset: {e}")
            raise
    
    def update_asset(self, asset_id, asset_data):
        """기존 자산을 업데이트합니다."""
        try:
            # 기존 데이터 조회
            old_data = self.get_asset(asset_id)
            if not old_data:
                raise ValueError(f"Asset with ID {asset_id} not found")
            
            query = """
            UPDATE assets 
            SET asset_type = %s, model = %s, purchase_date = %s, warranty = %s, 
                status = %s, location = %s, reason = %s
            WHERE id = %s
            """
            
            params = (
                asset_data["Type"],
                asset_data["Model"],
                asset_data["Purchase Date"],
                asset_data["Warranty"],
                asset_data["Status"],
                asset_data["Location"],
                asset_data["Reason"],
                asset_id
            )
            
            result = self.db.execute_query(query, params)
            
            if result > 0:
                # 이력 기록
                self._log_history(asset_id, 'UPDATE', old_data, asset_data)
                logger.info(f"Asset {asset_id} updated successfully")
                return True
            else:
                logger.warning(f"No rows affected when updating asset {asset_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating asset {asset_id}: {e}")
            raise
    
    def delete_asset(self, asset_id):
        """자산을 삭제합니다."""
        try:
            # 기존 데이터 조회 (이력 기록용)
            old_data = self.get_asset(asset_id)
            if not old_data:
                raise ValueError(f"Asset with ID {asset_id} not found")
            
            query = "DELETE FROM assets WHERE id = %s"
            result = self.db.execute_query(query, (asset_id,))
            
            if result > 0:
                # 이력 기록
                self._log_history(asset_id, 'DELETE', old_data, None)
                logger.info(f"Asset {asset_id} deleted successfully")
                return True
            else:
                logger.warning(f"No rows affected when deleting asset {asset_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting asset {asset_id}: {e}")
            raise
    
    def get_asset(self, asset_id):
        """특정 ID의 자산을 조회합니다."""
        try:
            query = "SELECT * FROM assets WHERE id = %s"
            result = self.db.execute_query(query, (asset_id,))
            
            if result:
                asset = result[0]
                return {
                    "ID": asset['id'],
                    "Type": asset['asset_type'],
                    "Model": asset['model'],
                    "Purchase Date": asset['purchase_date'],
                    "Warranty": asset['warranty'],
                    "Status": asset['status'],
                    "Location": asset['location'],
                    "Reason": asset['reason']
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting asset {asset_id}: {e}")
            raise
    
    def list_assets(self):
        """모든 자산을 조회합니다."""
        try:
            query = "SELECT * FROM assets ORDER BY id"
            result = self.db.execute_query(query)
            
            assets = {}
            for row in result:
                assets[row['id']] = {
                    "Type": row['asset_type'],
                    "Model": row['model'],
                    "Purchase Date": row['purchase_date'],
                    "Warranty": row['warranty'],
                    "Status": row['status'],
                    "Location": row['location'],
                    "Reason": row['reason']
                }
            
            return assets
            
        except Exception as e:
            logger.error(f"Error listing assets: {e}")
            raise
    
    def search_assets(self, search_term, search_field=None):
        """자산을 검색합니다."""
        try:
            if search_field:
                query = f"SELECT * FROM assets WHERE {search_field} ILIKE %s ORDER BY id"
                params = (f"%{search_term}%",)
            else:
                query = """
                SELECT * FROM assets 
                WHERE asset_type ILIKE %s OR model ILIKE %s OR status ILIKE %s 
                OR location ILIKE %s OR reason ILIKE %s
                ORDER BY id
                """
                params = (f"%{search_term}%",) * 5
            
            result = self.db.execute_query(query, params)
            
            assets = {}
            for row in result:
                assets[row['id']] = {
                    "Type": row['asset_type'],
                    "Model": row['model'],
                    "Purchase Date": row['purchase_date'],
                    "Warranty": row['warranty'],
                    "Status": row['status'],
                    "Location": row['location'],
                    "Reason": row['reason']
                }
            
            return assets
            
        except Exception as e:
            logger.error(f"Error searching assets: {e}")
            raise
    
    def get_asset_statistics(self):
        """자산 통계를 조회합니다."""
        try:
            query = """
            SELECT 
                COUNT(*) as total_assets,
                COUNT(CASE WHEN status = '입고' THEN 1 END) as in_stock,
                COUNT(CASE WHEN status = '대기' THEN 1 END) as waiting,
                COUNT(CASE WHEN status = '운영' THEN 1 END) as operating,
                COUNT(CASE WHEN status = '유휴' THEN 1 END) as idle,
                COUNT(CASE WHEN status = '폐기' THEN 1 END) as disposed,
                COUNT(CASE WHEN asset_type = 'HW' THEN 1 END) as hardware,
                COUNT(CASE WHEN asset_type = 'SW' THEN 1 END) as software,
                COUNT(CASE WHEN asset_type = 'NW' THEN 1 END) as network,
                COUNT(CASE WHEN asset_type = 'STORAGE' THEN 1 END) as storage
            FROM assets
            """
            
            result = self.db.execute_query(query)
            return result[0] if result else {}
            
        except Exception as e:
            logger.error(f"Error getting asset statistics: {e}")
            raise
    
    def _log_history(self, asset_id, action, old_values, new_values):
        """자산 변경 이력을 기록합니다."""
        try:
            query = """
            INSERT INTO asset_history (asset_id, action, old_values, new_values)
            VALUES (%s, %s, %s, %s)
            """
            
            old_json = json.dumps(old_values, default=str) if old_values else None
            new_json = json.dumps(new_values, default=str) if new_values else None
            
            params = (asset_id, action, old_json, new_json)
            self.db.execute_query(query, params)
            
        except Exception as e:
            logger.error(f"Error logging history: {e}")
            # 이력 기록 실패는 자산 작업을 중단시키지 않음
    
    def close(self):
        """데이터베이스 연결을 종료합니다."""
        self.db.close()

