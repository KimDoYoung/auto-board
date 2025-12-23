# Auto-Board

## 개요

- 개인용 기록물 관리(메타 데이터 기반 게시판)

## 기술스택

- FastAPI
- Jinja2
- SQLite
- JWT
- Alpine.js
- Quill.js
- TailwindCSS

## 폴더 구성

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

## 실행

```bash
set AUTOBOARD_PROFILE=local && python -m uvicorn app.main:app --reload
```
