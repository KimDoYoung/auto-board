# board - step1

## 개요

- 게시판(기록물)의 특징을 나타낸다.
- 물리적 table명을 의미한다.
- table boards 에 레코드가 추가된다.
- step1에 해당한다.

```json
{
  "id": 1,
  "name": "일지",
  "physical_table_name": "table_{board_id}",
  "note": "매일 작성하는 개인 일지",
  "is_file_attach": true
}
```

## 각 items

- `*`는 필수를 의미한다.

1. id : 필수아님, 순차적 증가 id, client단에서는 특정짓지 않아도 되면 서버에서 insert후 번호를 취득한다.
2. name(*) : 사용자에게 알려진 게시판명(기록물명 예: 일지, 여행후기)
3. physical_table_name : create table if not exists {physical_table_name} 문장에 사용된다.
   1. 자동으로 생성 board_id를 max(id) from boards로 부터 생성
   2. 사용자가 기입하지 않으면 table_{board_id} 로 정한다.
4. note : 게시판의 설명
5. is_file_attach(*) : 파일 첨부 기능이 있는지 여부

## UI

- 생성시  
  - name, note, is_file_attach를 입력받는다.
  - id가 존재하면 수정 mode이다.
  - board/wizard_step1.html -> `Board Info Section` 에서 기술한다

- UI로 부터 json을 만든다.

```json
{
  "id": null ,
  "name": "일지",
  "physical_table_name": "table_{board_id}",
  "note": "매일 작성하는 개인 일지",
  "is_file_attach": true
}
```

- id가 존재하면 수정모드이다. 수정모드란 boards 테이블에 해당 레코드가 존재함을 의미.
- 추가모드일때는 id를 boards의 next id로 취득한다.
- physical_table_name은 `table_{next_id}` 로 자동적으로 만든다.
