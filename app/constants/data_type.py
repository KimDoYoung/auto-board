# app/constants/data_types.py
from enum import Enum
from typing import Dict, List, Any

# 필드 데이터 타입 Enum
# sqlite의 데이터 타입과 매핑됨
# step1의 데이터 타입 선택에 사용됨

class FieldDataType(str, Enum):
    STRING = "string"
    TEXT = "text"
    INTEGER = "integer"
    REAL = "real"
    BOOLEAN = "boolean"
    YMD = "ymd"
    DATETIME = "datetime"

# 클라이언트로 보낼 데이터 타입 정보
DATA_TYPES_CONFIG = [
    {
        "value": "string",
        "label": "문자열",
        "description": "짧은 텍스트 (예: 이름, 제목)",
        "sqliteType": "TEXT",
        "inputType": "text",
        "inputComponent": "input",
        "example": "홍길동",
        "hasLength": True,
        "hasMinMax": False,
        "hasOptions": False
    },
    {
        "value": "text",
        "label": "문장",
        "description": "긴 텍스트 (예: 내용, 설명)",
        "sqliteType": "TEXT",
        "inputType": "text",
        "inputComponent": "textarea",
        "example": "여러 줄의 긴 텍스트...",
        "hasLength": False,
        "hasMinMax": False,
        "hasOptions": False
    },
    {
        "value": "integer",
        "label": "정수",
        "description": "소수점 없는 숫자 (예: 수량, 평점)",
        "sqliteType": "INTEGER",
        "inputType": "number",
        "inputComponent": "input",
        "example": "100",
        "hasLength": False,
        "hasMinMax": True,
        "hasOptions": False
    },
    {
        "value": "real",
        "label": "실수",
        "description": "소수점 있는 숫자 (예: 가격, 무게)",
        "sqliteType": "REAL",
        "inputType": "number",
        "inputComponent": "input",
        "example": "99.99",
        "hasLength": False,
        "hasMinMax": True,
        "hasOptions": False,
        "step": "0.01"
    },
    {
        "value": "boolean",
        "label": "참/거짓",
        "description": "예/아니오 선택 (예: 공개여부, 완료여부)",
        "sqliteType": "INTEGER",
        "inputType": "checkbox",
        "inputComponent": "checkbox",
        "example": "true",
        "hasLength": False,
        "hasMinMax": False,
        "hasOptions": False
    },
    {
        "value": "ymd",
        "label": "날짜",
        "description": "년월일 (예: 2024-01-15)",
        "sqliteType": "TEXT",
        "inputType": "date",
        "inputComponent": "input",
        "example": "2024-01-15",
        "hasLength": False,
        "hasMinMax": False,
        "hasOptions": False
    },
    {
        "value": "datetime",
        "label": "날짜시간",
        "description": "년월일 시분초 (예: 2024-01-15 14:30:00)",
        "sqliteType": "TEXT",
        "inputType": "datetime-local",
        "inputComponent": "input",
        "example": "2024-01-15T14:30",
        "hasLength": False,
        "hasMinMax": False,
        "hasOptions": False
    }
]

def get_data_types_config() -> List[Dict[str, Any]]:
    """클라이언트용 데이터 타입 설정 반환"""
    return DATA_TYPES_CONFIG

# 빠른 조회용 딕셔너리
DATA_TYPES_MAP = {item["value"]: item for item in DATA_TYPES_CONFIG}