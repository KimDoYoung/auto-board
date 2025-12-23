# app/routes/board.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import List, Dict, Any
import sqlite3
import json

from app.core.config import settings
from app.core.logger import get_logger
from app.core.deps import get_db_connection, get_current_user_from_cookie
from app.schemas.board import BoardCreate, BoardResponse, BoardMetaColumns
from app.schemas.user import User

logger = get_logger(__name__)

router = APIRouter(prefix="/boards", tags=["boards"])

@router.get("/create", response_class=HTMLResponse)
async def create_board_page(request: Request, user: User = Depends(get_current_user_from_cookie)):
    """게시판 생성 페이지"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
        
    return request.app.state.templates.TemplateResponse(
        "board/create.html", 
        {"request": request, "user": user}
    )

@router.post("/create", response_model=BoardResponse)
def create_board(
    board_data: BoardCreate,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """
    게시판 생성 API
    1. boards 테이블에 레코드 추가
    2. fields 정보를 meta_data 테이블에 'columns' 타입으로 저장
    """
    logger.info(f"🚀 Received Board Creation Request (Sync): {board_data.board.name}")
    cursor = conn.cursor()
    try:
        # 1. Insert into boards
        cursor.execute(
            """
            INSERT INTO boards (name, physical_table_name, note)
            VALUES (?, ?, ?)
            """,
            (board_data.board.name, board_data.board.physical_table_name, board_data.board.note)
        )
        board_id = cursor.lastrowid
        
        # 2. Prepare columns metadata JSON
        columns_json = board_data.columns.model_dump_json() # Pydantic v2
        
        # 3. Insert into meta_data
        cursor.execute(
            """
            INSERT INTO meta_data (board_id, name, meta, schema)
            VALUES (?, ?, ?, ?)
            """,
            (board_id, "columns", columns_json, "v1")
        )

        # 4. Create Physical Table
        def map_sqlite_type(dtype: str) -> str:
            dtype = dtype.lower()
            if dtype in ["integer", "boolean"]: return "INTEGER"
            if dtype == "float": return "REAL"
            return "TEXT"

        ddl_columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        for field in board_data.columns.fields:
            col_type = map_sqlite_type(field.data_type)
            nullable = "" if field.required else " NULL"
            ddl_columns.append(f"{field.name} {col_type}{nullable}")
        
        ddl_columns.append("created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        ddl_columns.append("updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        
        create_table_sql = f"CREATE TABLE {board_data.board.physical_table_name} ({', '.join(ddl_columns)})"
        
        logger.info(f"🛠 Executing DDL: {create_table_sql}")
        cursor.execute(create_table_sql)
        
        conn.commit()
        
        logger.info(f"✅ Board created: {board_data.board.name} (ID: {board_id})")
        return BoardResponse(board_id=board_id, message="success")

    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error creating board: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{board_id}/columns")
def get_board_columns(
    board_id: int,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """
    게시판 컬럼 메타데이터 조회
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT meta FROM meta_data WHERE board_id = ? AND name = ?",
        (board_id, "columns")
    )
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Columns metadata not found")
    
    try:
        meta_json = json.loads(row[0])
        return meta_json
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in metadata")
