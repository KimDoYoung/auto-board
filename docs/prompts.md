# 프롬프트

## 로그인 흐름

1. jwt auth로, 쿠키를 사용합시다.
2. login/logout 등의 url은 home.py homeroutes에서 처리.
3. "/" 접속시 login상태이면 index.html로
4. logout상태이면 login.html을  보여줌.
5. index.html은 main 이면서 dashboard형태인데 지금은 그냥 jinja2로 nav.html만들 include해서 사용.
6. nav는 임의로 dropdown 메뉴 `기록물` 클릭-> '새로운 기록물` 이렇게 나오게끔,
7. nav 오른쪽에 logout

## 기록물 생성

1. 1페이지에 기록물 생성을 쭉 만들어 봅시다. 나누거나 개선하는 것은 나중에 하기로 하고.
2. `boards` 테이블에 1레코드를 추가 : 이름과 설명 입력받음.
3. 항목들 추가(참조 docs/columns.md) : 추가버튼 클릭(동적)-> label입력, datatyp, 필수여부, 기본값, min,max,defalt 입력받음
4. 이 항목값들을 json으로 만들어서 `meta_data`에 board_id 1, name 'columns` 로 insert하게 된다.
5. 저장버튼 javascript로 입력값들을 json으로 만들어서  POST boards/create 로 전송. 서버에서 db에 저장 새로 생긴 board_id 리턴
6. board_manager.js 로 값들을 docs/columns.md에 따라서 json으로 만들자 그것을 전송하자.
7. 저장완료되면 list버튼, edit버튼, view버튼 활성화
8. list버튼 클릭시 서버로 부터 GET /boards/columns/{board_id}  `meta_data` board_id, `columns`의 json을 받음.  list_div 보이게끔(list_div에서 UI구성)
9. columns json으로 column list와 docs/list.md 에 따라서 label, width, align, sortble 정보를 사용자에게서 받음. (그렇게 UI를 만들어줘)
10. edit와 view도  list와 같음.
