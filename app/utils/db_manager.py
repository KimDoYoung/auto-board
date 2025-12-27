
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
        2. meta_data 테이블에 컬럼 정의 insert (설계 문서 준수)
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

            # 2. Prepare columns metadata JSON (설계 문서 형식 준수)
            table_meta = {
                "name": board_data.board.name,
                "note": board_data.board.note,
                "is_file_attach": getattr(board_data.board, 'is_file_attach', False),
                "physical_table_name": board_data.board.physical_table_name,
                "id": board_id,
                "columns": [field.model_dump() for field in board_data.columns.fields]
            }
            table_meta_json = json.dumps(table_meta, ensure_ascii=False)

            # 3. Insert into meta_data with name="table"
            self.cursor.execute(
                """
                INSERT INTO meta_data (board_id, name, meta, schema)
                VALUES (?, ?, ?, ?)
                """,
                (board_id, "table", table_meta_json, "v1")
            )

            # 4. Create Physical Table
            ddl_columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
            for field in board_data.columns.fields:
                col_type = map_sqlite_type(field.data_type)
                ddl_columns.append(f"{field.name} {col_type}")

            ddl_columns.append("created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            ddl_columns.append("updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

            create_table_sql = f"CREATE TABLE {board_data.board.physical_table_name} ({', '.join(ddl_columns)})"

            logger.info(f"🛠 Executing DDL: {create_table_sql}")
            self.cursor.execute(create_table_sql)

            # 5. 테이블 검증 로깅
            cursor = self.conn.cursor()
            cursor.execute(f"PRAGMA table_info({board_data.board.physical_table_name})")
            table_info = cursor.fetchall()
            logger.info(f"✅ Table '{board_data.board.physical_table_name}' created successfully")
            logger.info(f"📋 Table structure (PRAGMA table_info):")
            for col in table_info:
                logger.info(f"   - {col[1]}: {col[2]} (notnull={col[3]}, pk={col[5]})")

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
            (board_id, "table")
        )
        row = self.cursor.fetchone()
        if not row:
            return None

        try:
            meta = json.loads(row[0])
            # 설계 문서에 맞게 columns 배열 추출
            return {"fields": meta.get("columns", [])}
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in metadata")

    def get_board_info(self, board_id: int) -> Optional[Dict[str, Any]]:
        """보드 정보 조회"""
        self.cursor.execute(
            "SELECT id, name, physical_table_name, note, created_at, updated_at FROM boards WHERE id = ?",
            (board_id,)
        )
        row = self.cursor.fetchone()
        if not row:
            return None

        return {
            "id": row[0],
            "name": row[1],
            "physical_table_name": row[2],
            "note": row[3],
            "created_at": row[4],
            "updated_at": row[5]
        }

    def save_metadata(self, board_id: int, name: str, meta: Dict[str, Any]) -> None:
        """메타데이터 저장 (upsert)"""
        try:
            meta_json = json.dumps(meta, ensure_ascii=False)

            # 기존 메타데이터 확인
            self.cursor.execute(
                "SELECT id FROM meta_data WHERE board_id = ? AND name = ?",
                (board_id, name)
            )
            existing = self.cursor.fetchone()

            if existing:
                # 업데이트
                self.cursor.execute(
                    "UPDATE meta_data SET meta = ? WHERE board_id = ? AND name = ?",
                    (meta_json, board_id, name)
                )
            else:
                # 새로 생성
                self.cursor.execute(
                    "INSERT INTO meta_data (board_id, name, meta, schema) VALUES (?, ?, ?, ?)",
                    (board_id, name, meta_json, "v1")
                )

            self.conn.commit()
            logger.info(f"✅ Metadata saved: board_id={board_id}, name={name}")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"❌ Error saving metadata: {e}")
            raise e

    def get_metadata(self, board_id: int, name: str) -> Optional[Dict[str, Any]]:
        """메타데이터 조회"""
        self.cursor.execute(
            "SELECT meta FROM meta_data WHERE board_id = ? AND name = ?",
            (board_id, name)
        )
        row = self.cursor.fetchone()
        if not row:
            return None

        try:
            return json.loads(row[0])
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in metadata")
