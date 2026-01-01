# app/constants/element_type.py
from enum import Enum
from typing import Dict, List, Any

# UI 요소 타입 Enum
# step3에서 각 필드의 UI 요소(element_type) 선택에 사용됨
# element_type은 JSON으로 저장되고, 렌더링 시 HTML input 요소로 변환됨

class ElementType(str, Enum):
    INPUT_TEXT = "input-text"
    INPUT_HTML = "input-html"
    INPUT_DATE = "input-date"
    INPUT_INTEGER = "input-integer"
    INPUT_REAL = "input-real"
    INPUT_EMAIL = "input-email"
    RADIO = "radio"
    CHECKBOX_MULTI = "checkbox-multi"
    CHECKBOX = "checkbox"


# 클라이언트로 보낼 element_type 정보
ELEMENT_TYPES_CONFIG = [
    {
        "value": "input-text",
        "label": "문자열",
        "description": "텍스트 입력 (한 줄)",
        "htmlElement": "input",
        "htmlType": "text",
        "example": "홍길동",
        "hasOptions": False,
        "hasValidation": True
    },
    {
        "value": "input-html",
        "label": "문장",
        "description": "긴 텍스트 (여러 줄, HTML 지원)",
        "htmlElement": "textarea",
        "htmlType": None,
        "example": "여러 줄의 긴 텍스트...",
        "hasOptions": False,
        "hasValidation": False
    },
    {
        "value": "input-date",
        "label": "날짜",
        "description": "날짜 선택",
        "htmlElement": "input",
        "htmlType": "date",
        "example": "2024-01-15",
        "hasOptions": False,
        "hasValidation": False
    },
    {
        "value": "input-integer",
        "label": "정수",
        "description": "정수 입력 (소수점 불가)",
        "htmlElement": "input",
        "htmlType": "number",
        "example": "100",
        "hasOptions": False,
        "hasValidation": True
    },
    {
        "value": "input-real",
        "label": "실수",
        "description": "실수 입력 (소수점 포함)",
        "htmlElement": "input",
        "htmlType": "number",
        "example": "99.99",
        "hasOptions": False,
        "hasValidation": True,
        "step": "0.01"
    },
    {
        "value": "input-email",
        "label": "이메일",
        "description": "이메일 주소 입력",
        "htmlElement": "input",
        "htmlType": "email",
        "example": "user@example.com",
        "hasOptions": False,
        "hasValidation": False
    },
    {
        "value": "radio",
        "label": "라디오 버튼",
        "description": "하나의 선택지만 선택 가능",
        "htmlElement": "input",
        "htmlType": "radio",
        "example": "option1",
        "hasOptions": True,
        "hasValidation": False
    },
    {
        "value": "checkbox-multi",
        "label": "체크박스 (다중)",
        "description": "여러 개의 선택지를 선택 가능",
        "htmlElement": "input",
        "htmlType": "checkbox",
        "example": "[\"option1\", \"option2\"]",
        "hasOptions": True,
        "hasValidation": False
    },
    {
        "value": "checkbox",
        "label": "체크박스",
        "description": "참/거짓 선택",
        "htmlElement": "input",
        "htmlType": "checkbox",
        "example": "true",
        "hasOptions": False,
        "hasValidation": False
    }
]


def get_element_types_config() -> List[Dict[str, Any]]:
    """클라이언트용 element_type 설정 반환"""
    return ELEMENT_TYPES_CONFIG


# 빠른 조회용 딕셔너리
ELEMENT_TYPES_MAP = {item["value"]: item for item in ELEMENT_TYPES_CONFIG}


def get_element_type_by_data_type(data_type: str) -> str:
    """
    data_type으로부터 권장 element_type을 반환

    Args:
        data_type: FieldDataType 값 (string, text, integer, real, boolean, ymd, datetime)

    Returns:
        ElementType 값
    """
    mapping = {
        "string": "input-text",
        "text": "input-html",
        "integer": "input-integer",
        "real": "input-real",
        "boolean": "checkbox",
        "ymd": "input-date",
        "datetime": "input-date"
    }
    return mapping.get(data_type, "input-text")
