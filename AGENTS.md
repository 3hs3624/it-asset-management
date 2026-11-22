# it-asset-management 작업 규칙

Flask + PostgreSQL 기반 IT 자산 관리 시스템(2025-08 버전). 이후 ITAM 작업은 `itam_v1.0`, `studio`로 이어졌으며 이 저장소는 이전 버전 보관용이다. 개요는 `README.md`.

## 0. 공통 원칙 (모든 AI 에이전트·사람 공통)

이 절은 3hs3624 저장소 전체에 같은 문구로 들어간다. 바꿀 때는 모든 저장소에서 함께 바꾼다.

1. **이 파일(AGENTS.md)이 작업 규칙의 원본이다.** Codex 등 AGENTS.md를 읽는 에이전트는 이 파일을, Claude Code는 이 파일을 불러오는 `CLAUDE.md`를 읽는다. 규칙은 이 파일에만 쓰고 `CLAUDE.md`에는 불러오기 한 줄만 둔다.
2. **원본은 GitHub `3hs3624/it-asset-management`의 `main`이다.** PC 로컬 폴더, 개인 메모리, 채팅 기록은 근거가 아니다. 작업 시작 시 `main` 최신본에서 출발하고, 끝나면 커밋·푸시해 저장소에 남긴다.
3. **소스·문서·설계 결정·작업 기록은 모두 이 저장소에 둔다.** 다음 작업자가 다른 모델이어도 저장소만 읽고 같은 결과를 이어갈 수 있어야 한다. 결정은 문서(ADR·결정 기록)로, 진행 상황은 작업 기록으로 남긴다.
4. **구글 드라이브(또는 노션)에 함께 올리라고 정한 문서는 계속 함께 올린다.** 저장소가 원본이고 드라이브·노션은 같은 내용의 사본이다.
5. **비밀값은 커밋하지 않는다.** 토큰·비밀번호·`.env`는 저장소 밖에 두고, 필요한 변수 이름만 `.env.example`에 적는다.
6. **완료 보고 전에 아래 "검증" 명령을 실행하고 결과를 남긴다.** 실행하지 못한 검증은 "미검증"으로 적는다.
7. **특정 모델 전용 기능에 결과가 의존하지 않게 한다.** Claude 서브에이전트·훅, Codex 전용 설정 등을 쓰더라도, 같은 결과를 내는 절차를 이 파일이나 `docs/`에 적어 둔다.
8. **도구·버전은 저장소에 고정된 것을 쓴다.** 잠금 파일(`package-lock.json`, `requirements.txt`, `pom.xml` 등)과 `Dockerfile`·`docker-compose.yml`을 기준으로 하며, 바꾸면 이유를 기록한다.

## 1. 구성

- `DC_*.py`: Docker 환경용 모듈, `PS_*.py`: 로컬 PostgreSQL 환경용 모듈
- `web_app.py`: Flask 웹 앱, `templates/`: 화면, `init-scripts/01-init.sql`: DB 초기화
- `migrate_excel_data.py`: 엑셀 자산 데이터 이관

## 2. 실행

```bash
docker compose up -d --build     # Web http://localhost:5000, PostgreSQL localhost:5432
```

로컬 Python으로 실행할 때:

```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python web_app.py
```

## 3. 검증

자동 테스트가 없다. 실행 후 대시보드·자산 목록·등록이 동작하는지 확인하고 결과를 기록한다.

## 4. 알려진 문제

- `README.md`가 언급하는 `.dockerignore`, `DC_run_docker*.bat`, `DC_run_web.bat`은 저장소에 없다(과거 로컬에만 있었음). 필요하면 저장소에 추가하거나 README를 고친다.
- 새 기능 개발은 이 저장소가 아니라 `itam_v1.0` 또는 `studio`에서 한다.
