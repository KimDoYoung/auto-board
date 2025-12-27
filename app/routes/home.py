# app/routes/home.py
"""
작성자: 김도영
작성일: 2025-12-23
버전: 1.1 - Added Login/Logout/Auth logic
"""
from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import timedelta
from typing import Optional

from app.core.config import settings
from app.core.logger import get_logger
from app.core.security import create_access_token, verify_password
from app.core.deps import get_current_user_from_cookie, get_db_connection
from app.schemas.user import User
from app.utils.db_manager import DBManager
import sqlite3

logger = get_logger(__name__)

router = APIRouter()

# 템플릿 사용을 위한 헬퍼
def get_templates(request: Request) -> Jinja2Templates:
    return request.app.state.templates

@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    user: Optional[User] = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """메인 페이지 - 로그인 상태에 따라 분기"""
    templates = get_templates(request)

    if user:
        # 로그인 상태 -> index.html (Dashboard)
        # 보드 목록 조회
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, note, created_at FROM boards ORDER BY id DESC")
        boards = [dict(row) for row in cursor.fetchall()]

        return templates.TemplateResponse(
            "index.html",
            {"request": request, "user": user, "boards": boards}
        )
    else:
        # 비로그인 상태 -> login.html
        return templates.TemplateResponse("login.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, user: Optional[User] = Depends(get_current_user_from_cookie)):
    """로그인 페이지"""
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    templates = get_templates(request)
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """로그인 처리"""
    templates = get_templates(request)
    
    # DB에서 유저 확인
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin_users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or not verify_password(password, user["password"]):
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "아이디 또는 비밀번호가 올바르지 않습니다."}
        )
    
    # 토큰 생성
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    # 쿠키 설정 및 리다이렉트
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response

@router.get("/logout")
async def logout(request: Request):
    """로그아웃"""
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response
