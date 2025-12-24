from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import sqlite3

from app.core.config import settings
from app.core.logger import get_logger
from app.core.deps import get_db_connection, get_current_user_from_cookie
from app.schemas.board import BoardCreate, BoardResponse
from app.schemas.user import User
from app.utils.db_manager import DBManager

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
    게시판 생성 API (Delegates to DBManager)
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
