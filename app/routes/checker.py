from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import sqlite3
import json

from app.core.logger import get_logger
from app.core.deps import get_db_connection, get_current_user_from_cookie
from app.schemas.user import User
from app.utils.db_manager import DBManager

logger = get_logger(__name__)

router = APIRouter(prefix="/checker", tags=["checker"])

@router.get("/{board_id}", response_class=HTMLResponse)
async def check_board(
    request: Request,
    board_id: int,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """보드 상태 확인 (Metadata & Info)"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    logger.info(f"[CHECKER] board_id={board_id} 상태 확인")

    db_manager = DBManager(conn)
    board_info = db_manager.get_board_info(board_id)

    if not board_info:
        raise HTTPException(status_code=404, detail="Board not found")

    # 1. Board Info (Already fetched)
    
    # 2. Meta Data (All rows for this board)
    cursor = conn.cursor()
    cursor.execute("SELECT key, data, created_at, updated_at FROM meta_data WHERE board_id = ? ORDER BY key", (board_id,))
    meta_rows = cursor.fetchall()

    meta_data_list = []
    for row in meta_rows:
        key = row[0]
        data_str = row[1]
        try:
            # Try to parse JSON for pretty printing
            data_json = json.loads(data_str)
            data_pretty = json.dumps(data_json, indent=4, ensure_ascii=False)
        except:
            data_pretty = data_str

        meta_data_list.append({
            "key": key,
            "data": data_pretty,
            "created_at": row[2],
            "updated_at": row[3]
        })

    return request.app.state.templates.TemplateResponse(
        "checker.html",
        {
            "request": request,
            "user": user,
            "board": board_info,
            "meta_data_list": meta_data_list
        }
    )
