# create json 기술

## 개요

- meta_data table에 `create` 항목으로 저장된다.
- table_{id}에 새로운 레코드가 추가될 때 어떻게 html이 만들어지고 사용자에게 입력받느냐를 column별로 기술한다.

## json 예

```json
{
  "fields": [
    {
      "name": "ymd",
      "label": "날짜",
      "data_type": "ymd",
      "element": "input",
      "element_type": "date",
      "required": true,
      "default_value": "today",
      "order": 1,
      "inline_group": "header",
      "width": "30%",
      "help_text": "기록 날짜를 선택하세요"
    },
    {
      "name": "title",
      "label": "제목",
      "data_type": "string",
      "element": "input",
      "element_type": "text",
      "length": 100,
      "required": true,
      "placeholder": "제목을 입력하세요",
      "order": 2,
      "inline_group": "header",
      "width": "70%",
      "autofocus": true
    },
    {
      "name": "category",
      "label": "카테고리",
      "data_type": "string",
      "element": "select",
      "required": true,
      "options": [
        {"value": "work", "label": "업무"},
        {"value": "personal", "label": "개인"},
        {"value": "study", "label": "공부"}
      ],
      "order": 3,
      "width": "100%",
      "on_change": "updateRelatedFields"
    },
    {
      "name": "content",
      "label": "내용",
      "data_type": "text",
      "element": "html_editor",
      "required": false,
      "editor_type": "quill",
      "editor_config": {
        "modules": {
          "toolbar": [
            ["bold", "italic", "underline", "strike"],
            ["blockquote", "code-block"],
            [{"list": "ordered"}, {"list": "bullet"}],
            ["link", "image"],
            ["clean"]
          ]
        }
      },
      "order": 4,
      "full_width": true
    },
    {
      "name": "rating",
      "label": "평점",
      "data_type": "integer",
      "element": "input",
      "element_type": "range",
      "min_value": 1,
      "max_value": 10,
      "step": 1,
      "default_value": 5,
      "order": 5,
      "inline_group": "meta",
      "width": "50%",
      "help_text": "1-10점 사이로 평가하세요"
    },
    {
      "name": "price",
      "label": "가격",
      "data_type": "float",
      "element": "input",
      "element_type": "number",
      "min_value": 0.0,
      "max_value": 1000000.0,
      "step": 0.01,
      "placeholder": "0.00",
      "order": 6,
      "inline_group": "meta",
      "width": "50%"
    },
    {
      "name": "is_public",
      "label": "공개여부",
      "data_type": "boolean",
      "element": "checkbox",
      "default_value": false,
      "order": 7,
      "inline_group": "options",
      "width": "50%",
      "help_text": "다른 사람에게 공개합니다"
    },
    {
      "name": "tags",
      "label": "태그",
      "data_type": "string",
      "element": "select",
      "multiple": true,
      "options": [
        {"value": "important", "label": "중요"},
        {"value": "urgent", "label": "긴급"},
        {"value": "review", "label": "검토필요"}
      ],
      "order": 8,
      "inline_group": "options",
      "width": "50%"
    },
    {
      "name": "attachment",
      "label": "첨부파일",
      "data_type": "string",
      "element": "file",
      "accept": ".pdf,.doc,.docx,image/*",
      "max_file_size": 10485760,
      "multiple_files": true,
      "order": 9,
      "full_width": true
    },
    {
      "name": "created_at",
      "label": "생성일시",
      "data_type": "datetime",
      "element": "input",
      "element_type": "datetime-local",
      "required": true,
      "auto_generate": "timestamp",
      "readonly": true,
      "order": 10,
      "width": "100%"
    }
  ]
}

```

## 주요 변경사항

### 1. **position 제거** → **order + inline_group**

- `position: {"row": 1, "col": 1}` → `order: 1, inline_group: "header"`
- 더 직관적이고 유연한 배치

### 2. **inline_group 그룹핑**

- `"header"`: 날짜(30%) + 제목(70%) - 첫 줄
- `"meta"`: 평점(50%) + 가격(50%) - 같은 줄
- `"options"`: 공개여부(50%) + 태그(50%) - 같은 줄
- 그룹이 없는 필드는 독립적으로 배치

### 3. **width 방식 변경**

- `"200px"` → `"30%"` (상대값으로 변경)
- 반응형에 더 적합

### 4. **colspan 제거**

- `colspan: 2` → inline_group으로 더 명확하게 표현

### 5. **full_width 명시**

- 전체 너비를 차지하는 필드에 명시적 표시

## 렌더링 결과 (시각화)

```text

┌─────────────────────────────────────┐
│ [날짜 30%]  [제목 70%]              │  ← inline_group: "header"
│                                     │
│ [카테고리 100%]                     │  ← 독립
│                                     │
│ [내용 ────────────────────────]     │  ← full_width
│ [     HTML Editor 영역        ]     │
│ [                              ]     │
│                                     │
│ [평점 50%]     [가격 50%]           │  ← inline_group: "meta"
│                                     │
│ [공개여부 50%] [태그 50%]           │  ← inline_group: "options"
│                                     │
│ [첨부파일 ────────────────────]     │  ← full_width
│                                     │
│ [생성일시 100%]                     │  ← 독립
└─────────────────────────────────────┘
