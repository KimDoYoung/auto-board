from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
import shutil
import uuid
import os
from datetime import datetime
from pathlib import Path
from typing import List
import sqlite3

from app.core.config import settings
from app.core.logger import get_logger
from app.core.deps import get_db_connection

logger = get_logger(__name__)

router = APIRouter(prefix="/api/files", tags=["files"])

@router.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """파일 업로드 API"""
    uploaded_files = []
    cursor = conn.cursor()

    try:
        # yyyy/mm 폴더 생성
        now = datetime.now()
        base_folder = now.strftime("%Y/%m")
        save_dir = settings.FILES_DIR / base_folder
        save_dir.mkdir(parents=True, exist_ok=True)

        for file in files:
            # UUID 생성 (하이픈 제거)
            physical_name = str(uuid.uuid4()).replace("-", "")
            file_path = save_dir / physical_name

            # 파일 저장
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # 파일 정보 저장
            file_size = os.path.getsize(file_path)
            logical_name = file.filename
            mime_type = file.content_type

            cursor.execute(
                """
                INSERT INTO files (base_folder, physical_name, logical_name, size, mime)
                VALUES (?, ?, ?, ?, ?)
                """,
                (base_folder, physical_name, logical_name, file_size, mime_type)
            )
            file_id = cursor.lastrowid
            
            uploaded_files.append({
                "id": file_id,
                "logical_name": logical_name,
                "size": file_size,
                "mime": mime_type
            })
            
            logger.info(f"[FILE] Uploaded: {logical_name} -> {base_folder}/{physical_name} (ID: {file_id})")

        conn.commit()
        return JSONResponse(uploaded_files, status_code=201)

    except Exception as e:
        conn.rollback()
        logger.error(f"[FILE] Upload failed: {e}")
        raise HTTPException(status_code=500, detail="File upload failed")

@router.get("/{file_id}")
async def download_file(
    file_id: int,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """파일 다운로드 API"""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT base_folder, physical_name, logical_name, mime FROM files WHERE id = ?",
        (file_id,)
    )
    row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="File not found")

    base_folder, physical_name, logical_name, mime_type = row
    file_path = settings.FILES_DIR / base_folder / physical_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Physical file not found")

    return FileResponse(
        path=file_path,
        filename=logical_name,
        media_type=mime_type
    )

@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """파일 삭제 API"""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT base_folder, physical_name FROM files WHERE id = ?", 
        (file_id,)
    )
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="File not found")

    base_folder, physical_name = row
    file_path = settings.FILES_DIR / base_folder / physical_name

    try:
        # DB 삭제 (file_match는 ON DELETE CASCADE가 없으므로 수동 삭제 필요)
        cursor.execute("DELETE FROM file_match WHERE file_id = ?", (file_id,))
        cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
        conn.commit()

        # 물리 파일 삭제
        if file_path.exists():
            os.remove(file_path)
            logger.info(f"[FILE] Deleted physical file: {file_path}")
        
        return JSONResponse({"message": "File deleted"}, status_code=200)

    except Exception as e:
        conn.rollback()
        logger.error(f"[FILE] Delete failed: {e}")
        raise HTTPException(status_code=500, detail="File delete failed")
