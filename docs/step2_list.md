# step2 - list

## wizard_step2.html의 submit 시

```json
{
  "view_mode": "table",
  "display_columns": [
    {
      "name": "ymd",
      "label": "날짜",
      "width": "120px",
      "align": "center",
      "sortable": true,
      "format": "date"
    },
    {
      "name": "title",
      "label": "제목",
      "width": "auto",
      "align": "left",
      "sortable": true
    },
    {
      "name": "category",
      "label": "카테고리",
      "width": "100px",
      "align": "center",
      "sortable": true,
      "format": "badge"
    },
    {
      "name": "rating",
      "label": "평점",
      "width": "120px",
      "align": "center",
      "sortable": true,
      "format": "stars"
    },
    {
      "name": "price",
      "label": "가격",
      "width": "120px",
      "align": "right",
      "sortable": true,
      "format": "currency"
    }
  ],
  "pagination": {
    "enabled": true,
    "page_size": 20,
    "page_size_options": [10, 20, 50, 100]
  },
  
  // ✅ 개선 1: 다중 정렬을 위한 배열 구조
  "default_sort": [
    {
      "column": "ymd",
      "order": "desc"
    },
    {
      "column": "title",
      "order": "asc"
    }
  ],
  
  "search": {
    "enabled": true,
    "mode": "both",  // "simple", "advanced", "both"
    "show_toggle": true,
    
    // ✅ 개선 2: Simple 검색에 포함될 필드 명시
    "simple_fields": ["title", "content"],
    
    // Advanced 검색 상세 설정
    "advanced_fields": [
      {
        "name": "title",
        "label": "제목",
        "search_type": "text",
        "placeholder": "제목으로 검색",
        "operator": "contains"
      },
      {
        "name": "content",
        "label": "내용",
        "search_type": "text",
        "placeholder": "내용으로 검색"
      },
      {
        "name": "ymd",
        "label": "날짜",
        "search_type": "date_range",
        "presets": [
          {"label": "오늘", "value": "today"},
          {"label": "이번 주", "value": "this_week"},
          {"label": "이번 달", "value": "this_month"}
        ]
      },
      {
        "name": "category",
        "label": "카테고리",
        "search_type": "select",
        "options": [
          {"value": "work", "label": "업무"},
          {"value": "personal", "label": "개인"},
          {"value": "study", "label": "공부"}
        ],
        "multiple": true
      },
      {
        "name": "rating",
        "label": "평점",
        "search_type": "range",
        "min": 1,
        "max": 10,
        "step": 1
      },
      {
        "name": "price",
        "label": "가격",
        "search_type": "range",
        "min": 0,
        "max": 1000000,
        "step": 1000
      },
      {
        "name": "is_public",
        "label": "공개여부",
        "search_type": "boolean",
        "true_label": "공개",
        "false_label": "비공개",
        "all_label": "전체"
      }
    ]
  },
  
  "actions": {
    "show_edit": true,
    "show_delete": true,
    "show_detail": true,
    "bulk_actions": ["delete", "export"]
  }
}
```

## simple search

```json
{
  "search": {
    "enabled": true,
    "mode": "simple",
    "simple_fields": ["title", "content", "category"]
  }
}
```

**UI:**

- 대략적인 UI

```text
**UI:**

- UI

Simple Mode:
┌─────────────────────────────────────┐
│ 🔍 [통합 검색________] [검색] [고급▼]│
└─────────────────────────────────────┘

Advanced Mode (토글 클릭 시):
┌─────────────────────────────────────┐
│ 제목: [_******]  내용: [******_]    │
│ 날짜: [****] ~ [****]  [이번 달▼]  │
│ 평점: 1 ━━━●━━━ 10                 │
│        [초기화] [검색]    [간단히▲]│
└─────────────────────────────────────┘
```
