# column를 기술하는 json

## 개요

- sqlite의 물리적인 table을 기술한다.
- step1에 해당한다.
- json의 fields의 항목으로 crate table table_{id}의 컬럼을 지정한다.
- create table시 주의할 점. ( 사용자가 변경시 database의 table을 alter table하는 것은 힘듬)
  - default를 정했다고 해서 ddl로 default키워드를 쓰지 말것.
  - min,max등 validateion에 해당하는 것을 check 키워드를 쓰지 말것.
  - not null을 쓰지 말것
  - 즉 모드 로직으로 체크할 예정임
- 입력받는 항목들 (data_type에 따라서 동적으로 입력받는 항목들이 변경된다)
  - label
  - data_type : dropdown 형식
  - required 필수여부
  - default value
  - string인 경우 length default는 100으로
  - integer인 경우 min, max
  - text인 경우 content_type (html:워드형식, text: 단순문자 )

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
