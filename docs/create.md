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
      "data_type": "string",
      "required": true,
      "default_value": "today",
      "element" : "input",
      "element_type": "date",
      "width" : "100px",
      "position": {"row":1, "col" :1}
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
      "default_value": null,
      "content_type" : "html" 
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
    }
  ]
}
```
