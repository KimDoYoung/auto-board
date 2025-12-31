# view를 기술하는 json

## 기능들

- 미리 정의된 style을 통해서 view를 꾸민다.
-

```json
// styles.js 또는 constants.py
FIELD_STYLES = {
  // 텍스트 크기
  "field-title": "text-2xl font-bold text-gray-900 mb-2",
  "field-subtitle": "text-xl font-semibold text-gray-800 mb-2",
  "field-heading": "text-lg font-semibold text-gray-800 mb-1",
  "field-normal": "text-base text-gray-700",
  "field-small": "text-sm text-gray-600",
  "field-tiny": "text-xs text-gray-500",
  
  // 강조
  "field-highlight": "bg-yellow-100 px-2 py-1 rounded",
  "field-important": "border-l-4 border-red-500 pl-3 py-1",
  "field-info": "bg-blue-50 p-3 rounded-lg",
  "field-success": "bg-green-50 p-3 rounded-lg",
  "field-warning": "bg-yellow-50 p-3 rounded-lg",
  "field-danger": "bg-red-50 p-3 rounded-lg",
  
  // 정렬
  "field-center": "text-center",
  "field-right": "text-right",
  "field-left": "text-left",
  
  // 레이아웃
  "field-card": "bg-white p-4 rounded-lg shadow-sm border",
  "field-divider": "border-b border-gray-200 pb-3 mb-3"
}
```

```json
{
  "columns": [
    {
      "name": "ymd",
      "label": "작성일",
      "display_type": "date",
      "format": "YYYY년 MM월 DD일",
      "order": 1,
      "inline_group": "header",
      "width": "30%",
      "style_class": "field-small"
    },
    {
      "name": "category",
      "label": "카테고리",
      "display_type": "badge",
      "badge_color_map": {
        "work": "blue",
        "personal": "green",
        "study": "purple"
      },
      "order": 2,
      "inline_group": "header",
      "width": "30%"
    },
    {
      "name": "created_at",
      "label": "등록일시",
      "display_type": "datetime",
      "format": "YYYY-MM-DD HH:mm",
      "relative": true,
      "order": 3,
      "inline_group": "header",
      "width": "40%",
      "style_class": "field-small"
    },
    {
      "name": "title",
      "label": "제목",
      "display_type": "text",
      "order": 4,
      "full_width": true,
      "style_class": "field-title",
      "hide_label": true
    },
    {
      "name": "rating",
      "label": "평점",
      "display_type": "stars",
      "max_stars": 10,
      "show_number": true,
      "order": 5,
      "inline_group": "meta",
      "width": "40%"
    },
    {
      "name": "price",
      "label": "가격",
      "display_type": "currency",
      "currency_code": "KRW",
      "decimal_places": 0,
      "thousands_separator": true,
      "order": 6,
      "inline_group": "meta",
      "width": "30%"
    },
    {
      "name": "is_public",
      "label": "공개여부",
      "display_type": "boolean",
      "true_text": "공개",
      "false_text": "비공개",
      "true_class": "text-green-600",
      "false_class": "text-gray-600",
      "show_icon": true,
      "order": 7,
      "inline_group": "meta",
      "width": "30%"
    },
    {
      "name": "content",
      "label": "내용",
      "display_type": "html",
      "sanitize": true,
      "order": 8,
      "full_width": true,
      "section": "detail",
      "section_title": "상세 내용",
      "style_class": "field-normal"
    },
    {
      "name": "tags",
      "label": "태그",
      "display_type": "list",
      "display_as": "badges",
      "separator": " ",
      "order": 9,
      "full_width": true,
      "hide_if_empty": true
    },
    {
      "name": "attachment",
      "label": "첨부파일",
      "display_type": "file_link",
      "show_size": true,
      "show_icon": true,
      "download": true,
      "order": 10,
      "full_width": true,
      "hide_if_empty": true
    }
  ]
}

```

## 렌더링 결과 (시각화)

```text
┌─────────────────────────────────────────────────┐
│ [2024년 12월 26일 30%] [업무 뱃지 30%] [2시간 전 40%] │  ← inline_group: "header"
│                                                 │
│ 일지 작성 예시                                    │  ← field-title (큰 제목)
│                                                 │
│ [★★★★★★★★☆☆ 8.0] [₩15,000] [공개 ✓]           │  ← inline_group: "meta"
│                                                 │
├─ 상세 내용 ────────────────────────────────────┤
│ 오늘은 프로젝트를 진행하면서...                    │
│ • 중요한 점 1                                    │
│ • 중요한 점 2                                    │
│                                                 │
│ [중요] [긴급]  ← 태그 뱃지들                     │
│                                                 │
│ 📎 design.pdf (2.5 MB) [다운로드]                │
└─────────────────────────────────────────────────┘
