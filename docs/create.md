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
      "width": "200px",
      "position": {"row": 1, "col": 1},
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
      "position": {"row": 1, "col": 2},
      "colspan": 2,
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
      "position": {"row": 2, "col": 1},
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
      "position": {"row": 3, "col": 1},
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
      "position": {"row": 4, "col": 1},
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
      "position": {"row": 4, "col": 2}
    },
    {
      "name": "is_public",
      "label": "공개여부",
      "data_type": "boolean",
      "element": "checkbox",
      "default_value": false,
      "position": {"row": 5, "col": 1},
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
      "position": {"row": 5, "col": 2}
    },
    {
      "name": "attachment",
      "label": "첨부파일",
      "data_type": "string",
      "element": "file",
      "accept": ".pdf,.doc,.docx,image/*",
      "max_file_size": 10485760,
      "multiple_files": true,
      "position": {"row": 6, "col": 1},
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
      "position": {"row": 7, "col": 1}
    }
  ]
}
```
