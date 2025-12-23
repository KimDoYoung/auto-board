# view를 기술하는 json

## 기능들

- 미리 정의된 style을 통해서 view를 꾸민다.

```json
// styles.js 또는 constants.py
const FIELD_STYLES = {
  // 텍스트 크기
  'field-title': 'text-2xl font-bold text-gray-900',
  'field-subtitle': 'text-xl font-semibold text-gray-800',
  'field-normal': 'text-base text-gray-700',
  'field-small': 'text-sm text-gray-600',
  
  // 강조
  'field-highlight': 'bg-yellow-100 px-2 py-1 rounded',
  'field-important': 'border-l-4 border-red-500 pl-3',
  'field-info': 'bg-blue-50 p-2 rounded',
  
  // 정렬
  'field-center': 'text-center',
  'field-right': 'text-right',
}
```

```json
{
  "display_fields": [
    {
      "name": "ymd",
      "label": "날짜",
      "display_type": "text",
      "style_class": "field-small"
    },
    {
      "name": "title",
      "label": "제목",
      "display_type": "text",
      "style_class": "field-title"
    },
    {
      "name": "content",
      "label": "내용",
      "display_type": "html",
      "style_class": "field-normal",
      "full_width": true
    },
    {
      "name": "rating",
      "label": "평점",
      "display_type": "stars",
      "style_class": "field-highlight"
    }
  ]
}
```
