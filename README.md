# Auto-Board

개인용 메타데이터 기반 기록물 관리 시스템

## 개요

사용자가 커스텀 "보드"(기록 유형)를 만들고 사용자 정의 필드/컬럼을 설정할 수 있는 개인용 데이터베이스 UI입니다.
예: 일기, 키보드 수집, 혈압 기록, 영화 리뷰 등

**단일 사용자 애플리케이션** - 외부 인터페이스 없음

## 기술스택

### 백엔드

- **FastAPI** - 웹 프레임워크
- **Jinja2** - 서버 사이드 템플릿 (JSON 메타데이터 기반)
- **SQLite** - 데이터베이스
- **JWT** - 쿠키 기반 인증
- **bcrypt** - 비밀번호 해싱

### 프론트엔드

- **TailwindCSS** - 스타일링
- **Alpine.js** - 반응형 UI
- **Quill.js** - 리치 HTML 에디터

### 빌드/테스트

- **uv** - Python 패키지 매니저
- **npm** - Node.js 패키지 관리
- **Jest** - JavaScript 단위 테스트

## 폴더 구성

```text
auto-board/
├── app/
│   ├── core/            # 설정, 로깅, 인증, 의존성
│   ├── routes/          # 라우트 핸들러
│   ├── schemas/         # Pydantic 모델
│   ├── utils/           # 유틸리티 (데이터베이스 매니저)
│   ├── static/
│   │   ├── css/
│   │   ├── images/
│   │   └── js/
│   ├── templates/       # Jinja2 템플릿
│   ├── resources/       # SQL DDL, 리소스
│   └── main.py          # 애플리케이션 진입점
├── tests/               # Python 테스트 (pytest)
├── tests_js/            # JavaScript 테스트 (Jest)
├── docs/                # 설계 문서
├── pyproject.toml       # Python 프로젝트 설정
├── package.json         # Node.js 프로젝트 설정
├── jest.config.js       # Jest 설정
└── README.md            # 이 파일
```

## 🚀 새로운 PC에서 시작하기

### 요약

1. 저장소 클론 - git clone
2. Python 환경 설정 - uv venv + uv sync
3. Node.js 의존성 - npm install
4. 환경 변수 - .env 파일 생성
5. DB 초기화 - 자동 또는 수동 초기화
6. CSS 빌드 - npm run build:css
7. 테스트 실행 - npm test (29개 테스트)
8. 앱 실행 - python -m uvicorn app.main:app --reload
9. 브라우저 접속 - <http://localhost:8000>

### 필수 요구사항

- **Python**: 3.8+
- **Node.js**: 18+
- **uv**: Python 패키지 매니저

### Step 1: 저장소 클론

```bash
git clone <repository-url>
cd auto-board
```

### Step 2: Python 의존성 설치

```bash
# uv 사용 (권장)
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv sync

# 또는 pip 사용
pip install -r requirements.txt  # (필요시 생성)
```

**⚠️ IDE 설정:** VSCode/PyCharm에서 Python 인터프리터를 **`.venv`** 또는 **`.venv/Scripts/python.exe`** (Windows)로 선택해야 pytest가 정상 작동합니다.

### Step 3: Node.js 의존성 설치

```bash
npm install
```

### Step 4: 환경 변수 설정

`.env` 파일 생성:

```bash
# Windows
copy .env.example .env

# 또는 Linux/Mac
cp .env.example .env
```

`.env` 파일 수정 (필요에 따라):

```env
AUTOBOARD_PROFILE=local
DEBUG=True
```

### Step 5: 데이터베이스 초기화 (첫 실행 시)

데이터베이스는 자동으로 생성되며, 다음 명령으로 수동 초기화 가능:

```bash
python -c "from app.core.config import Settings; Settings()"
```

### Step 6: TailwindCSS 빌드 (CSS 개발 시)

```bash
npm run build:css
```

**Watch 모드** (CSS 자동 갱신):

```bash
npm run build:css  # 이미 watch 모드 포함
```

### Step 7: JavaScript 테스트 실행 (선택사항)

```bash
npm test              # 모든 테스트 실행 (29개)
npm run test:watch    # Watch 모드
npm run test:coverage # 커버리지 리포트
```

### Step 8: 애플리케이션 실행

#### Windows

```bash
set AUTOBOARD_PROFILE=local && python -m uvicorn app.main:app --reload
```

#### Linux/Mac

```bash
export AUTOBOARD_PROFILE=local && python -m uvicorn app.main:app --reload
```

**또는:**

```bash
python app/main.py
```

### Step 9: 브라우저 접속

```
http://localhost:8000
```

**기본 로그인:**

- Username: `admin`
- Password: `admin123`

---

## 📋 개발 명령어

### Python (백엔드)

```bash
# 개발 서버 실행 (자동 리로드)
python -m uvicorn app.main:app --reload

# Python 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/test_db_manager.py -v
```

### Node.js (프론트엔드)

```bash
# CSS 빌드 (Watch 모드)
npm run build:css

# JavaScript 테스트 실행
npm test

# Watch 모드 (파일 변경 시 자동 실행)
npm run test:watch

# 테스트 커버리지 리포트
npm run test:coverage
```

---

## 🗄️ 데이터베이스

### 핵심 테이블

- **admin_users**: 관리자 계정
- **boards**: 보드 정의 (이름, 물리 테이블명, 설명)
- **meta_data**: JSON 메타데이터 (columns, list, view, create, edit)
- **files**: 첨부 파일 메타데이터
- **file_match**: 파일과 보드 레코드 링크

### 동적 테이블

각 보드는 자체 SQLite 테이블 생성:

- `table_1`, `table_2`, ... (메타데이터 기반 자동 생성)
- 자동 컬럼: `id`, `created_at`, `updated_at`

---

## 🏗️ 아키텍처

### 메타데이터 기반 설계

시스템은 JSON 메타데이터로 UI 렌더링과 데이터 구조를 동적으로 제어합니다:

1. **보드 생성**
   - `boards` 테이블에 보드 정의 저장
   - JSON 메타데이터를 `meta_data` 테이블에 저장
   - 메타데이터 기반 CREATE TABLE DDL 실행

2. **메타데이터 유형**
   - `columns`: 스키마/필드 정의
   - `list`: 레코드 목록 표시 방식
   - `view`: 개별 레코드 상세 표시
   - `create`/`edit`: 폼 정의

### 인증

- JWT 기반 쿠키 인증
- 기본 관리자 계정: `admin` / `admin123`

---

## 📖 설계 문서

상세 설명서는 `docs/` 폴더 참고:

- `docs/design.md` - 전체 아키텍처
- `docs/columns.md` - 컬럼 필드 메타데이터
- `docs/list.md` - 목록 뷰 설정
- `docs/view.md` - 상세 뷰 스타일링
- `docs/테스트전략.md` - 테스트 전략 및 도구

---

## 🧪 테스트

### Python 테스트 (pytest)

```bash
pytest                    # 모든 테스트 실행
pytest -v               # 상세 출력
pytest tests/test_db_manager.py  # 특정 파일
```

### JavaScript 테스트 (Jest)

```bash
npm test                # 모든 테스트 (29개)
npm run test:watch     # Watch 모드
npm run test:coverage  # 커버리지 리포트
```

**테스트 대상:**

- `app/static/js/board_manager_logic.js` - 순수 검증 로직 (29개 테스트 케이스)

---

## 🔧 트러블슈팅

### 포트 8000 이미 사용 중

```bash
# 다른 포트 사용
python -m uvicorn app.main:app --reload --port 8001
```

### 데이터베이스 초기화

```bash
# 데이터베이스 파일 삭제 (첫 실행 시 자동 생성)
rm app.db
python app/main.py
```

### CSS 변경사항 미반영

```bash
# TailwindCSS 재빌드
npm run build:css
```

### JavaScript 테스트 실패

```bash
# 의존성 재설치
rm package-lock.json node_modules
npm install
npm test
```

---

## 📝 License

ISC

---

## 👨‍💻 개발자 가이드

### 새 기능 추가 시 순서

1. **데이터베이스**: `app/resources/sqls/` DDL 추가
2. **백엔드**: `app/core/`, `app/routes/` 로직 작성
3. **테스트**: `tests/` Python 테스트 추가
4. **프론트엔드**: `app/static/js/`, `app/templates/` 작성
5. **테스트**: `tests_js/` JavaScript 테스트 추가 (필요시)
6. **CSS**: `app/static/css/` TailwindCSS 스타일 추가
7. **문서**: `docs/` 설계 문서 업데이트

### 코드 스타일

- **Python**: PEP 8
- **JavaScript**: ES6+, 함수형 프로그래밍
- **CSS**: TailwindCSS 유틸리티 클래스

---

**질문이나 이슈는 GitHub Issues를 통해 보고해주세요.**
