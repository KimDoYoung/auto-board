# column를 기술하는 json

- sqlite의 물리적인 table을 기술한다.

```json
{
  "fields": [
    {
      "name": "ymd",
      "label": "날짜",
      "data_type": "ymd",
      "required": true,
      "default_value": null
    },
    {
      "name": "title",
      "label": "제목",
      "data_type": "string",
      "length": 100,
      "required": true,
      "default_value": ""
    },
    {
      "name": "content",
      "label": "내용",
      "data_type": "text",
      "required": false,
      "default_value": null
    },
    {
      "name": "rating",
      "label": "평점",
      "data_type": "integer",
      "min_value": 1,
      "max_value": 10,
      "required": true,
      "default_value": 5
    },
    {
      "name": "price",
      "label": "가격",
      "data_type": "float",
      "min_value": 0.0,
      "max_value": 1000000.0,
      "required": false,
      "default_value": null
    },
    {
      "name": "is_public",
      "label": "공개여부",
      "data_type": "boolean",
      "required": true,
      "default_value": false
    },
    {
      "name": "created_at",
      "label": "생성일시",
      "data_type": "datetime",
      "required": true,
      "default_value": "now()"
    }
  ]
}
```
