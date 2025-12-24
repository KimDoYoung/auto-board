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
async def wizard_step1_form(request: Request, user: User = Depends(get_current_user_from_cookie)):
    """Step 1: 기본 정보 및 컬럼 정의 페이지"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    return request.app.state.templates.TemplateResponse(
        "board/wizard_step1.html",
        {"request": request, "user": user}
    )

@router.post("/new/step1")
async def wizard_step1_submit(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Step 1: Board 생성 및 컬럼 메타데이터 저장"""
    try:
        form_data = await request.json()
        board_name = form_data.get("board_name")
        board_note = form_data.get("board_note", "")
        columns_data = form_data.get("columns", [])

        logger.info(f"🚀 Step 1 Submit: Creating board '{board_name}' with {len(columns_data)} columns")

        # DBManager를 사용해 board 생성
        db_manager = DBManager(conn)

        # 1. Board 생성
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO boards (name, note) VALUES (?, ?)",
            (board_name, board_note)
        )
        board_id = cursor.lastrowid

        # 2. 컬럼 메타데이터 저장
        columns_meta = {"fields": columns_data}
        db_manager.save_metadata(board_id, "columns", columns_meta)

        # 3. 물리 테이블 생성
        physical_table_name = f"table_{board_id}"

        # SQL 생성
        from app.utils.db_manager import map_sqlite_type
        ddl_columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        for field in columns_data:
            col_type = map_sqlite_type(field.get("data_type", "string"))
            nullable = "" if field.get("required", True) else " NULL"
            ddl_columns.append(f"{field['name']} {col_type}{nullable}")

        ddl_columns.append("created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        ddl_columns.append("updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

        create_table_sql = f"CREATE TABLE {physical_table_name} ({', '.join(ddl_columns)})"
        logger.info(f"🛠 Creating physical table: {create_table_sql}")
        cursor.execute(create_table_sql)

        # 4. Board의 physical_table_name 업데이트
        cursor.execute(
            "UPDATE boards SET physical_table_name = ? WHERE id = ?",
            (physical_table_name, board_id)
        )
        conn.commit()

        logger.info(f"✅ Board created: {board_name} (ID: {board_id})")
        return {"board_id": board_id, "redirect": f"/boards/new/step2/{board_id}"}

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

    columns_meta = db_manager.get_metadata(board_id, "columns") or {"fields": []}
    list_meta = db_manager.get_metadata(board_id, "list")

    return request.app.state.templates.TemplateResponse(
        "board/wizard_step2.html",
        {
            "request": request,
            "user": user,
            "board": board_info,
            "columns": columns_meta.get("fields", []),
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

    columns_meta = db_manager.get_metadata(board_id, "columns") or {"fields": []}
    create_meta = db_manager.get_metadata(board_id, "create")

    return request.app.state.templates.TemplateResponse(
        "board/wizard_step3.html",
        {
            "request": request,
            "user": user,
            "board": board_info,
            "columns": columns_meta.get("fields", []),
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

    columns_meta = db_manager.get_metadata(board_id, "columns") or {"fields": []}
    create_meta = db_manager.get_metadata(board_id, "create")
    edit_meta = db_manager.get_metadata(board_id, "edit")

    return request.app.state.templates.TemplateResponse(
        "board/wizard_step4.html",
        {
            "request": request,
            "user": user,
            "board": board_info,
            "columns": columns_meta.get("fields", []),
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
