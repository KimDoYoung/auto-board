# GEMINI.md

This file serves as the primary context for the Gemini agent when working on the `auto-board` project.

## Project Overview

**Auto-Board** is a personal, metadata-driven record management system. It allows users to create custom "boards" with user-defined fields (columns), storing definitions as JSON metadata and dynamically generating corresponding SQLite tables. It is designed as a single-user local application.

## Technology Stack

### Backend
- **Language:** Python 3.11+
- **Framework:** FastAPI
- **Templating:** Jinja2 (Server-side rendering)
- **Database:** SQLite (with dynamic table generation)
- **Auth:** JWT (Cookie-based), bcrypt
- **Package Manager:** `uv`

### Frontend
- **Styling:** Tailwind CSS
- **Interactivity:** Alpine.js (via CDN), Vanilla JavaScript
- **Editor:** Quill.js (Rich Text)
- **Build Tool:** `npm` (strictly for Tailwind CSS build and JS testing)

## Project Structure

```text
auto-board/
├── app/
│   ├── core/           # Config, Logging, Security, Deps
│   ├── routes/         # FastAPI Routes (board, home, records, etc.)
│   ├── schemas/        # Pydantic Models
│   ├── resources/      # SQL DDLs
│   ├── static/         # Static assets (CSS, JS)
│   ├── templates/      # Jinja2 HTML Templates
│   ├── utils/          # Database Manager & Utilities
│   └── main.py         # App Entry Point
├── docs/               # Design & Architecture Documentation
├── tests/              # Python Tests (pytest)
├── tests_js/           # JavaScript Tests (Jest)
├── .env.sample         # Sample Environment Variables
├── pyproject.toml      # Python Dependencies (uv)
└── package.json        # Node Dependencies & Scripts
```

## Development Workflow

### 1. Environment Setup

**Python (`uv`):**
```bash
uv venv
# Windows
.venv\Scripts\activate
# Unix
source .venv/bin/activate

uv sync
```

**Node.js (`npm`):**
```bash
npm install
```

**Environment Variables:**
Copy `.env.sample` to `.env` and set `AUTOBOARD_PROFILE=local`.

### 2. Running the Application

**Backend Server:**
```powershell
# Windows
$env:AUTOBOARD_PROFILE="local"; python -m uvicorn app.main:app --reload

# Unix
export AUTOBOARD_PROFILE=local && python -m uvicorn app.main:app --reload
```
*Access at: `http://localhost:8000` (Default Admin: `admin` / `admin123`)*

**CSS Watcher (Tailwind):**
```bash
npm run build:css
```

### 3. Testing

**Python (Backend):**
```bash
pytest
```

**JavaScript (Frontend):**
```bash
npm test
```

## Key Architectural Concepts

### Metadata-Driven Design
The core feature is the dynamic generation of boards.
1.  **Board Definition:** Stored in the `boards` table.
2.  **Metadata:** JSON configurations for columns, list views, detail views, and forms are stored in the `meta_data` table.
3.  **Physical Storage:** A real SQLite table (e.g., `table_1`) is created/altered based on the `columns` metadata.

### Data Flow
1.  User defines schema via Wizard (Step 1-4).
2.  `board.py` receives schema -> updates `meta_data` -> `db_manager.py` executes DDL to create/modify `table_{id}`.
3.  CRUD operations (`records.py`) read metadata to dynamically validate and map data to the physical table.

## Coding Conventions

-   **Python:** Type hints are mandatory. Use Pydantic for schemas. Follow PEP 8.
-   **JavaScript:** ES6+. Use functional patterns where possible. Files are in `app/static/js`.
-   **CSS:** Utility-first with Tailwind. Avoid custom CSS files unless necessary (`input.css`).
-   **Database:** Use `sqlite3.Row` for dict-like cursor access. Ensure connections are closed (handled by `deps.py`).
-   **Error Handling:** Use `try-except` blocks in routes and valid HTTP exceptions.

## Common Tasks

-   **Reset DB:** Delete `app.db` (or configured DB file) and restart the app.
-   **New Dependency:** Add to `pyproject.toml` (Python) or `package.json` (JS) and run sync/install.
-   **New Route:** Create file in `app/routes/`, router in `app/routes/__init__.py`, and include in `app/main.py`.
