# wizard steps

## step1

- 새로운 테이블을 create한다.
- wizard_step1.html

### 주요 기능

- 새로운 기록물을 생성 시작
- sqlite 의 create table을 하게 된다.
- docs/board.md, docs/columns.md 참조

### 흐름

1. wizard_step1.html에서  UI -> `board json`과 `columns json` -> submit
2. new/step1_submit 에서 boards 에 record추가.
3. create table ddl 수행. 필요시 drop table ddl
4. meta_data table `columns` 에 `columns json` 추가
5. 최종결과
   1. boards table 1 record 추가.
   2. meta_data table 1 record 추가.
   3. autoboard sqlite db에 table 1개 생성

## step2

- list를 어떻게 할 것인지 사용자가 편집한다.

## 주요기능

- new/wizard_step2.html
- step1에서 생성된 table  예를 들어 table_1 에 대한 리스트를 어떻게 표현 할 것인가 정하게 된다.
- 그 정보는 docs/list.md에 기술한 것과 같은 json 으로 표현된다.
- 즉 list.md를 만들 수 있는 html 페이지를 제공한다.

## step3

- create 즉 table_{id} 에 대한 create 화면을 어떻게 보여주면서 편집(사용자가 추가, 수정) 할 지 UI를 통해서 정한 후 그 결과를 `create_edit` json 으로 만든다.
- 만들어진 json은 submit 되어서 `meta-data` table에 `create_edit` 항목으로 저장된다.

## step4

- view 즉 table_{id}를 어떻게 보여줄지를 나타내는 json을 만드는 UI를 만든다.
- UI에서 `view.json`을 output으로 한다.

## 결론

- step1,2,3,4 는 json 파일을 만드는 UI를 제공해야한다.

1. step1 -> submit -> board.md와 columns.md의 json을 만들어서 server로 보낸다.
2. server에서는 create table table_{id} 을 한다. josn을 meta-data table에 name을 `table` 1개의 레코드로 넣는다.
3. step2 -> submit -> 만들어진 table_{id}을 보여줄 수 있는 meta json을 만들어서 server로 보낸다.
4. server에서는 json을 name을 `list`로 레코드로 넣는다.
5. step3 -> submit -> 만들어진 table_{id}를 어떻게 추가, 수정할 수 있는 html을 만드는지 지정하는 json을 만들어서 server에 보낸다.
6. server에서는 josn을 name을 `create_edit`로 레코드로 넣는다.
7. step4 -> submit -> 만들어진 table_{id}를 어떻게 detail view 할지 결정하는  json을 만들어서 server에 보낸다.
8. server에서는 josn을 name을 `view`로 레코드로 넣는다.
9. step1,2,3,4 는 json 파일을 만드는 UI를 제공해야한다.

```sql
create table if not exists meta_data(
    id integer primary key,
    board_id integer not null,
    name text not null, -- `table`,`columns`,`create_edit`,`view`,`list`
    meta text not null, --json format
    schema text not null,
    created_at timestamp not null default current_timestamp,
    updated_at timestamp not null default current_timestamp
);
```

Step 1 → {table: {...}, columns: {fields: [...]}}

- step1 submit json : wizard_step1.html에서 submit하는 json
{
    name: "일지",
    note: "매일 작성하는 개인 일지",
    is_file_attach: false,

    columns: [
        { label: "날짜", data_type: "ymd", comment:"기준일자"},
        { label: "제목", data_type: "string", comment: "하루의 요약"}
    ]
}
- data_type은 dropdown으로 `문자열`(string),`문장`(text),`정수`(integer),`실수(소수점포함)`(real),`날짜`(ymd),`날짜시간`(datetime) 처리

- step1 meta table json : meta_data 에 `table` 로 저장되는 json
{
    name: "일지",
    note: "매일 작성하는 개인 일지",
    is_file_attach: false,

    "physical_table_name": "table_{board_id}",
    "id" : 1
    columns: [
        { label: "날짜", data_type: "ymd", name: "col1"},
        { label: "제목", data_type: "string" , name: "col2"}
    ]
}

- submit 후의 검증
  1. table desc을 log로 인쇄
  2. table_1 이 만들어져야하며 comment는 일지로 기록되어야함.
  3. table_1 은 `null`, `integer`,`real`, `text`의 데이터타입을 가지고 `col1`, `col2`...와 같이 만들어져야함.

Step 2 → {list: {...}}

{
    view_mode: "table",
    display_columns: ["ymd", "title", "content"],
    pagination: { enabled: true, page_size: 10 },
    default_sort: { column: "ymd", order: "desc" },
    search: {
      enabled: true,
      columns: ["title", "content"]
    }
}
Step 3 → {create_edit: {fields: [...]}}

{
  create_edit: {
    fields: [
      { name: "ymd", label: "날짜", element: "input", element_type: "date", required: true },
      { name: "title", label: "제목", element: "input", element_type: "text", required: true }
    ]
  }
}
Step 4 → {view: {display_fields: [...]}}

{
  view: {
    display_fields: [
      { name: "ymd", label: "작성일", display_type: "date", format: "YYYY-MM-DD", order: 1 },
      { name: "title", label: "제목", display_type: "text", style_class: "field-title", order: 2 }
    ]
  }
}
모두 docs/ 설계문서와 동일한 JSON 스키마를 따르도록 수정되었습니다!
