# 라우팅 목록

## board

✅ board.py - 보드 목록 엔드포인트 추가
GET /boards/ → 보드 목록 조회
✅ finish.html - 링크 변경
/boards/{{ board.id }} → /boards/{{ board.id }}/records
"대시보드" → "보드 목록"
✅ records.py - 새 파일 생성
GET /boards/{board_id}/records/ → 기록 목록
POST /boards/{board_id}/records/ → 기록 생성
GET /boards/{board_id}/records/{record_id} → 기록 상세보기
PUT /boards/{board_id}/records/{record_id} → 기록 수정
DELETE /boards/{board_id}/records/{record_id} → 기록 삭제
✅ main.py - records 라우터 등록
✅ 템플릿 생성:
app/templates/board/list.html - 보드 목록 페이지
app/templates/record/list.html - 기록 목록
app/templates/record/create.html - 기록 생성
app/templates/record/edit.html - 기록 수정
app/templates/record/view.html - 기록 상세보기
라우팅 구조:

/boards                          → 보드 목록 (GET)
/boards/new/step1               → 보드 생성 마법사
/boards/{board_id}/records      → 기록 목록 (GET)
/boards/{board_id}/records/new  → 기록 생성 폼 (GET)
/boards/{board_id}/records      → 기록 생성 (POST)
/boards/{board_id}/records/{id} → 기록 상세보기 (GET)
/boards/{board_id}/records/{id}/edit → 기록 수정 폼 (GET)
/boards/{board_id}/records/{id} → 기록 수정 (PUT)
/boards/{board_id}/records/{id} → 기록 삭제 (DELETE)
