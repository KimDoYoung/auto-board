# Auto-Board 설계

## 개요

사람(개인)은 살면서 여러가지  **기록**을 하게 되는데, 기록의 종류에 따라서 각 **항목**들이 다르다.
그래서 새로운 기록을 위해서 항목을 **자유롭게 정할 필요**가 있다. 기록은 database의 테이블에 해당하고 항목은 컬럼에 해당한다.
기록과 항목을 자유롭게 편집해서 CRUD를 하고자 한다. 자유게시판이라고 할 수 있다.
예를 들어 일지, 키보드 수집, 혈압측정기록, 영화감상 등등...
개인(1인용)용 프로그램임. 외부 interface는 없음. 어떤 기록물인가에 따라 다르나  대략 각 기록물당 1만원이하로 가정하다.

## 특징

- 개인의 다양한 기록물을 관리
- 메타 데이터 기반 게시판
- 이미지를 본문에 넣을 수 있다.
- 첨부파일을 추가할 수 있다.

## 기술스택

- 프로젝트는 backend와 frontend를 모두 갖는다.

### backend

- FastAPI
- jinja2 : json meta data를 이용한 rendering
- DB : sqlite
- jwt authentication

### frontend

- tailwindcdd
- alpine.js
- html editor로 quill.js
- 기타 CDN 가능한 js library들

## tables

- boards(기록들)
  - id, name(title), physical_table_name, note
  - 실제로 물리적인 파일을 만든다. table_{id} 형태로 작성(사용자에게 물리적 파일은 노출되지 않는다)
- meta_data
  - board_id, name, meta, schema
  - name에는 `columns`, `list`, `create`, `edit`, `view`
  - meta에는 `columns` 인 경우 json형태로 board에 대한 column들을 기술한다.
    - column의 data type, min/max length, required, select one of items, validation check등
  - `list`인 경우에는 table의 내용을 list로 표출할 때의 형태등을 기술한다.
    - list할 columns, list하는 방식 (table, card), paging여부
  - `create`인 경우에는 table의 레코드를 추가 할 때의 형태등을 기술한다.
    - 입력받을 columns
    - 각 columns의 입력방식(input, textarea, html editor사용등)
  - `edit`인 경우에는 table의 레코드를 수정 할 때의 형태등을 기술한다.
    - `create`와 유사
  - schema는 meta data에 대한 JSON Schema validation 을 갖는다.

- files
  - 첨부파일리스트
  - id, base_folder, physical_name, logical_name, size, mime
- file_match
  - board_id, table_id, file_id

## 사용자 설정

- .env 파일을 갖고 사용자의 설정을 관리한다.
- .env안의 base_dir로 사용자의 데이터 위치를 관리한다.

## 기능

- 새로운 기록을 생성
  - 새로운 기록과 딸린 항목들을 사용자가 설정한다.
  - 물리적인 테이블을 생성한다.
- 기록의 CRUD
  - meta_data에 의해서 html을 만든다.
  - board_id와 table_id로 특정짓는다.
- 기록의 CSV, Excel, PDF로 출력
- 기존에 만들어진 물리테이블의 항목(column)에 추가는 가능하고 제한적인 수정은 가능하다. 삭제도 가능하면 데이터를 소실된다.

## 배포

- 개인용 pc에 dir base(--onedir)의 pyinstaller를 사용한 배포
- base_dir 하위의 folder들에 sqlite db와 files 들을 갖고 있게 한다.

## 시나리오

### `일지(diary)` 기록물 생성

1. boards에 레코드 추가 1, `일지`, `table_1`, `일지`
2. meta_data 1(meta_data자체의 id), 1 (boards id), [{`col1`:{'name':'ymd', datatype:'string', len:8},...}
3. meta_data를 참조하여 물리테이블 table_1를 생성한다. 즉 create table ddl을 생성하여 수행시킨다.

## 사용자가 기록의 항목을 추가

1. meta_data `columns`의 json으로 기존 항목을 UI에 표시
2. 항목을 추가
3. 항목의 기능들을 설정
4. 설정된 내용을 meta_data의 json에 추가

## json파일을 참조

1. columns : docs/columns.md
2. list : docs/list.md
3. view : docs/view.md

## 폴더의 구성

- docs 폴더 하위에 설계문서를 넣는다.
- app 폴더 하위에 소스를 넣는다.

```text
app
|-- core
|-- domain
|-- endpoints
|-- static
|   |-- css
|   |-- images
|   `-- js
`-- templates
```
