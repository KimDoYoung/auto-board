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

- create 즉 table_{id} 에 대한 create 화면을 어떻게 보여줄 지 UI를 통해서 정한 후 그 결과를 `create-json`으로 만든다.
- 만들어진 json은 submit 되어서 `meta-data` table에 `create` 항목으로 저장된다.

