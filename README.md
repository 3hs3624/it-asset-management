# 🖥️ IT 자산 관리 시스템

PostgreSQL과 Docker를 사용한 현대적인 IT 자산 관리 시스템입니다.

## ✨ 주요 기능

- **자산 관리**: 하드웨어, 소프트웨어, 네트워크, 스토리지 자산의 CRUD 작업
- **실시간 통계**: 자산 현황을 실시간으로 표시하는 대시보드
- **검색 및 필터링**: 고급 검색 기능과 필드별 필터링
- **변경 이력**: 모든 자산 변경사항을 자동으로 기록
- **데이터 내보내기**: CSV 형식으로 데이터 백업
- **웹 인터페이스**: 반응형 웹 디자인으로 모든 기기에서 접근 가능
- **Docker 지원**: 컨테이너 기반 배포로 쉬운 설치 및 실행

## 🏗️ 아키텍처

### 백엔드
- **데이터베이스**: PostgreSQL 15
- **웹 프레임워크**: Flask (Python)
- **ORM**: psycopg2 (PostgreSQL 어댑터)

### 프론트엔드
- **UI 프레임워크**: Bootstrap 5
- **아이콘**: Font Awesome 6
- **JavaScript**: ES6+ (Fetch API, Async/Await)

### 인프라
- **컨테이너화**: Docker & Docker Compose
- **데이터 영속성**: Docker Volumes
- **네트워킹**: 포트 매핑 (PostgreSQL: 5432, Web: 5000)

## 📁 프로젝트 구조

```
Asset/
├── 📁 templates/                 # 웹 템플릿
│   ├── index.html               # 메인 페이지
│   └── error.html               # 에러 페이지
├── 📁 init-scripts/             # 데이터베이스 초기화
│   └── 01-init.sql             # 테이블 생성 및 샘플 데이터
├── 🐳 docker-compose.yml        # Docker 서비스 설정
├── 🐳 Dockerfile                # 웹 앱 컨테이너 빌드
├── 🐳 .gitignore                # Git 제외 파일 목록
├── 🐳 .dockerignore             # Docker 제외 파일 목록
├── 🐳 requirements.txt           # Python 의존성
├── 🐳 web_app.py                # Flask 웹 애플리케이션
├── 🐳 DC_*.py                   # Docker 환경용 모듈
├── 🐳 PS_*.py                   # PostgreSQL 환경용 모듈
├── 🐳 DC_run_web.bat            # 웹 앱 실행 스크립트
├── 🐳 DC_run_docker.bat         # 전체 시스템 실행 스크립트
├── 🐳 DC_run_docker_simple.bat  # 데이터베이스만 실행 스크립트
├── 🐳 migrate_excel_data.py     # 엑셀 데이터 마이그레이션
└── 📖 README.md                 # 프로젝트 문서
```

## 🚀 빠른 시작

### 1. 사전 요구사항
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 설치
- Git 설치

### 2. 저장소 클론
```bash
git clone https://github.com/your-username/it-asset-management.git
cd it-asset-management
```

### 3. 웹 애플리케이션 실행
```bash
# Windows
DC_run_web.bat

# 또는 수동 실행
docker-compose up -d --build
```

### 4. 웹 브라우저에서 접속
```
http://localhost:5000
```

## 🛠️ 실행 방법

### 웹 애플리케이션 (권장)
```bash
DC_run_web.bat
```
- PostgreSQL + 웹 앱을 모두 Docker로 실행
- 웹 브라우저에서 `http://localhost:5000` 접속

### 데이터베이스만 실행
```bash
DC_run_docker_simple.bat
```
- PostgreSQL만 Docker로 실행
- 로컬 Python 앱과 연동

### 전체 시스템 (Python 필요)
```bash
DC_run_docker.bat
```
- 데이터베이스 + GUI 앱 모두 실행

## 📊 데이터베이스 스키마

### 자산 테이블 (assets)
| 컬럼명 | 타입 | 설명 | 제약조건 |
|--------|------|------|----------|
| id | SERIAL | 자산 ID | PRIMARY KEY |
| asset_type | VARCHAR(10) | 자산 유형 | HW, SW, NW, STORAGE |
| model | VARCHAR(255) | 모델명 | NOT NULL |
| purchase_date | DATE | 구매일 | - |
| warranty | VARCHAR(255) | 보증기간 | - |
| status | VARCHAR(20) | 상태 | 입고, 대기, 운영, 유휴, 폐기 |
| location | VARCHAR(100) | 위치 | 본사 서버실, 개인지급, 프로젝트장소, 기타 |
| reason | TEXT | 비고 | - |
| created_at | TIMESTAMP | 생성일시 | 자동 설정 |
| updated_at | TIMESTAMP | 수정일시 | 자동 업데이트 |

### 이력 테이블 (asset_history)
| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| id | SERIAL | 이력 ID |
| asset_id | INTEGER | 자산 ID (외래키) |
| action | VARCHAR(20) | 작업 유형 (INSERT, UPDATE, DELETE) |
| old_values | JSONB | 변경 전 값 |
| new_values | JSONB | 변경 후 값 |
| changed_at | TIMESTAMP | 변경 일시 |

## 🔧 개발 환경 설정

### 로컬 개발
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=it_asset_db
export DB_USER=postgres
export DB_PASSWORD=your_password

# 애플리케이션 실행
python web_app.py
```

### Docker 개발
```bash
# 컨테이너 빌드 및 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f webapp

# 컨테이너 내부 접속
docker exec -it it_asset_webapp bash
```

## 📝 API 문서

### 자산 관리 API

#### 자산 목록 조회
```
GET /api/assets
```

#### 특정 자산 조회
```
GET /api/assets/{asset_id}
```

#### 자산 추가
```
POST /api/assets
Content-Type: application/json

{
  "Type": "HW",
  "Model": "Dell OptiPlex 7090",
  "Purchase Date": "2024-01-15",
  "Warranty": "3년",
  "Status": "운영",
  "Location": "본사 서버실",
  "Reason": "개발팀 업무용"
}
```

#### 자산 수정
```
PUT /api/assets/{asset_id}
Content-Type: application/json

{
  "Type": "HW",
  "Model": "Dell OptiPlex 7090",
  "Status": "유휴"
}
```

#### 자산 삭제
```
DELETE /api/assets/{asset_id}
```

#### 자산 검색
```
GET /api/search?q={search_term}&field={search_field}
```

#### 통계 정보
```
GET /api/statistics
```

#### CSV 내보내기
```
GET /export/csv
```

## 🧪 테스트

### 단위 테스트
```bash
python -m pytest tests/
```

### 통합 테스트
```bash
# Docker 환경에서 테스트
docker-compose up -d
python -m pytest tests/integration/
```

## 📦 배포

### Docker 이미지 빌드
```bash
docker build -t it-asset-management:latest .
```

### Docker Compose 배포
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes 배포
```bash
kubectl apply -f k8s/
```

## 🔒 보안

### 현재 구현된 보안 기능
- SQL 인젝션 방지 (매개변수화된 쿼리)
- XSS 방지 (템플릿 엔진 사용)
- CSRF 보호 (Flask 기본 설정)

### 운영 환경 권장사항
- 환경 변수를 통한 비밀번호 관리
- HTTPS 적용
- 방화벽 설정
- 정기적인 보안 업데이트

## 🤝 기여하기

### 개발 환경 설정
1. 저장소 포크
2. 기능 브랜치 생성: `git checkout -b feature/amazing-feature`
3. 변경사항 커밋: `git commit -m 'Add amazing feature'`
4. 브랜치 푸시: `git push origin feature/amazing-feature`
5. Pull Request 생성

### 코드 스타일
- Python: PEP 8 준수
- JavaScript: ESLint 규칙 준수
- HTML/CSS: Bootstrap 가이드라인 준수

### 테스트
- 새로운 기능에 대한 테스트 코드 작성
- 기존 테스트가 모두 통과하는지 확인

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 지원

### 문제 해결
- [GitHub Issues](https://github.com/your-username/it-asset-management/issues) 등록
- [Wiki](https://github.com/your-username/it-asset-management/wiki) 참조

### 커뮤니티
- GitHub Discussions 참여
- Pull Request 제출

## 🙏 감사의 말

이 프로젝트는 다음 오픈소스 프로젝트들의 도움을 받았습니다:
- [Flask](https://flask.palletsprojects.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [Docker](https://www.docker.com/)
- [Bootstrap](https://getbootstrap.com/)

---

**버전**: 2.1.0  
**최종 업데이트**: 2024년 12월  
**개발자**: IT Asset Management Team

