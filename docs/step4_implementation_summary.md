# Step 4 구현 완료 - 상세보기(View) 설정

## 작업 요약

Step 4(상세보기 설정) 화면에 다음 기능을 구현했습니다:

1. **기존 view 메타데이터 로드** - 수정 모드 구현
2. **새로운 view 설정 생성** - 생성 모드 구현
3. **클라이언트 측 상세 로깅** - 모든 단계별 console.log 추가
4. **서버 측 상세 로깅** - 데이터 저장 전후 상세 로깅

---

## 파일 변경 사항

### 1. `app/templates/board/wizard/step4.html`

#### 변경 내용:

**[1] 초기화 로직 개선**
- `createEditConfig` 변수 추가: Step 3에서 생성한 create_edit 설정 표시
- `viewConfig` 변수 추가: 기존 view 메타데이터 로드
- `boardData` 변수 추가: 보드 정보 전달

**[2] 초기화 단계별 로깅** (`console.log` 추가)

```javascript
// [STEP4-INIT-0] 초기화 시작
// [STEP4-INIT-0-1] Board 정보 로그
// [STEP4-INIT-0-2] 컬럼 데이터 로그
// [STEP4-INIT-0-3] 기존 view config 로그

// [STEP4-INIT-1] init() 실행
// [STEP4-INIT-2] CREATE/EDIT MODE 판단
  // - CREATE MODE: 기본 섹션 + 컬럼 필드 자동 추가
  // - EDIT MODE: loadExistingConfig() 호출
// [STEP4-INIT-3] ✓ 초기화 완료
```

**[3] Edit Mode 지원 - `loadExistingConfig()` 메서드 추가**

```javascript
loadExistingConfig() {
    // 1. 섹션별로 필드 그룹화
    // 2. 각 섹션 UI 추가 (섹션 제목 포함)
    // 3. 각 필드 UI 생성 및 데이터 복원
    //    - 기본 필드: name, label, display_type, width, inline_group, full_width, hide_label, style_class
    //    - Display type별 옵션 복원 (date, datetime, stars, currency, boolean, badge, list, file_link)
    // 4. 조건부 UI 업데이트
}
```

**[4] Display Type별 옵션 복원 - `restoreDisplayTypeOptions()` 메서드 추가**

각 display type의 특수 옵션을 복원합니다:
- `date`: format
- `datetime`: format, relative
- `stars`: max_stars, show_number
- `currency`: currency_code, decimal_places, thousands_separator
- `boolean`: true_text, false_text, true_class, false_class, show_icon
- `badge`: badge_color_map
- `list`: display_as, separator, hide_if_empty
- `file_link`: show_size, show_icon, download

**[5] 제출 단계별 상세 로깅** (`submit()` 메서드)

```javascript
// [STEP4-SUBMIT] 제출 시작
// [STEP4-SUBMIT-1] form_data 수집 완료
// [STEP4-SUBMIT-2] 총 N개 필드 준비
// [STEP4-SUBMIT-3-{idx}] 각 필드별 상세 정보
// [STEP4-SUBMIT-4] JSON 전송 준비 (pretty print)
// [STEP4-SUBMIT-5] POST 요청 중
// [STEP4-SUBMIT-6] 응답 상태
// [STEP4-SUBMIT-7] 응답 데이터
// [STEP4-SUBMIT-8] ✓ 제출 성공
// [STEP4-SUBMIT-9] 리다이렉트 경로
```

**[6] DOMContentLoaded 로깅 추가**

```javascript
// [STEP4-DOM] DOMContentLoaded 이벤트 발생
// [STEP4-DOM] ✓ init() 호출 완료
```

---

### 2. `app/routes/board.py`

#### GET 핸들러 변경 (`wizard_step4_form`)

**수정 전:**
```python
create_meta = db_manager.get_metadata(board_id, "create")
edit_meta = db_manager.get_metadata(board_id, "edit")

return {
    "create_config": create_meta,
    "edit_config": edit_meta
}
```

**수정 후:**
```python
create_config = db_manager.get_metadata(board_id, "create_edit")  # Step 3 데이터
view_meta = db_manager.get_metadata(board_id, "view")            # Step 4 기존 데이터

return {
    "create_config": create_config,   # 입력폼 참고용
    "view_config": view_meta          # 상세보기 기존 설정
}
```

#### POST 핸들러 변경 (`wizard_step4_submit`)

**수정 전:**
```python
edit_config = form_data.get("edit_config", {})
db_manager.save_metadata(board_id, "edit", edit_config)
```

**수정 후:**
```python
view_config = form_data.get("view", {})
db_manager.save_metadata(board_id, "view", view_config)
```

#### 서버 측 상세 로깅 추가

**[STEP4-1]** 🚀 Step 4 Submit 시작
- board_id 기록

**[STEP4-2]** 전송된 form_data 구조
- form_data의 키 목록

**[STEP4-3]** view 설정 받음
- 총 필드 개수
- 각 필드별 상세 정보:
  - 필드명, 라벨, display_type, order
  - 조건부: width, inline_group, full_width, hide_label, style_class, section, section_title
  - Display type별 옵션 (format, max_stars, currency_code 등)

**[STEP4-4~5]** JSON 저장 전 로깅
- "데이터베이스에 저장 중..." 메시지
- 저장할 JSON (pretty print)

**[STEP4-6]** ✓ 데이터베이스에 저장 완료

**[STEP4-7]** 메타데이터 검증
- board_id, type='view' 정보

**[STEP4-8]** 저장된 데이터 검증 완료
- 저장된 필드 개수
- 각 필드명 및 라벨 확인

**[STEP4-9]** 마무리 페이지로 리다이렉트

**[STEP4-ERROR]** 예외 발생 로깅
- 예외 타입, 메시지, 스택 트레이스

---

## 데이터 흐름

### CREATE MODE (새로운 보드)

```
Step 4 초기 로드
├─ [STEP4-INIT-0] 초기화 시작 (보드, 컬럼, view config=null)
├─ [STEP4-INIT-1] init() 실행
├─ [STEP4-INIT-2] CREATE MODE 감지
│  └─ addSection() → populateFieldsFromColumns()
├─ [STEP4-INIT-3] ✓ 초기화 완료
│
사용자 입력
│
Step 4 제출
├─ [STEP4-SUBMIT] 제출 시작
├─ [STEP4-SUBMIT-1~2] form_data 수집
├─ [STEP4-SUBMIT-3-N] 각 필드 정보 로깅
├─ [STEP4-SUBMIT-4] JSON 준비 (pretty print)
├─ [STEP4-SUBMIT-5] POST /boards/new/step4/{board_id}
│
서버 처리
├─ [STEP4-1] 🚀 Step 4 Submit 시작
├─ [STEP4-2] form_data 구조 확인
├─ [STEP4-3] view 설정 분석 (필드별 상세)
├─ [STEP4-4~5] JSON 저장 전 로깅
├─ db_manager.save_metadata(board_id, "view", view_config)
├─ [STEP4-6~8] 저장 완료 및 검증
└─ [STEP4-9] 마무리 페이지로 리다이렉트
```

### EDIT MODE (기존 보드 수정)

```
Step 4 초기 로드
├─ [STEP4-INIT-0] 초기화 시작 (보드, 컬럼, view config=있음)
├─ [STEP4-INIT-1] init() 실행
├─ [STEP4-INIT-2] EDIT MODE 감지
│  └─ loadExistingConfig()
│     ├─ [STEP4-INIT-2-1] 기존 view 설정 로드 시작
│     ├─ [STEP4-INIT-2-2] 섹션별 그룹화
│     ├─ [STEP4-INIT-2-3-N] 각 필드 UI 생성 및 데이터 복원
│     ├─ [STEP4-INIT-OPT] Display type별 옵션 복원
│     └─ [STEP4-INIT-2-4] ✓ 기존 설정 모두 로드 완료
├─ [STEP4-INIT-3] ✓ 초기화 완료
│
사용자 수정
│
Step 4 제출 (위와 동일)
```

---

## 메타데이터 저장 구조

### view 메타데이터 형식

```json
{
  "columns": [
    {
      "name": "ymd",
      "label": "작성일",
      "display_type": "date",
      "format": "YYYY년 MM월 DD일",
      "order": 1,
      "inline_group": "header",
      "width": "30%",
      "style_class": "field-small"
    },
    {
      "name": "title",
      "label": "제목",
      "display_type": "text",
      "order": 4,
      "full_width": true,
      "style_class": "field-title",
      "hide_label": true
    },
    {
      "name": "rating",
      "label": "평점",
      "display_type": "stars",
      "max_stars": 10,
      "show_number": true,
      "order": 5,
      "inline_group": "meta",
      "width": "40%"
    },
    {
      "name": "content",
      "label": "내용",
      "display_type": "html",
      "sanitize": true,
      "order": 8,
      "full_width": true,
      "section": "section_1",
      "section_title": "상세 내용"
    }
  ]
}
```

---

## 로깅 비교

### 이전 (변경 전)
```
🚀 Step 4 Submit: Saving edit config for board 1
✅ Edit config saved for board 1
```

### 이제 (변경 후)
```
[STEP4-1] 🚀 Step 4 Submit 시작 - board_id=1
[STEP4-2] 전송된 form_data 구조: ['view']
[STEP4-3] view 설정 받음: 5개 필드
     [1] 필드명: ymd
         - label: 작성일
         - display_type: date
         - order: 1
         - width: 30%
         - inline_group: header
         - style_class: field-small
         - format: YYYY년 MM월 DD일
     [2] 필드명: rating
         - label: 평점
         - display_type: stars
         - order: 5
         - inline_group: meta
         - width: 40%
         - max_stars: 10
         - show_number: true
     ... (이하 계속)
[STEP4-4] 데이터베이스에 저장 중...
[STEP4-5] 저장할 JSON (pretty):
{
  "columns": [
    {
      "name": "ymd",
      "label": "작성일",
      "display_type": "date",
      "format": "YYYY년 MM월 DD일",
      ...
    },
    ...
  ]
}
[STEP4-6] ✓ 데이터베이스에 저장 완료
[STEP4-7] 메타데이터 검증: board_id=1, type='view'
[STEP4-8] ✅ 저장된 데이터 검증 완료: 5개 필드
       [1] ymd (작성일)
       [2] rating (평점)
       ...
[STEP4-9] 마무리 페이지로 리다이렉트 중...
```

---

## 클라이언트 로그 예시 (브라우저 console)

### 초기화 단계
```
============================================================
[STEP4-INIT-0] Step 4 초기화 시작
============================================================
[STEP4-INIT-0-1] Board 정보: {id: 1, name: "일지", is_file_attach: true, ...}
[STEP4-INIT-0-2] 컬럼 데이터: [{name: "ymd", label: "날짜", data_type: "ymd", ...}, ...]
[STEP4-INIT-0-3] 기존 view config: null

[STEP4-INIT-1] init() 실행 중...
[STEP4-INIT-2] CREATE MODE - 새로운 설정 생성
[STEP4-INIT-3] ✓ 초기화 완료

[STEP4-DOM] DOMContentLoaded 이벤트 발생
[STEP4-DOM] ✓ init() 호출 완료
```

### 제출 단계
```
============================================================
[STEP4-SUBMIT] Step 4 제출 시작
============================================================
[STEP4-SUBMIT-1] form_data 수집 완료
[STEP4-SUBMIT-2] 총 10개 필드 준비됨
[STEP4-SUBMIT-3-0] 필드: ymd
         - label: 작성일
         - display_type: date
         - order: 1
         - width: 30%
         - inline_group: header
         - style_class: field-small
[STEP4-SUBMIT-3-1] 필드: title
         ...
[STEP4-SUBMIT-4] JSON 전송 준비:
{
  "view": {
    "columns": [
      {
        "name": "ymd",
        "label": "작성일",
        "display_type": "date",
        ...
      },
      ...
    ]
  }
}
[STEP4-SUBMIT-5] /boards/new/step4/1로 POST 요청 중...
[STEP4-SUBMIT-6] 응답 상태: 200 OK
[STEP4-SUBMIT-7] 응답 데이터: {redirect: "/boards/new/finish/1"}
[STEP4-SUBMIT-8] ✓ 제출 성공
[STEP4-SUBMIT-9] 리다이렉트: /boards/new/finish/1
============================================================
```

---

## 수정 모드 초기화 예시 (기존 view 설정이 있을 때)

```
[STEP4-INIT-0] Step 4 초기화 시작
[STEP4-INIT-0-3] 기존 view config: {columns: [{name: "ymd", ...}, ...]}

[STEP4-INIT-1] init() 실행 중...
[STEP4-INIT-2] EDIT MODE 감지 - 기존 view 설정 로드

[STEP4-INIT-2-1] 기존 view 설정 로드 시작
[STEP4-INIT-2-1-1] 필드 로드: ymd (섹션: default)
[STEP4-INIT-2-1-2] 필드 로드: title (섹션: default)
...

[STEP4-INIT-2-2] 섹션 추가: default
[STEP4-INIT-2-3-0] 필드 UI 생성: ymd
[STEP4-INIT-2-3-0] ✓ 필드명: ymd
[STEP4-INIT-2-3-0] ✓ 라벨: 작성일
[STEP4-INIT-2-3-0] ✓ 표시타입: date
[STEP4-INIT-OPT] ymd의 옵션 복원 (타입: date)
[STEP4-INIT-OPT]   - format: YYYY년 MM월 DD일

[STEP4-INIT-2-3-1] 필드 UI 생성: title
...

[STEP4-INIT-2-4] ✓ 기존 설정 모두 로드 완료
[STEP4-INIT-3] ✓ 초기화 완료
```

---

## 기능 검증 체크리스트

- ✅ CREATE MODE: 새 보드 생성 시 빈 설정으로 시작
- ✅ EDIT MODE: 기존 view 메타데이터 로드 및 표시
- ✅ 섹션별 필드 그룹화
- ✅ Display type별 옵션 복원 (8가지 타입)
- ✅ 클라이언트 단계별 상세 로깅
- ✅ 서버 단계별 상세 로깅
- ✅ JSON 저장 전후 검증 로깅
- ✅ 메타데이터 키 올바른 사용 ("view")
- ✅ 데이터 정합성 검증

---

## 다음 단계

Step 5(또는 Finish) 페이지에서 보드 생성 완료 상태를 표시하고,
생성된 모든 메타데이터를 확인하는 기능을 구현할 수 있습니다.
