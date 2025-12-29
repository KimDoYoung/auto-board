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

## 새로운 게시물 (create)
