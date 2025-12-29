# record

## 개요

- wizard steps 로 생성된 meta_data를 기반으로 각 기록물(게시판)의 CRUD 기능을 구현을 한다.
- meta_data를 기반으로 한다는 것은 wizard steps와 sync되어야 한다는 의미이다.
- 예를 들어 wizard steps에서 컬럼을 추가하면 meta_data에 추가되고, templates/record/ 하위의 html들에도 반영되어야 한다.

## 용어

- create : 새로운 게시물
- edit : 기존 게시물 수정
- view : 게시물 조회
- list : 게시물 목록

## 참조

- autoboard_ddl.sql
- `meta_data` 테이블의 name column은 `table`, `list`,`create_edit`, `view` 으로 정의되어 있다.
- meta_data순서가 `table`, `list`, `create_edit`, `view` 순으로

## 새로운 게시물 (create)

- meta_data의 `table`, `create_edit` 을 기반으로 새로운 게시물 생성
- `table`의 is_file_attach가 true이면 파일 첨부 기능 추가
- `create_edit`의 fields 를 따라서 입력을 받는 html을 생성한다. (jinja2 template)
- templates/record/create.html을 기반으로 새로운 게시물 생성
