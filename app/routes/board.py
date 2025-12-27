from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import sqlite3

from app.core.logger import get_logger
from app.core.deps import get_db_connection, get_current_user_from_cookie
from app.schemas.board import BoardCreate, BoardResponse
from app.schemas.user import User
from app.utils.db_manager import DBManager

logger = get_logger(__name__)

router = APIRouter(prefix="/boards", tags=["boards"])

# ============================================================================
# 5-Step Board Creation Wizard
# ============================================================================

# Step 1: 테이블 생성 (컬럼 정의)
@router.get("/new/step1", response_class=HTMLResponse)
async def wizard_step1_form(
    request: Request,
    board_id: Optional[int] = None,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Step 1: 기본 정보 및 컬럼 정의 페이지 (신규 생성 또는 기존 수정)"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    board_info = None
    columns_data = None
    board_meta = None

    # board_id가 있으면 기존 데이터 조회
    if board_id:
        db_manager = DBManager(conn)
        board_info = db_manager.get_board_info(board_id)
        if not board_info:
            return RedirectResponse(url="/boards/new/step1", status_code=status.HTTP_302_FOUND)

        board_meta = db_manager.get_metadata(board_id, "table") or {}
        columns_data = board_meta.get("columns", [])

    return request.app.state.templates.TemplateResponse(
        "board/wizard_step1.html",
        {
            "request": request,
            "user": user,
            "board": board_info,
            "board_meta": board_meta,
            "columns": columns_data,
            "board_id": board_id
        }
    )

@router.post("/new/step1")
async def wizard_step1_submit(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Step 1: Board 생성 및 컬럼 메타데이터 저장 (신규 생성 또는 기존 수정)"""
    try:
        form_data = await request.json()
        board_id = form_data.get("board_id")  # 수정 모드인지 신규 모드인지 판단
        board_name = form_data.get("name")
        board_note = form_data.get("note", "")
        is_file_attach = form_data.get("is_file_attach", False)
        columns_data = form_data.get("columns", [])

        db_manager = DBManager(conn)
        cursor = conn.cursor()

        # ===== 신규 생성 모드 =====
        if not board_id:
            logger.info(f"🚀 Step 1 Submit: Creating NEW board '{board_name}' with {len(columns_data)} columns")

            # 1. 최대 ID를 구해서 다음 ID 계산
            cursor.execute("SELECT MAX(id) FROM boards")
            result = cursor.fetchone()
            next_board_id = (result[0] or 0) + 1
            physical_table_name = f"table_{next_board_id}"

            # 2. Board 신규 생성 (physical_table_name 포함)
            cursor.execute(
                "INSERT INTO boards (name, note, physical_table_name) VALUES (?, ?, ?)",
                (board_name, board_note, physical_table_name)
            )
            board_id = cursor.lastrowid

            # 3. 컬럼명 자동 생성 및 메타데이터 준비 (설계 문서 준수)
            columns_with_names = []
            for idx, field in enumerate(columns_data, 1):
                col_name = f"col{idx}"
                col_data = {
                    "label": field.get("label"),
                    "data_type": field.get("data_type"),
                    "name": col_name
                }

                # comment는 선택사항
                if field.get("comment"):
                    col_data["comment"] = field.get("comment")

                columns_with_names.append(col_data)

            columns_meta = {
                "name": board_name,
                "note": board_note,
                "is_file_attach": is_file_attach,
                "physical_table_name": physical_table_name,
                "id": board_id,
                "columns": columns_with_names
            }
            db_manager.save_metadata(board_id, "table", columns_meta)

            # 4. 물리 테이블 생성
            from app.utils.db_manager import map_sqlite_type
            ddl_columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
            for field in columns_with_names:
                col_type = map_sqlite_type(field.get("data_type", "string"))
                col_name = field.get("name")
                # comment가 없으면 label을 comment로 사용
                col_comment = field.get("comment") or field.get("label")
                ddl_columns.append(f"{col_name} {col_type} -- {col_comment}")

            ddl_columns.append("created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            ddl_columns.append("updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

            create_table_sql = f"CREATE TABLE {physical_table_name} ({', '.join(ddl_columns)})"
            logger.info(f"🛠 Creating physical table: {create_table_sql}")
            cursor.execute(create_table_sql)

            # 5. 테이블 검증 로깅
            cursor.execute(f"PRAGMA table_info({physical_table_name})")
            table_info = cursor.fetchall()
            logger.info(f"✅ Table '{physical_table_name}' created successfully")
            logger.info(f"📋 Table structure (PRAGMA table_info):")
            for col in table_info:
                logger.info(f"   - {col[1]}: {col[2]} (notnull={col[3]}, pk={col[5]})")

            conn.commit()
            logger.info(f"✅ Board created: {board_name} (ID: {board_id}, Table: {physical_table_name})")

        # ===== 수정 모드 =====
        else:
            logger.info(f"🚀 Step 1 Submit: Updating board (ID: {board_id}) '{board_name}'")

            # 1. 기존 Board 정보 조회
            existing_board = db_manager.get_board_info(board_id)
            if not existing_board:
                raise HTTPException(status_code=404, detail="Board not found")

            physical_table_name = existing_board["physical_table_name"]

            # 2. Board 정보 UPDATE
            cursor.execute(
                "UPDATE boards SET name = ?, note = ? WHERE id = ?",
                (board_name, board_note, board_id)
            )

            # 3. 컬럼명 자동 생성 및 메타데이터 준비
            columns_with_names = []
            for idx, field in enumerate(columns_data, 1):
                col_name = f"col{idx}"
                col_data = {
                    "label": field.get("label"),
                    "data_type": field.get("data_type"),
                    "name": col_name
                }

                if field.get("comment"):
                    col_data["comment"] = field.get("comment")

                columns_with_names.append(col_data)

            columns_meta = {
                "name": board_name,
                "note": board_note,
                "is_file_attach": is_file_attach,
                "physical_table_name": physical_table_name,
                "id": board_id,
                "columns": columns_with_names
            }

            # 4. 메타데이터 UPDATE (save_metadata는 UPSERT 처리)
            db_manager.save_metadata(board_id, "table", columns_meta)

            # 5. 물리 테이블 DROP -> CREATE (수정 모드는 항상 재생성)
            logger.info(f"🔄 Updating table structure for board {board_id}...")

            # 5-1. 기존 테이블에 데이터가 있는지 확인
            cursor.execute(f"SELECT COUNT(*) FROM {physical_table_name}")
            record_count = cursor.fetchone()[0]

            if record_count > 0:
                logger.warning(f"⚠️ Table {physical_table_name} has {record_count} existing record(s). Cannot modify structure.")
                conn.rollback()
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot modify table structure when {record_count} record(s) exist. Please delete all records first."
                )

            # 5-2. 기존 테이블 DROP
            cursor.execute(f"DROP TABLE {physical_table_name}")
            logger.info(f"🗑️ Dropped table {physical_table_name}")

            # 5-3. 새 테이블 생성
            from app.utils.db_manager import map_sqlite_type
            ddl_columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
            for field in columns_with_names:
                col_type = map_sqlite_type(field.get("data_type", "string"))
                col_name = field.get("name")
                col_comment = field.get("comment") or field.get("label")
                ddl_columns.append(f"{col_name} {col_type} -- {col_comment}")

            ddl_columns.append("created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            ddl_columns.append("updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

            create_table_sql = f"CREATE TABLE {physical_table_name} ({', '.join(ddl_columns)})"
            logger.info(f"🛠 Recreating physical table: {create_table_sql}")
            cursor.execute(create_table_sql)

            # 5-4. 테이블 검증
            cursor.execute(f"PRAGMA table_info({physical_table_name})")
            table_info = cursor.fetchall()
            logger.info(f"✅ Table '{physical_table_name}' recreated successfully")
            logger.info(f"📋 Table structure (PRAGMA table_info):")
            for col in table_info:
                logger.info(f"   - {col[1]}: {col[2]} (notnull={col[3]}, pk={col[5]})")

            conn.commit()
            logger.info(f"✅ Board updated: {board_name} (ID: {board_id}, Table: {physical_table_name})")

        return {"board_id": board_id, "redirect": f"/boards/new/step2/{board_id}"}

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error in Step 1: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Step 2: 목록 설정
@router.get("/new/step2/{board_id}", response_class=HTMLResponse)
async def wizard_step2_form(
    request: Request,
    board_id: int,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Step 2: 목록 화면 설정"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    db_manager = DBManager(conn)
    board_info = db_manager.get_board_info(board_id)

    if not board_info:
        return RedirectResponse(url="/boards/new/step1", status_code=status.HTTP_302_FOUND)

    table_meta = db_manager.get_metadata(board_id, "table") or {}
    columns_data = table_meta.get("columns", [])
    list_meta = db_manager.get_metadata(board_id, "list")

    return request.app.state.templates.TemplateResponse(
        "board/wizard_step2.html",
        {
            "request": request,
            "user": user,
            "board": board_info,
            "columns": columns_data,
            "list_config": list_meta
        }
    )

@router.post("/new/step2/{board_id}")
async def wizard_step2_submit(
    board_id: int,
    request: Request,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Step 2: 목록 설정 저장"""
    try:
        form_data = await request.json()
        list_config = form_data.get("list_config", {})

        logger.info(f"🚀 Step 2 Submit: Saving list config for board {board_id}")

        db_manager = DBManager(conn)
        db_manager.save_metadata(board_id, "list", list_config)

        logger.info(f"✅ List config saved for board {board_id}")
        return {"redirect": f"/boards/new/step3/{board_id}"}

    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error in Step 2: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Step 3: 입력폼 설정
@router.get("/new/step3/{board_id}", response_class=HTMLResponse)
async def wizard_step3_form(
    request: Request,
    board_id: int,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Step 3: 입력 화면 설정"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    db_manager = DBManager(conn)
    board_info = db_manager.get_board_info(board_id)

    if not board_info:
        return RedirectResponse(url="/boards/new/step1", status_code=status.HTTP_302_FOUND)

    table_meta = db_manager.get_metadata(board_id, "table") or {}
    columns_data = table_meta.get("columns", [])
    create_meta = db_manager.get_metadata(board_id, "create")

    return request.app.state.templates.TemplateResponse(
        "board/wizard_step3.html",
        {
            "request": request,
            "user": user,
            "board": board_info,
            "columns": columns_data,
            "create_config": create_meta
        }
    )

@router.post("/new/step3/{board_id}")
async def wizard_step3_submit(
    board_id: int,
    request: Request,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Step 3: 입력 설정 저장"""
    try:
        form_data = await request.json()
        create_config = form_data.get("create_config", {})

        logger.info(f"🚀 Step 3 Submit: Saving create config for board {board_id}")

        db_manager = DBManager(conn)
        db_manager.save_metadata(board_id, "create", create_config)

        logger.info(f"✅ Create config saved for board {board_id}")
        return {"redirect": f"/boards/new/step4/{board_id}"}

    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error in Step 3: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Step 4: 수정폼 설정
@router.get("/new/step4/{board_id}", response_class=HTMLResponse)
async def wizard_step4_form(
    request: Request,
    board_id: int,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Step 4: 수정 화면 설정"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    db_manager = DBManager(conn)
    board_info = db_manager.get_board_info(board_id)

    if not board_info:
        return RedirectResponse(url="/boards/new/step1", status_code=status.HTTP_302_FOUND)

    table_meta = db_manager.get_metadata(board_id, "table") or {}
    columns_data = table_meta.get("columns", [])
    create_meta = db_manager.get_metadata(board_id, "create")
    edit_meta = db_manager.get_metadata(board_id, "edit")

    return request.app.state.templates.TemplateResponse(
        "board/wizard_step4.html",
        {
            "request": request,
            "user": user,
            "board": board_info,
            "columns": columns_data,
            "create_config": create_meta,
            "edit_config": edit_meta
        }
    )

@router.post("/new/step4/{board_id}")
async def wizard_step4_submit(
    board_id: int,
    request: Request,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Step 4: 수정 설정 저장"""
    try:
        form_data = await request.json()
        edit_config = form_data.get("edit_config", {})

        logger.info(f"🚀 Step 4 Submit: Saving edit config for board {board_id}")

        db_manager = DBManager(conn)
        db_manager.save_metadata(board_id, "edit", edit_config)

        logger.info(f"✅ Edit config saved for board {board_id}")
        return {"redirect": f"/boards/new/finish/{board_id}"}

    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error in Step 4: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Finish: 완료 확인
@router.get("/new/finish/{board_id}", response_class=HTMLResponse)
async def wizard_finish(
    request: Request,
    board_id: int,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """보드 생성 완료 페이지"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    db_manager = DBManager(conn)
    board_info = db_manager.get_board_info(board_id)

    if not board_info:
        return RedirectResponse(url="/boards/new/step1", status_code=status.HTTP_302_FOUND)

    return request.app.state.templates.TemplateResponse(
        "board/wizard_finish.html",
        {
            "request": request,
            "user": user,
            "board": board_info
        }
    )

# ============================================================================
# Legacy Endpoints (for backward compatibility)
# ============================================================================

@router.get("/create", response_class=HTMLResponse)
async def create_board_page(user: User = Depends(get_current_user_from_cookie)):
    """게시판 생성 페이지 (레거시 - /new/step1로 리다이렉트)"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    return RedirectResponse(url="/boards/new/step1", status_code=status.HTTP_302_FOUND)

@router.post("/create", response_model=BoardResponse)
def create_board(
    board_data: BoardCreate,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """
    게시판 생성 API (레거시 - 호환성 유지)
    """
    logger.info(f"🚀 Received Board Creation Request: {board_data.board.name}")
    try:
        db_manager = DBManager(conn)
        return db_manager.create_board(board_data)
    except Exception as e:
        # DBManager already logs error
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{board_id}/columns")
def get_board_columns(
    board_id: int,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """
    게시판 컬럼 메타데이터 조회 (Delegates to DBManager)
    """
    db_manager = DBManager(conn)
    result = db_manager.get_board_columns(board_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Columns metadata not found")

    return result
