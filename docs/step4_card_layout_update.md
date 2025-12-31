# Step 4 카드 레이아웃 업데이트

## 변경 요약

Step 4 상세보기 설정 화면을 카드 기반 UI로 개선했습니다.

### 주요 변경사항

#### 1. **자동 필드 표시 (테이블 메타데이터 기반)**

✅ **모든 필드 자동 로드**
- `table` 메타데이터의 컬럼 정보를 자동으로 읽어옴
- 각 필드가 개별 카드로 표시됨
- 필드를 삭제할 필요 없이 속성만 설정

**코드:**
```javascript
populateFieldsFromColumns() {
    if (this.columns && this.columns.length > 0) {
        this.columns.forEach((col, idx) => {
            this.addField(1, col);  // ← 컬럼 데이터와 함께 전달
        });
    }
}
```

#### 2. **카드 기반 UI 디자인**

각 필드는 다음 구조로 표시됩니다:

```
┌─────────────────────────────────────┐
│ 필드 라벨 [data_type] ✕ 제거 버튼   │ ← 헤더
├─────────────────────────────────────┤
│ 표시 타입: [dropdown]              │
│ 너비: [input]                      │
│ 라벨: [input]                      │
├─────────────────────────────────────┤
│ 인라인 그룹: [input]                │
│ ☐ 전체 너비  ☐ 라벨 숨기기        │
├─────────────────────────────────────┤
│ 스타일 클래스: [dropdown]           │
├─────────────────────────────────────┤
│ [Display type별 옵션들...]          │
└─────────────────────────────────────┘
```

#### 3. **향상된 필드 정보 표시**

카드 헤더에 다음 정보 표시:
- 필드 라벨 (큰 텍스트)
- 데이터 타입 배지 (예: `string`, `integer`, `date`)
- 필드명 (코드)

**예시:**
```
제목 [string]
필드명: title
```

#### 4. **개선된 스타일 옵션**

기존 스타일 외에 추가된 스타일:
- `field-tiny`: 매우 작은 텍스트
- `field-success`: 성공 상태
- `field-warning`: 경고 상태
- `field-danger`: 위험 상태
- `field-card`: 카드 스타일
- `field-divider`: 구분선

#### 5. **데이터 타입별 자동 기본값**

컬럼의 데이터 타입에 따라 자동으로 표시 타입 설정:

| 데이터 타입 | 기본 표시 타입 |
|-----------|--------------|
| `ymd` | date |
| `datetime` | datetime |
| `integer` | text |
| `float` | currency |
| `boolean` | boolean |
| `text` | html |
| `string` | text |

---

## 구현 상세

### 변경된 메서드

#### `populateFieldsFromColumns()`

**이전:**
```javascript
// 컬럼 구조를 가정: columns.fields[...]
// 각 컬럼을 수동으로 선택해서 추가
```

**현재:**
```javascript
// 컬럼 구조: columns[...]
// 모든 컬럼을 자동으로 카드로 변환
populateFieldsFromColumns() {
    console.log('[STEP4-INIT-3-1] populateFieldsFromColumns 시작');

    if (this.columns && this.columns.length > 0) {
        const fieldsContainer = document.querySelector('[data-section-fields="1"]');
        console.log(`[STEP4-INIT-3-2] 총 ${this.columns.length}개 컬럼 발견`);

        this.columns.forEach((col, idx) => {
            console.log(`[STEP4-INIT-3-3-${idx}] 필드 추가: ${col.name} (${col.label})`);
            this.addField(1, col);  // ← 컬럼 데이터 전달
        });

        console.log('[STEP4-INIT-3-4] ✓ populateFieldsFromColumns 완료');
    }
}
```

#### `addField(sectionIndex, columnData = null)`

**개선 사항:**
- `columnData` 매개변수 추가 (옵션)
- 카드 기반 UI 생성
- 필드 헤더에 라벨과 데이터 타입 표시
- 자동으로 기본 display_type 설정

**헤더 구조:**
```html
<div class="flex justify-between items-start gap-3">
    <div class="flex-1">
        <span class="text-lg font-bold">${columnData.label}</span>
        <span class="text-xs bg-indigo-100">${columnData.data_type}</span>
        <p class="text-xs text-gray-500">필드명: ${columnData.name}</p>
    </div>
    <button onclick="viewStep4.removeField(this)">✕ 제거</button>
</div>
```

---

## CREATE vs EDIT MODE 동작

### CREATE MODE (새 보드)
```
Step 4 로드
  ↓
1. 기본 섹션 생성 (addSection)
  ↓
2. 모든 컬럼을 카드로 표시 (populateFieldsFromColumns)
  ↓
3. 각 필드의 표시 타입, 너비, 스타일 설정
  ↓
4. JSON 미리보기 업데이트
```

### EDIT MODE (기존 보드 수정)
```
Step 4 로드 (기존 view 메타데이터 있음)
  ↓
1. loadExistingConfig() 호출
  ↓
2. 섹션별로 필드 재구성
  ↓
3. 각 필드의 이전 설정값 복원
  ↓
4. Display type별 옵션 복원
```

---

## 로깅 추가

### 초기화 단계 로그

```
[STEP4-INIT-3-1] populateFieldsFromColumns 시작
[STEP4-INIT-3-2] 총 10개 컬럼 발견
[STEP4-INIT-3-3-0] 필드 추가: ymd (날짜)
[STEP4-INIT-3-3-1] 필드 추가: title (제목)
...
[STEP4-INIT-3-4] ✓ populateFieldsFromColumns 완료
[STEP4-INIT-ADD-FIELD] 필드 추가됨: ymd (index: 1)
[STEP4-INIT-ADD-FIELD] 필드 추가됨: title (index: 2)
...
```

---

## 카드 UI 레이아웃

### 필드 카드 내부 구조

**Row 1: 기본 표시 설정 (grid-cols-3)**
- 표시 타입 (dropdown)
- 너비 (input)
- 라벨 텍스트 (input)

**Row 2: 레이아웃 옵션 (grid-cols-3)**
- 인라인 그룹 (input)
- 전체 너비 (checkbox)
- 라벨 숨기기 (checkbox)

**Row 3: 스타일 설정**
- 스타일 클래스 (dropdown with 15 options)

**Row 4: Display type별 옵션**
- 동적으로 생성되는 형식별 설정 (date, datetime, stars, currency 등)

---

## 예시: 생성된 JSON

### 입력 (UI)
```
[카드 1] 날짜
  - 표시 타입: date
  - 너비: 30%
  - 라벨: 작성일
  - 포맷: YYYY년 MM월 DD일

[카드 2] 제목
  - 표시 타입: text
  - 너비: (비어있음 → 자동)
  - 라벨: 제목
  - 전체 너비: 체크
  - 스타일: field-title
```

### 출력 (JSON)
```json
{
  "view": {
    "columns": [
      {
        "name": "ymd",
        "label": "작성일",
        "display_type": "date",
        "order": 1,
        "width": "30%",
        "format": "YYYY년 MM월 DD일"
      },
      {
        "name": "title",
        "label": "제목",
        "display_type": "text",
        "order": 2,
        "full_width": true,
        "style_class": "field-title"
      }
    ]
  }
}
```

---

## 사용 흐름

### 1️⃣ 페이지 로드
```
GET /boards/new/step4/{board_id}
  ↓
table 메타데이터의 컬럼 정보 로드
  ↓
columns 배열로 변환
  ↓
populateFieldsFromColumns() 실행
  ↓
모든 필드가 카드로 표시됨
```

### 2️⃣ 속성 설정
```
각 카드에서:
- 표시 타입 선택
- 너비/스타일 설정
- Display type별 옵션 구성
```

### 3️⃣ 제출
```
POST /boards/new/step4/{board_id}
{
  "view": {
    "columns": [...]
  }
}
  ↓
메타데이터 저장
  ↓
마무리 페이지로 리다이렉트
```

---

## 키 개선사항

| 항목 | 이전 | 현재 |
|------|------|------|
| 필드 선택 | 드롭다운 선택 | 자동으로 모두 표시 |
| UI 스타일 | 테이블 형식 | 카드 형식 |
| 필드 정보 | 필드명만 표시 | 라벨 + 데이터 타입 표시 |
| 초기 설정 | 수동 설정 | 자동 기본값 |
| 스타일 옵션 | 8가지 | 15가지 |

---

## 테스트 체크리스트

- ✅ CREATE MODE에서 모든 필드 자동 표시
- ✅ EDIT MODE에서 기존 설정 로드 및 복원
- ✅ 카드별로 속성 독립적 설정 가능
- ✅ Display type 변경 시 옵션 동적 생성
- ✅ JSON 미리보기 실시간 업데이트
- ✅ 브라우저 console 로그 확인
- ✅ 제출 시 올바른 JSON 생성

---

## 기술 스택

- **Frontend:** Alpine.js (reactive), TailwindCSS (styling)
- **Data Flow:** Table metadata → Columns → Cards UI → View metadata JSON
- **Logging:** Console logs for debugging (client-side) + Server logs (server-side)
