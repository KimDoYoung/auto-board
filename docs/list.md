# list를 기술하는 json

## 기능

- list에 나타날 컬럼들과 속성
- 검색조건을 나타내는 속성
- 페이징에 대한 속성

```json
{
  "display_columns": [
    {
      "name": "ymd",
      "label": "날짜",
      "width": "120px",
      "align": "center",
      "sortable": true
    },
    {
      "name": "title",
      "label": "제목",
      "width": "auto",
      "align": "left",
      "sortable": true
    },
    {
      "name": "rating",
      "label": "평점",
      "width": "80px",
      "align": "center",
      "sortable": true,
      "format": "stars"  // 별점으로 표시
    },
    {
      "name": "price",
      "label": "가격",
      "width": "120px",
      "align": "right",
      "sortable": true,
      "format": "currency"  // 통화 형식
    }
  ],
  "view_mode": "table",  // "table" or "card"
  "paging_type" : "page", // "next", "none"
  "pagination": {
    "next_style" : false,
    "enabled": true,
    "page_size": 20,
    "page_size_options": [10, 20, 50, 100]
  },
  "default_sort": {
    "column": "ymd",
    "order": "desc"  // "asc" or "desc"
  },
  "search": {
    "enabled": true,
    "columns": ["title", "content"]
  },
  "actions": {
    "show_edit": true,
    "show_delete": true,
    "show_detail": true
  }
  "search": {
    "enabled": true,
    "mode": "simple",  // "simple" or "advanced"
    "fields": [
      {
        "name": "title",
        "label": "제목",
        "search_type": "text"  // text, exact, date_range
      },
      {
        "name": "ymd",
        "label": "날짜",
        "search_type": "date_range"
      },
      {
        "name": "rating",
        "label": "평점",
        "search_type": "range",  // 1-10 사이
        "min": 1,
        "max": 10
      }
    ]
  }  
}
````

- UI 샘플

```text
[제목 검색: _______] [날짜: 시작일____ ~ 종료일____] [평점: 1 ━━●━━ 10]
```
