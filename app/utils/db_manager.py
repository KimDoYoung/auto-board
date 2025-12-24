
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.core.logger import get_logger
from app.schemas.board import BoardCreate, BoardResponse

logger = get_logger(__name__)

def map_sqlite_type(dtype: str) -> str:
    dtype = dtype.lower()
    if dtype in ["integer", "boolean"]: return "INTEGER"
    if dtype == "float": return "REAL"
    return "TEXT"

class DBManager:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.cursor = conn.cursor()

    def create_board(self, board_data: BoardCreate) -> BoardResponse:
        """
        게시판 생성 로직:
        1. boards 테이블에 메타 정보 insert
        2. meta_data 테이블에 컬럼 정의 insert
        3. 실제 물리 테이블 create
        """
        try:
            # 1. Insert into boards
            self.cursor.execute(
                """
                INSERT INTO boards (name, physical_table_name, note)
                VALUES (?, ?, ?)
                """,
                (board_data.board.name, board_data.board.physical_table_name, board_data.board.note)
            )
            board_id = self.cursor.lastrowid
            
            # 2. Prepare columns metadata JSON
            columns_json = board_data.columns.model_dump_json()
            
            # 3. Insert into meta_data
            self.cursor.execute(
                """
                INSERT INTO meta_data (board_id, name, meta, schema)
                VALUES (?, ?, ?, ?)
                """,
                (board_id, "columns", columns_json, "v1")
            )

            # 4. Create Physical Table
            ddl_columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
            for field in board_data.columns.fields:
                col_type = map_sqlite_type(field.data_type)
                nullable = "" if field.required else " NULL"
                ddl_columns.append(f"{field.name} {col_type}{nullable}")
            
            ddl_columns.append("created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            ddl_columns.append("updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            
            create_table_sql = f"CREATE TABLE {board_data.board.physical_table_name} ({', '.join(ddl_columns)})"
            
            logger.info(f"🛠 Executing DDL: {create_table_sql}")
            self.cursor.execute(create_table_sql)
            
            self.conn.commit()
            
            logger.info(f"✅ Board created: {board_data.board.name} (ID: {board_id})")
            return BoardResponse(board_id=board_id, message="success")

        except Exception as e:
            self.conn.rollback()
            logger.error(f"❌ Error creating board: {e}")
            raise e

    def get_board_columns(self, board_id: int) -> Dict[str, Any]:
        """게시판 컬럼 메타데이터 조회"""
        self.cursor.execute(
            "SELECT meta FROM meta_data WHERE board_id = ? AND name = ?",
            (board_id, "columns")
        )
        row = self.cursor.fetchone()
        if not row:
            return None
        
        try:
            return json.loads(row[0])
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in metadata")
