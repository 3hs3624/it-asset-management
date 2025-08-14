# 🐳 Docker 기반 IT 자산 관리 시스템

Docker를 사용하여 PostgreSQL 데이터베이스와 함께 IT 자산 관리 시스템을 실행하는 방법입니다.

## 🚀 빠른 시작

### 1. Docker Desktop 설치
- [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) 다운로드 및 설치
- 설치 후 Docker Desktop 실행

### 2. 웹 애플리케이션 실행 (권장)
```bash
# Windows 배치 파일 실행 (웹 버전)
DC_run_web.bat
```
이 방법은 PostgreSQL 데이터베이스와 웹 애플리케이션을 모두 Docker로 실행합니다.

### 3. 데이터베이스만 실행 (Python 설치 없이)
```bash
# Windows 배치 파일 실행 (데이터베이스만)
DC_run_docker_simple.bat
```
이 방법은 PostgreSQL 데이터베이스만 Docker로 실행합니다.

### 4. 전체 시스템 실행 (Python 필요)
```bash
# Windows 배치 파일 실행 (전체 시스템)
DC_run_docker.bat
```

### 5. 수동 실행
```bash
# 1. PostgreSQL 컨테이너 시작
docker-compose up -d

# 2. Python 패키지 설치 (Python이 설치된 경우)
pip install -r requirements.txt

# 3. 애플리케이션 실행
python DC_Asset_Management.py
```

## 📁 Docker 파일 구조

```
├── docker-compose.yml              # PostgreSQL + 웹 앱 컨테이너 설정
├── Dockerfile                      # 웹 애플리케이션 빌드 설정
├── init-scripts/                   # 데이터베이스 초기화 스크립트
│   └── 01-init.sql                # 테이블 생성 및 샘플 데이터
├── templates/                      # 웹 템플릿
│   ├── index.html                  # 메인 페이지
│   └── error.html                  # 에러 페이지
├── web_app.py                      # Flask 웹 애플리케이션
├── DC_config.py                    # Docker 환경 설정
├── DC_database.py                  # Docker 데이터베이스 매니저
├── DC_asset_manager.py             # Docker 자산 매니저
├── DC_Asset_Management.py          # Docker 메인 애플리케이션 (GUI)
├── DC_run_docker.bat               # Windows 실행 스크립트 (전체)
├── DC_run_docker_simple.bat        # Windows 실행 스크립트 (DB만)
├── DC_run_web.bat                  # Windows 실행 스크립트 (웹 버전)
└── requirements.txt                 # Python 패키지 목록
```

## 🔧 Docker Compose 설정

### PostgreSQL 서비스
- **이미지**: postgres:15
- **포트**: 5432
- **데이터베이스**: it_asset_db
- **사용자**: postgres
- **비밀번호**: postgres123
- **데이터 영속성**: Docker 볼륨 사용

### 웹 애플리케이션 서비스
- **빌드**: 로컬 Dockerfile
- **포트**: 5000
- **의존성**: PostgreSQL 서비스
- **자동 재시작**: 활성화

### 자동 초기화
- 컨테이너 시작 시 자동으로 테이블 생성
- 샘플 데이터 자동 삽입
- 인덱스 및 트리거 자동 생성

## 🌐 웹 애플리케이션 접속

### 웹 브라우저에서 접속
```
http://localhost:5000
```

### 주요 기능
- **자산 목록 조회**: 모든 IT 자산을 테이블 형태로 표시
- **실시간 통계**: 자산 현황을 실시간으로 업데이트
- **자산 추가/수정/삭제**: 모달 창을 통한 직관적인 관리
- **검색 및 필터링**: 필드별 검색 및 전체 검색 지원
- **CSV 내보내기**: 데이터 백업 및 외부 시스템 연동
- **반응형 디자인**: 모바일과 데스크톱 모두 지원

## 📊 데이터베이스 구조

### 자산 테이블 (assets)
- ID, 유형, 모델, 구매일, 보증기간, 상태, 위치, 비고
- 자동 생성일시 및 수정일시
- 데이터 무결성 제약조건

### 이력 테이블 (asset_history)
- 모든 변경사항 자동 기록
- JSON 형태로 변경 전후 값 저장

## 🎯 주요 기능

- **실시간 통계**: 자산 현황 실시간 표시
- **고급 검색**: 필드별 및 전체 검색
- **변경 이력**: 모든 데이터 변경사항 자동 기록
- **데이터 내보내기**: CSV 형식으로 백업
- **직관적 UI**: 사용하기 쉬운 웹 인터페이스
- **모바일 지원**: 반응형 디자인으로 모든 기기에서 사용 가능

## 🛠️ 관리 명령어

### 컨테이너 관리
```bash
# 컨테이너 시작 (웹 앱 포함)
docker-compose up -d --build

# 컨테이너 상태 확인
docker-compose ps

# 컨테이너 중지
docker-compose down

# 컨테이너와 데이터 모두 삭제
docker-compose down -v

# 로그 확인
docker-compose logs postgres
docker-compose logs webapp
```

### 데이터베이스 접속
```bash
# PostgreSQL 컨테이너에 직접 접속
docker exec -it it_asset_postgres psql -U postgres -d it_asset_db

# 데이터베이스 백업
docker exec it_asset_postgres pg_dump -U postgres it_asset_db > backup.sql
```

## 🔍 문제 해결

### 1. 포트 충돌
```
Error: Port 5432 is already in use
Error: Port 5000 is already in use
```
**해결방법**: 
- 다른 PostgreSQL 서비스 중지
- 다른 웹 서비스 중지
- `docker-compose.yml`에서 포트 변경

### 2. 컨테이너 시작 실패
```
Error: container failed to start
```
**해결방법**:
```bash
# 로그 확인
docker-compose logs postgres
docker-compose logs webapp

# 컨테이너 재시작
docker-compose restart postgres
docker-compose restart webapp
```

### 3. 연결 타임아웃
```
Error: connection timeout
```
**해결방법**:
- Docker Desktop이 실행 중인지 확인
- 컨테이너가 완전히 시작될 때까지 대기 (약 15초)

### 4. 웹 앱 접속 불가
```
http://localhost:5000 접속 안됨
```
**해결방법**:
```bash
# 웹 앱 로그 확인
docker-compose logs webapp

# 컨테이너 상태 확인
docker-compose ps

# 웹 앱 재시작
docker-compose restart webapp
```

## 📈 성능 최적화

### 데이터베이스 인덱스
- 자동으로 생성되는 인덱스로 검색 성능 향상
- 자주 사용되는 필드에 대한 최적화

### 연결 풀링
- 애플리케이션 수준에서 연결 관리
- 효율적인 리소스 사용

## 🔒 보안 고려사항

- **개발용 설정**: 기본 비밀번호 사용
- **운영 환경**: 환경변수로 비밀번호 관리 권장
- **네트워크**: 로컬호스트에서만 접근 가능
- **웹 보안**: Flask 기본 보안 설정 사용

## 🚀 확장 가능성

- **다중 인스턴스**: 여러 사용자 동시 접근 지원
- **백업/복구**: Docker 볼륨을 통한 데이터 보존
- **모니터링**: 컨테이너 상태 및 로그 모니터링
- **로드 밸런싱**: 여러 웹 앱 인스턴스로 확장 가능

## 💡 팁

1. **첫 실행**: 컨테이너 시작 후 15초 대기
2. **데이터 보존**: `docker-compose down`만 사용하여 데이터 유지
3. **정기 백업**: `pg_dump` 명령어로 데이터베이스 백업
4. **리소스 모니터링**: Docker Desktop에서 리소스 사용량 확인
5. **웹 앱 접속**: `http://localhost:5000`으로 웹 브라우저에서 접속
6. **자동 새로고침**: 웹 페이지에서 실시간 데이터 업데이트

---

**버전**: 2.1.0 (Docker + PostgreSQL + Web App)
**최종 업데이트**: 2024년 12월
**개발자**: IT Asset Management Team
