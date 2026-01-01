# app/constants/display_type.py
from enum import Enum
from typing import Dict, List, Any

# 데이터 표시 타입 Enum
# view/list 메타데이터에서 각 필드를 어떻게 렌더링할지 정의
# step4에서 각 필드의 표시 방식(display_type) 선택에 사용됨

class DisplayType(str, Enum):
    # 필수 핵심 (6개)
    TEXT = "text"
    HTML = "html"
    DATE = "date"
    NUMBER = "number"
    IMAGE = "image"
    FILE = "file"
    # 추가 (4개)
    STARS = "stars"
    BOOLEAN = "boolean"
    TAGS = "tags"
    CURRENCY = "currency"


# 클라이언트로 보낼 display_type 정보
DISPLAY_TYPES_CONFIG = [
    # 필수 핵심 (6개)
    {
        "value": "text",
        "label": "텍스트",
        "description": "일반 텍스트로 표시",
        "htmlElement": "span",
        "htmlClass": "text-gray-700",
        "example": "홍길동",
        "supportsFormatting": False,
        "requiresFile": False,
        "isCore": True
    },
    {
        "value": "html",
        "label": "HTML",
        "description": "렌더링된 HTML로 표시 (리치 텍스트)",
        "htmlElement": "div",
        "htmlClass": "html-content prose prose-sm",
        "example": "<p>렌더링된 <strong>HTML</strong> 내용</p>",
        "supportsFormatting": True,
        "requiresFile": False,
        "isCore": True
    },
    {
        "value": "date",
        "label": "날짜",
        "description": "포맷된 날짜로 표시 (예: 2024년 1월 1일)",
        "htmlElement": "span",
        "htmlClass": "text-gray-700",
        "example": "2024년 1월 1일",
        "supportsFormatting": False,
        "requiresFile": False,
        "isCore": True,
        "dateFormat": "YYYY년 M월 D일"
    },
    {
        "value": "number",
        "label": "숫자",
        "description": "천단위 콤마가 적용된 숫자로 표시",
        "htmlElement": "span",
        "htmlClass": "text-right font-mono",
        "example": "1,234,567",
        "supportsFormatting": False,
        "requiresFile": False,
        "isCore": True,
        "decimalPlaces": 0
    },
    {
        "value": "image",
        "label": "이미지",
        "description": "이미지 썸네일로 표시",
        "htmlElement": "img",
        "htmlClass": "thumbnail w-32 h-32 object-cover rounded",
        "example": "<img src=\"...\" class=\"thumbnail\">",
        "supportsFormatting": False,
        "requiresFile": True,
        "isCore": True,
        "width": "128px",
        "height": "128px"
    },
    {
        "value": "file",
        "label": "파일링크",
        "description": "다운로드 가능한 파일 링크로 표시",
        "htmlElement": "a",
        "htmlClass": "text-blue-600 hover:underline flex items-center gap-1",
        "example": "<a href=\"...\" download>📎 파일명.pdf</a>",
        "supportsFormatting": False,
        "requiresFile": True,
        "isCore": True,
        "icon": "📎"
    },
    # 추가 (4개)
    {
        "value": "stars",
        "label": "별점",
        "description": "별 아이콘으로 표시 (★★★★☆)",
        "htmlElement": "span",
        "htmlClass": "text-yellow-400 text-lg",
        "example": "★★★★☆",
        "supportsFormatting": False,
        "requiresFile": False,
        "isCore": False,
        "minRating": 1,
        "maxRating": 5
    },
    {
        "value": "boolean",
        "label": "불린",
        "description": "체크 또는 엑스 아이콘으로 표시",
        "htmlElement": "span",
        "htmlClass": "text-lg",
        "example": "✓ 또는 ✗",
        "supportsFormatting": False,
        "requiresFile": False,
        "isCore": False,
        "trueIcon": "✓",
        "falseIcon": "✗",
        "trueClass": "text-green-600",
        "falseClass": "text-red-600"
    },
    {
        "value": "tags",
        "label": "태그목록",
        "description": "쉼표로 구분된 태그들을 개별 스팬으로 표시",
        "htmlElement": "span",
        "htmlClass": "inline-flex gap-2 flex-wrap",
        "example": "<span class=\"tag\">태그1</span> <span class=\"tag\">태그2</span>",
        "supportsFormatting": False,
        "requiresFile": False,
        "isCore": False,
        "tagClass": "inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm"
    },
    {
        "value": "currency",
        "label": "통화",
        "description": "통화 기호와 함께 천단위 콤마가 적용된 숫자로 표시",
        "htmlElement": "span",
        "htmlClass": "text-right font-mono",
        "example": "₩1,234,567",
        "supportsFormatting": False,
        "requiresFile": False,
        "isCore": False,
        "currencySymbol": "₩",
        "decimalPlaces": 0
    }
]


def get_display_types_config() -> List[Dict[str, Any]]:
    """클라이언트용 display_type 설정 반환"""
    return DISPLAY_TYPES_CONFIG


# 빠른 조회용 딕셔너리
DISPLAY_TYPES_MAP = {item["value"]: item for item in DISPLAY_TYPES_CONFIG}


def get_display_type_by_data_type(data_type: str) -> str:
    """
    data_type으로부터 권장 display_type을 반환

    Args:
        data_type: FieldDataType 값 (string, text, integer, real, boolean, ymd, datetime)

    Returns:
        DisplayType 값
    """
    mapping = {
        "string": "text",
        "text": "html",
        "integer": "number",
        "real": "number",
        "boolean": "boolean",
        "ymd": "date",
        "datetime": "date"
    }
    return mapping.get(data_type, "text")


def get_core_display_types() -> List[Dict[str, Any]]:
    """필수 핵심 display_type만 반환"""
    return [item for item in DISPLAY_TYPES_CONFIG if item.get("isCore", False)]


def get_additional_display_types() -> List[Dict[str, Any]]:
    """추가 display_type만 반환"""
    return [item for item in DISPLAY_TYPES_CONFIG if not item.get("isCore", False)]
