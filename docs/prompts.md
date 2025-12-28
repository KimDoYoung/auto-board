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

## 삭제 프로세스

1. 현재 templates/board/wizard_*html을 templates/board/wizard 폴더를 만들고 그쪽으로 옮기기
2. 1.에 따른 board.py 코드 수정
3. index.html에서 card의 하단에 `수정`,`삭제` icon생성
4. `수정` click wizard_step1 을 표현
5. `삭제` click 시

- 해당 테이블이 존재하지 않을 경우 바로 삭제
- 해당 테이블이 존재하며 table 레코드가 0 인 경우 `삭제하시겠습니까?` confirm 하고 yes이면 삭제
- 해당 테이블이 존재하며 table 레코드가 1 이상인 경우 `delete_confirm.html` 표시
- delete_confirm화면은 현재 몇개의 레코드가 있고 진짜로 삭제하려면 테이블의 이름을 입력 받고 삭제
- `삭제` 프로세스는 boards와 meta_data 레코드에서 해당 id를 삭제하라는 뜻임.

6. boards 테이블에 status 필드를 추가하면 어떨까?
   예를 들어 step0(step1도 끝내지 않았다), step1(step1을 끝낸 상태다) 뭐 이런 것을 , `finish`는 설정 끝 이런 식으로
