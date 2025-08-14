#!/usr/bin/env python3
"""
IT 자산 관리 시스템 - 웹 버전
Flask를 사용하여 웹 브라우저에서 접근 가능한 자산 관리 시스템
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from DC_asset_manager import ITAssetManager
import logging
from datetime import datetime
import json

# Flask 앱 초기화
app = Flask(__name__)
app.secret_key = 'it_asset_management_secret_key'

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 자산 매니저 초기화
try:
    asset_manager = ITAssetManager()
    logger.info("자산 매니저가 성공적으로 초기화되었습니다")
except Exception as e:
    logger.error(f"자산 매니저 초기화 실패: {e}")
    asset_manager = None

@app.route('/')
def index():
    """메인 페이지 - 자산 목록과 통계 표시"""
    if not asset_manager:
        return render_template('error.html', error="데이터베이스 연결에 실패했습니다.")
    
    try:
        assets = asset_manager.list_assets()
        stats = asset_manager.get_asset_statistics()
        return render_template('index.html', assets=assets, stats=stats)
    except Exception as e:
        logger.error(f"메인 페이지 로드 오류: {e}")
        return render_template('error.html', error=str(e))

@app.route('/api/assets')
def get_assets():
    """자산 목록을 JSON으로 반환"""
    if not asset_manager:
        return jsonify({'error': '데이터베이스 연결에 실패했습니다.'}), 500
    
    try:
        assets = asset_manager.list_assets()
        return jsonify(assets)
    except Exception as e:
        logger.error(f"자산 목록 조회 오류: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assets/<int:asset_id>')
def get_asset(asset_id):
    """특정 자산 정보를 JSON으로 반환"""
    if not asset_manager:
        return jsonify({'error': '데이터베이스 연결에 실패했습니다.'}), 500
    
    try:
        asset = asset_manager.get_asset(asset_id)
        if asset:
            return jsonify(asset)
        else:
            return jsonify({'error': '자산을 찾을 수 없습니다.'}), 404
    except Exception as e:
        logger.error(f"자산 조회 오류: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assets', methods=['POST'])
def add_asset():
    """새 자산 추가"""
    if not asset_manager:
        return jsonify({'error': '데이터베이스 연결에 실패했습니다.'}), 500
    
    try:
        data = request.get_json()
        asset_id = asset_manager.add_asset(data)
        return jsonify({'success': True, 'asset_id': asset_id, 'message': '자산이 성공적으로 추가되었습니다.'})
    except Exception as e:
        logger.error(f"자산 추가 오류: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assets/<int:asset_id>', methods=['PUT'])
def update_asset(asset_id):
    """자산 정보 수정"""
    if not asset_manager:
        return jsonify({'error': '데이터베이스 연결에 실패했습니다.'}), 500
    
    try:
        data = request.get_json()
        success = asset_manager.update_asset(asset_id, data)
        if success:
            return jsonify({'success': True, 'message': '자산이 성공적으로 수정되었습니다.'})
        else:
            return jsonify({'error': '자산 수정에 실패했습니다.'}), 400
    except Exception as e:
        logger.error(f"자산 수정 오류: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assets/<int:asset_id>', methods=['DELETE'])
def delete_asset(asset_id):
    """자산 삭제"""
    if not asset_manager:
        return jsonify({'error': '데이터베이스 연결에 실패했습니다.'}), 500
    
    try:
        success = asset_manager.delete_asset(asset_id)
        if success:
            return jsonify({'success': True, 'message': '자산이 성공적으로 삭제되었습니다.'})
        else:
            return jsonify({'error': '자산 삭제에 실패했습니다.'}), 400
    except Exception as e:
        logger.error(f"자산 삭제 오류: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search')
def search_assets():
    """자산 검색"""
    if not asset_manager:
        return jsonify({'error': '데이터베이스 연결에 실패했습니다.'}), 500
    
    try:
        search_term = request.args.get('q', '')
        search_field = request.args.get('field', 'all')
        
        if not search_term:
            assets = asset_manager.list_assets()
        else:
            assets = asset_manager.search_assets(search_term, search_field if search_field != 'all' else None)
        
        return jsonify(assets)
    except Exception as e:
        logger.error(f"자산 검색 오류: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics')
def get_statistics():
    """자산 통계 정보 반환"""
    if not asset_manager:
        return jsonify({'error': '데이터베이스 연결에 실패했습니다.'}), 500
    
    try:
        stats = asset_manager.get_asset_statistics()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"통계 조회 오류: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/export/csv')
def export_csv():
    """CSV 형식으로 데이터 내보내기"""
    if not asset_manager:
        return jsonify({'error': '데이터베이스 연결에 실패했습니다.'}), 500
    
    try:
        from io import StringIO
        import csv
        
        assets = asset_manager.list_assets()
        
        # CSV 데이터 생성
        output = StringIO()
        writer = csv.writer(output)
        
        # 헤더 작성
        writer.writerow(['ID', 'Type', 'Model', 'Purchase Date', 'Warranty', 'Status', 'Location', 'Reason'])
        
        # 데이터 작성
        for asset_id, asset_data in assets.items():
            writer.writerow([
                asset_id,
                asset_data.get('Type', ''),
                asset_data.get('Model', ''),
                asset_data.get('Purchase Date', ''),
                asset_data.get('Warranty', ''),
                asset_data.get('Status', ''),
                asset_data.get('Location', ''),
                asset_data.get('Reason', '')
            ])
        
        output.seek(0)
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=assets_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
        )
        
    except Exception as e:
        logger.error(f"CSV 내보내기 오류: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error="페이지를 찾을 수 없습니다."), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="내부 서버 오류가 발생했습니다."), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

