"""
Records API - 기록물(기록 아이템) 순수 CRUD API
각 보드의 실제 데이터 레코드를 JSON으로 반환
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
import sqlite3

from app.core.logger import get_logger
from app.core.deps import get_db_connection, get_current_user_from_cookie
from app.schemas.user import User
from app.utils.db_manager import DBManager

logger = get_logger(__name__)

router = APIRouter(prefix="/records", tags=["records"])


# ============================================================================
# HTML Pages
# ============================================================================

@router.get("/{board_id}/", response_class=HTMLResponse)
async def get_records_list(
    request: Request,
    board_id: int,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """기록물 목록 조회 (HTML)"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    logger.info(f"[RECORDS-LIST-1] board_id={board_id} 기록물 목록 조회 시작")

    db_manager = DBManager(conn)
    board_info = db_manager.get_board_info(board_id)

    if not board_info:
        logger.error(f"[RECORDS-LIST-ERROR] 보드를 찾을 수 없음: board_id={board_id}")
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    logger.info(f"[RECORDS-LIST-2] ✓ 보드 찾음: {board_info['name']}")

    # 컬럼 정보 조회
    table_meta = db_manager.get_metadata(board_id, "table") or {}
    columns = table_meta.get("columns", [])

    # 실제 레코드 조회
    physical_table_name = board_info["physical_table_name"]
    cursor = conn.cursor()

    try:
        cursor.execute(f"SELECT * FROM {physical_table_name} ORDER BY id DESC")
        records = [dict(row) for row in cursor.fetchall()]
        logger.info(f"[RECORDS-LIST-3] ✓ 레코드 조회 완료: {len(records)}개")
    except Exception as e:
        logger.error(f"[RECORDS-LIST-ERROR] 레코드 조회 실패: {e}")
        records = []

    return request.app.state.templates.TemplateResponse(
        "record/list.html",
        {
            "request": request,
            "user": user,
            "board": board_info,
            "records": records,
            "columns": columns
        }
    )


@router.get("/{board_id}/create", response_class=HTMLResponse)
async def record_create_page(
    request: Request,
    board_id: int,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """기록 생성 페이지"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    db_manager = DBManager(conn)
    board_info = db_manager.get_board_info(board_id)

    if not board_info:
        return RedirectResponse(url="/boards", status_code=status.HTTP_302_FOUND)

    table_meta = db_manager.get_metadata(board_id, "table") or {}
    columns_data = table_meta.get("columns", [])
    create_edit_config = db_manager.get_metadata(board_id, "create_edit")

    return request.app.state.templates.TemplateResponse(
        "record/create.html",
        {
            "request": request,
            "user": user,
            "board": board_info,
            "columns": columns_data,
            "table_meta": table_meta,
            "create_edit_config": create_edit_config
        }
    )


@router.get("/{board_id}/view/{record_id}", response_class=HTMLResponse)
async def record_view_page(
    request: Request,
    board_id: int,
    record_id: int,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """기록 상세보기 페이지"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    db_manager = DBManager(conn)
    board_info = db_manager.get_board_info(board_id)

    if not board_info:
        return RedirectResponse(url="/boards", status_code=status.HTTP_302_FOUND)

    table_meta = db_manager.get_metadata(board_id, "table") or {}
    columns_data = table_meta.get("columns", [])
    view_config = db_manager.get_metadata(board_id, "view")

    # 레코드 조회
    physical_table_name = board_info["physical_table_name"]
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {physical_table_name} WHERE id = ?", (record_id,))
    row = cursor.fetchone()

    if not row:
        return RedirectResponse(url=f"/records/{board_id}/", status_code=status.HTTP_302_FOUND)

    record = dict(row)

    return request.app.state.templates.TemplateResponse(
        "record/view.html",
        {
            "request": request,
            "user": user,
            "board": board_info,
            "record": record,
            "columns": columns_data,
            "view_config": view_config
        }
    )


@router.get("/{board_id}/edit/{record_id}", response_class=HTMLResponse)
async def record_edit_page(
    request: Request,
    board_id: int,
    record_id: int,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """기록 수정 페이지"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    db_manager = DBManager(conn)
    board_info = db_manager.get_board_info(board_id)

    if not board_info:
        return RedirectResponse(url="/boards", status_code=status.HTTP_302_FOUND)

    table_meta = db_manager.get_metadata(board_id, "table") or {}
    columns_data = table_meta.get("columns", [])
    create_edit_config = db_manager.get_metadata(board_id, "create_edit")

    # 레코드 조회
    physical_table_name = board_info["physical_table_name"]
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {physical_table_name} WHERE id = ?", (record_id,))
    row = cursor.fetchone()

    if not row:
        return RedirectResponse(url=f"/records/{board_id}/", status_code=status.HTTP_302_FOUND)

    record = dict(row)

    return request.app.state.templates.TemplateResponse(
        "record/edit.html",
        {
            "request": request,
            "user": user,
            "board": board_info,
            "record": record,
            "columns": columns_data,
            "create_edit_config": create_edit_config
        }
    )


# ============================================================================
# JSON APIs
# ============================================================================

@router.post("/api/{board_id}/")
async def create_record(
    board_id: int,
    form_data: dict,
    conn: sqlite3.Connection = Depends(get_db_connection),
    user: User = Depends(get_current_user_from_cookie)
):
    """새 기록 생성 (JSON)"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.info(f"[RECORD-CREATE-1] board_id={board_id} 새 기록 생성 시작")

    try:
        db_manager = DBManager(conn)
        board_info = db_manager.get_board_info(board_id)

        if not board_info:
            logger.error(f"[RECORD-CREATE-ERROR] 보드를 찾을 수 없음: board_id={board_id}")
            raise HTTPException(status_code=404, detail="Board not found")

        physical_table_name = board_info["physical_table_name"]
        cursor = conn.cursor()

        # 레코드 생성
        columns = list(form_data.keys())
        placeholders = ",".join(["?"] * len(columns))
        values = [form_data[col] for col in columns]

        insert_sql = f"INSERT INTO {physical_table_name} ({','.join(columns)}) VALUES ({placeholders})"
        logger.info(f"[RECORD-CREATE-2] SQL 실행: {insert_sql}")

        cursor.execute(insert_sql, values)
        record_id = cursor.lastrowid
        conn.commit()

        logger.info(f"[RECORD-CREATE-3] ✓ 레코드 생성 완료: record_id={record_id}")

        return {
            "success": True,
            "record_id": record_id,
            "board_id": board_id,
            "redirect": f"/records/{board_id}/"
        }

    except Exception as e:
        conn.rollback()
        logger.error(f"[RECORD-CREATE-ERROR] 예외 발생: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"[RECORD-CREATE-ERROR] 스택 트레이스:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/{board_id}/{record_id}")
async def get_record(
    board_id: int,
    record_id: int,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """기록 조회 (JSON)"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.info(f"[RECORD-VIEW-1] board_id={board_id}, record_id={record_id} 조회 시작")

    db_manager = DBManager(conn)
    board_info = db_manager.get_board_info(board_id)

    if not board_info:
        logger.error(f"[RECORD-VIEW-ERROR] 보드를 찾을 수 없음: board_id={board_id}")
        raise HTTPException(status_code=404, detail="Board not found")

    physical_table_name = board_info["physical_table_name"]
    cursor = conn.cursor()

    try:
        cursor.execute(f"SELECT * FROM {physical_table_name} WHERE id = ?", (record_id,))
        row = cursor.fetchone()

        if not row:
            logger.error(f"[RECORD-VIEW-ERROR] 레코드를 찾을 수 없음: record_id={record_id}")
            raise HTTPException(status_code=404, detail="Record not found")

        record = dict(row)
        logger.info(f"[RECORD-VIEW-2] ✓ 레코드 조회 완료: record_id={record_id}")

        return {
            "board_id": board_id,
            "board_name": board_info["name"],
            "record": record
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[RECORD-VIEW-ERROR] 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/{board_id}/{record_id}")
async def update_record(
    board_id: int,
    record_id: int,
    form_data: dict,
    conn: sqlite3.Connection = Depends(get_db_connection),
    user: User = Depends(get_current_user_from_cookie)
):
    """기록 수정 (JSON)"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.info(f"[RECORD-UPDATE-1] board_id={board_id}, record_id={record_id} 기록 수정 시작")

    try:
        db_manager = DBManager(conn)
        board_info = db_manager.get_board_info(board_id)

        if not board_info:
            logger.error(f"[RECORD-UPDATE-ERROR] 보드를 찾을 수 없음: board_id={board_id}")
            raise HTTPException(status_code=404, detail="Board not found")

        physical_table_name = board_info["physical_table_name"]
        cursor = conn.cursor()

        # id 제외하고 업데이트
        update_fields = [f"{col} = ?" for col in form_data.keys() if col != "id"]
        update_values = [form_data[col] for col in form_data.keys() if col != "id"]
        update_values.append(record_id)

        if not update_fields:
            logger.warning("[RECORD-UPDATE-2] 업데이트할 필드가 없습니다")
            # HTML 리다이렉트 경로 수정
            return {"success": True, "record_id": record_id, "redirect": f"/records/{board_id}/view/{record_id}"}

        update_sql = f"UPDATE {physical_table_name} SET {','.join(update_fields)} WHERE id = ?"
        logger.info(f"[RECORD-UPDATE-2] SQL 실행: {update_sql}")

        cursor.execute(update_sql, update_values)
        conn.commit()

        logger.info(f"[RECORD-UPDATE-3] ✓ 기록 수정 완료: record_id={record_id}")

        return {
            "success": True,
            "record_id": record_id,
            "board_id": board_id,
            "redirect": f"/records/{board_id}/view/{record_id}"
        }

    except Exception as e:
        conn.rollback()
        logger.error(f"[RECORD-UPDATE-ERROR] 예외 발생: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"[RECORD-UPDATE-ERROR] 스택 트레이스:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/{board_id}/{record_id}")
async def delete_record(
    board_id: int,
    record_id: int,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """기록 삭제 (JSON)"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.info(f"[RECORD-DELETE-1] board_id={board_id}, record_id={record_id} 기록 삭제 시작")

    try:
        db_manager = DBManager(conn)
        board_info = db_manager.get_board_info(board_id)

        if not board_info:
            logger.error(f"[RECORD-DELETE-ERROR] 보드를 찾을 수 없음: board_id={board_id}")
            raise HTTPException(status_code=404, detail="Board not found")

        physical_table_name = board_info["physical_table_name"]
        cursor = conn.cursor()

        # 레코드 삭제
        cursor.execute(f"DELETE FROM {physical_table_name} WHERE id = ?", (record_id,))
        conn.commit()

        logger.info(f"[RECORD-DELETE-2] ✓ 기록 삭제 완료: record_id={record_id}")

        return {
            "success": True,
            "record_id": record_id,
            "board_id": board_id
        }

    except Exception as e:
        conn.rollback()
        logger.error(f"[RECORD-DELETE-ERROR] 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))
