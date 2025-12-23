from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime

# --- Column Schema (based on docs/columns.md) ---

class ColumnField(BaseModel):
    name: str = Field(..., description="컬럼 영문 이름 (DB 컬럼명)")
    label: str = Field(..., description="컬럼 한글 라벨")
    data_type: str = Field(..., description="ymd, string, text, integer, float, boolean, datetime")
    required: bool = True
    default_value: Optional[Any] = None
    length: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None

class BoardMetaColumns(BaseModel):
    fields: List[ColumnField]

# --- Board API Schema ---

class BoardInfo(BaseModel):
    name: str = Field(..., description="게시판 이름")
    physical_table_name: str = Field(..., description="물리 테이블 이름")
    note: Optional[str] = None

class BoardCreate(BaseModel):
    board: BoardInfo
    columns: BoardMetaColumns

class BoardResponse(BaseModel):
    board_id: int
    message: str = "success"

class BoardDTO(BaseModel):
    id: int
    name: str
    physical_table_name: str
    note: Optional[str]
    created_at: datetime
    updated_at: datetime
