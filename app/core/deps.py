# deps.py
"""
모듈 설명: 
    - db 연결, 토큰 검증, 현재 사용자 가져오기
주요 기능:
    

작성자: 김도영
작성일: 2025-12-24
버전: 1.0
"""
from typing import Optional
from fastapi import Request
import jwt
from app.core.config import settings
from app.schemas.user import User  # Import schema
import sqlite3

def get_db_connection():
    conn = sqlite3.connect(settings.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

async def get_current_user_from_cookie(request: Request) -> Optional[User]:
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    # Bearer 제거 logic
    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except jwt.PyJWTError: 
        return None

    # DB에서 유저 확인
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin_users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row:
        # Convert row to dict, then to User model
        user_dict = dict(row)
        # SQLite's timestamp might need parsing if Pydantic complains, but typically it works.
        # However, to be safe, let Pydantic handle it.
        try:
            return User(**user_dict)
        except Exception:
            return None # Validation error fallback
    return None
