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


# --- List Metadata Schema (based on docs/list.md) ---

class ListColumn(BaseModel):
    """목록 화면에 표시할 컬럼"""
    name: str = Field(..., description="컬럼 이름")
    label: str = Field(..., description="표시할 라벨")
    width: Optional[str] = None
    align: Optional[str] = "left"

class ListPagination(BaseModel):
    """페이지네이션 설정"""
    enabled: bool = True
    page_size: int = 20

class ListSort(BaseModel):
    """정렬 설정"""
    enabled: bool = True
    column: Optional[str] = "id"
    order: str = "desc"  # asc, desc

class ListSearch(BaseModel):
    """검색 설정"""
    enabled: bool = True
    searchable_columns: List[str] = []

class BoardMetaList(BaseModel):
    """목록 메타데이터"""
    columns: List[ListColumn] = []
    display_mode: str = "table"  # table, card
    pagination: ListPagination = ListPagination()
    sort: ListSort = ListSort()
    search: ListSearch = ListSearch()


# --- Form Metadata Schema (for create/edit) ---

class FormField(BaseModel):
    """폼의 입력 필드"""
    name: str = Field(..., description="컬럼 이름")
    label: str = Field(..., description="필드 라벨")
    input_type: str = Field(..., description="text, textarea, number, select, date, etc")
    required: bool = True
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    rows: Optional[int] = None  # for textarea
    options: Optional[List[dict]] = None  # for select

class FormSection(BaseModel):
    """폼의 섹션"""
    title: Optional[str] = None
    fields: List[FormField] = []

class BoardMetaCreate(BaseModel):
    """생성 폼 메타데이터"""
    sections: List[FormSection] = []

class BoardMetaEdit(BaseModel):
    """수정 폼 메타데이터"""
    sections: List[FormSection] = []


# --- View Metadata Schema (based on docs/view.md) ---

class ViewField(BaseModel):
    """상세 보기 필드"""
    name: str = Field(..., description="컬럼 이름")
    label: str = Field(..., description="필드 라벨")
    style_class: Optional[str] = None
    display_type: str = "text"  # text, html, date, etc

class ViewSection(BaseModel):
    """상세 보기 섹션"""
    title: Optional[str] = None
    fields: List[ViewField] = []

class BoardMetaView(BaseModel):
    """상세 보기 메타데이터"""
    sections: List[ViewSection] = []
