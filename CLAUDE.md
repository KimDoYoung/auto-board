# CLAUDE.md

이 문서는 Claude Code(claude.ai/code) 에 대한 지침을 제공한다

## Project Overview

- 이 프로젝트(auto-board)는 사용자가 자신의 기록물에 대한 스키마를 임의로 설정하고 그 결과를 json으로 만들어서 sqlite table에 저장 한 후 그것을 바탕으로 CRUD를 하도록 한다.

## Technology Stack

**Backend:**

- FastAPI (web framework)
- Jinja2 (server-side templating driven by JSON metadata)
- SQLite (database)
- JWT (authentication via cookies)
- bcrypt (password hashing)

**Frontend:**

- TailwindCSS (styling)
- Alpine.js (reactive UI)
- Quill.js (rich HTML editor)
- CDN-based JavaScript libraries

**Build Tools:**

- uv (Python package manager)
- npm (for TailwindCSS build)

## Development Commands

### Running the Application

```bash
# Set profile and run with uvicorn (with auto-reload)
set AUTOBOARD_PROFILE=local && python -m uvicorn app.main:app --reload

# Or run directly
python app/main.py
```

The application uses profile-based configuration. Set `AUTOBOARD_PROFILE` environment variable (default: `local`). Configuration loads from `.env` and `.env.{profile}` files.

### TailwindCSS Build

```bash
# Watch mode for CSS development
npm run build:css
```

This watches `app/static/css/input.css` and outputs to `app/static/css/style.css`.

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_db_manager.py

# Run with verbose output
pytest -v
```

## Architecture

### Core Metadata-Driven Design

The system uses JSON metadata stored in the `meta_data` table to dynamically control UI rendering and data structure:

1. **boards** table: Stores board definitions (name, physical_table_name, note)
2. **meta_data** table: Stores JSON metadata for each board with different `name` types:
   - `table`: Defines the schema/fields for the board (see docs/columns.md)
   - `list`: Defines how to display record lists (see docs/list.md)
   - `view`: Defines how to display individual records (see docs/view.md)
   - `create`/`edit`: Defines forms for creating/editing records

3. **Dynamic physical tables**: Each board gets its own SQLite table (e.g., `table_1`, `table_2`) created based on the `columns` metadata

### Board Creation Flow

When a user creates a new board:

1. Insert into `boards` table with generated physical_table_name
2. Insert columns metadata JSON into `meta_data` table
3. Generate and execute CREATE TABLE DDL for the physical table based on metadata
4. Physical tables include auto-generated columns: `id`, `created_at`, `updated_at`
5. templates/board/wizard/step1~4.html에서 `table`, `list`,`create_edit`,`view`의 meta data (json)을 만든다. 서버단 board.py에서 처리한다.
6. 5.번의 각각 javascript는 js/wizard/step1~4.js에서 처리한다
7. templates/record/ 폴더의 create.html, edit.html, list.html,view.html에서 설정된 json에 따라서 CRUD를 수행한다.

### Configuration System

Configuration is managed through `app/core/config.py:Settings` using pydantic-settings:

- Profile-based .env loading (.env → .env.{profile})
- Auto-creates necessary directories (BASE_DIR, FILES_DIR, LOG_FILE parent, DB_PATH parent)
- Key settings: BASE_DIR, DB_PATH, FILES_DIR, LOG_FILE, HOST, PORT, JWT settings

### Database Connection

Use dependency injection pattern via `app/core/deps.py:get_db_connection()`:

- Returns SQLite connection with `row_factory = sqlite3.Row` for dict-like access
- Properly yields and closes connections
- 비동기 함수를 유지하되, 스레드 안전하게 처리하는 방식을 선택할 것.

### Authentication

JWT-based authentication using cookies:

- `app/core/deps.py:get_current_user_from_cookie()` extracts and validates JWT from cookies
- Default admin user: username=`admin`, password=`admin123` (created by DDL)
- Tokens stored in `access_token` cookie with optional "Bearer " prefix

### Logging

Structured logging via `app/core/logger.py:get_logger()`:

- Uses concurrent_log_handler for file rotation
- Logs to both console and file (LOG_FILE path)
- Startup logs show all configuration values

### Application Structure

```
app/
├── core/           # Core infrastructure (config, logging, deps, security)
├── routes/         # FastAPI route handlers (home.py, board.py)
├── schemas/        # Pydantic models (user.py, token.py, board.py)
├── utils/          # Utilities (db_manager.py)
├── static/         # Static files (css, images, js)
├── templates/      # Jinja2 templates
├── resources/      # SQL DDL files and other resources
└── main.py         # Application entry point
```

### PyInstaller Considerations

Code includes PyInstaller support for --onedir bundling:

- `app/main.py:get_directory_path()` handles `sys.frozen` and `sys._MEIPASS`
- Static/template paths resolve correctly in both dev and bundled modes

## Database Schema

Core tables (see `app/resources/sqls/autoboard_ddl.sql`):

- **admin_users**: Single admin account authentication
- **boards**: Board definitions
- **meta_data**: JSON metadata for boards (columns, list, view, etc.)
- **files**: Attachment file metadata
- **file_match**: Links files to board records (board_id, table_id, file_id)

Dynamic tables (`table_1`, `table_2`, etc.) are created per board based on metadata.

## Data Type Mapping

SQLite type mapping in `app/utils/db_manager.py:map_sqlite_type()`:

- `integer`, `boolean` → INTEGER
- `float` → REAL
- All others (including `string`, `text`, `ymd`, `datetime`) → TEXT

## 주요 구현 참고사항

- 보드 라우트는 /boards 접두사 사용 (app/routes/board.py에 정의됨)
- 템플릿은 라우트 간 접근을 위해 app.state.templates에 저장됨
- 모든 타임스탬프는 SQLite의 CURRENT_TIMESTAMP 기본값 사용
- 컬럼 메타데이터 지원: data_type, required, default_value, min_value, max_value, length
- 목록 메타데이터 지원: 페이지네이션, 정렬, 검색, 표시 모드 (table/card)
- 뷰 메타데이터는 필드 표시를 위해 사전 정의된 스타일 클래스 사용
