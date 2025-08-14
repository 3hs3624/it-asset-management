-- IT 자산 관리 시스템 초기화 스크립트

-- 데이터베이스 생성 (이미 docker-compose에서 생성됨)
-- CREATE DATABASE it_asset_db;

-- IT 자산 테이블 생성
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

-- 자산 이력 테이블 생성
CREATE TABLE IF NOT EXISTS asset_history (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE,
    action VARCHAR(20) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- updated_at 트리거 함수 생성
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- updated_at 트리거 생성
DROP TRIGGER IF EXISTS update_assets_updated_at ON assets;
CREATE TRIGGER update_assets_updated_at 
    BEFORE UPDATE ON assets 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 샘플 데이터 삽입
INSERT INTO assets (asset_type, model, purchase_date, warranty, status, location, reason) VALUES
('HW', 'Dell OptiPlex 7090', '2024-01-15', '3년', '운영', '본사 서버실', '개발팀 업무용'),
('SW', 'Visual Studio Code', '2024-02-01', '1년', '운영', '개인지급', '개발자 코딩 도구'),
('NW', 'Cisco Catalyst 2960', '2023-12-10', '5년', '운영', '본사 서버실', '네트워크 스위치'),
('STORAGE', 'Seagate IronWolf 4TB', '2024-01-20', '3년', '입고', '본사 서버실', '백업 저장소'),
('HW', 'HP EliteBook 840', '2024-03-01', '3년', '대기', '개인지급', '신입사원 지급 예정')
ON CONFLICT DO NOTHING;

-- 인덱스 생성 (성능 향상)
CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(asset_type);
CREATE INDEX IF NOT EXISTS idx_assets_status ON assets(status);
CREATE INDEX IF NOT EXISTS idx_assets_location ON assets(location);
CREATE INDEX IF NOT EXISTS idx_assets_model ON assets(model);
