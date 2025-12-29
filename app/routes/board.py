from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import sqlite3
from typing import Optional

from app.core.logger import get_logger
from app.core.deps import get_db_connection, get_current_user_from_cookie
from app.schemas.board import BoardCreate, BoardResponse
from app.schemas.user import User
from app.utils.db_manager import DBManager

logger = get_logger(__name__)

router = APIRouter(prefix="/boards", tags=["boards"])

# ============================================================================
# Board List
# ============================================================================

@router.get("/", response_class=HTMLResponse)
async def list_boards(
    request: Request,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """보드 목록 조회"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    cursor = conn.cursor()

    # boards 테이블에서 모든 보드 조회
    cursor.execute("SELECT id, name, note, physical_table_name, created_at FROM boards ORDER BY created_at DESC")
    boards = [dict(row) for row in cursor.fetchall()]

    logger.info(f"[LIST] ✓ 보드 목록 조회 완료: {len(boards)}개 보드")

    return request.app.state.templates.TemplateResponse(
        "board/list.html",
        {
            "request": request,
            "user": user,
            "boards": boards
        }
    )

# ============================================================================
# Record Pages (HTML Rendering)
# ============================================================================

@router.get("/{board_id}/records", response_class=HTMLResponse)
async def record_list_page(
    request: Request,
    board_id: int,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """기록 목록 페이지"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    db_manager = DBManager(conn)
    board_info = db_manager.get_board_info(board_id)

    if not board_info:
        return RedirectResponse(url="/boards", status_code=status.HTTP_302_FOUND)

    table_meta = db_manager.get_metadata(board_id, "table") or {}
    columns_data = table_meta.get("columns", [])

    return request.app.state.templates.TemplateResponse(
        "record/list.html",
        {
            "request": request,
            "user": user,
            "board": board_info,
            "columns": columns_data
        }
    )


@router.get("/{board_id}/records/new", response_class=HTMLResponse)
async def record_create_page(
    request: Request,
    board_id: int,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """새 기록 생성 페이지"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    db_manager = DBManager(conn)
    board_info = db_manager.get_board_info(board_id)

    if not board_info:
        return RedirectResponse(url="/boards", status_code=status.HTTP_302_FOUND)

    table_meta = db_manager.get_metadata(board_id, "table") or {}
    columns_data = table_meta.get("columns", [])
    create_edit_config = db_manager.get_metadata(board_id, "create_edit")

    return request.app.state.templates.TemplateResponse(
        "record/create.html",
        {
            "request": request,
            "user": user,
            "board": board_info,
            "columns": columns_data,
            "create_edit_config": create_edit_config
        }
    )


@router.get("/{board_id}/records/{record_id}", response_class=HTMLResponse)
async def record_view_page(
    request: Request,
    board_id: int,
    record_id: int,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """기록 상세보기 페이지"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    db_manager = DBManager(conn)
    board_info = db_manager.get_board_info(board_id)

    if not board_info:
        return RedirectResponse(url="/boards", status_code=status.HTTP_302_FOUND)

    table_meta = db_manager.get_metadata(board_id, "table") or {}
    columns_data = table_meta.get("columns", [])
    view_config = db_manager.get_metadata(board_id, "view")

    # 레코드 조회
    physical_table_name = board_info["physical_table_name"]
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {physical_table_name} WHERE id = ?", (record_id,))
    row = cursor.fetchone()

    if not row:
        return RedirectResponse(url=f"/boards/{board_id}/records", status_code=status.HTTP_302_FOUND)

    record = dict(row)

    return request.app.state.templates.TemplateResponse(
        "record/view.html",
        {
            "request": request,
            "user": user,
            "board": board_info,
            "record": record,
            "columns": columns_data,
            "view_config": view_config
        }
    )


@router.get("/{board_id}/records/{record_id}/edit", response_class=HTMLResponse)
async def record_edit_page(
    request: Request,
    board_id: int,
    record_id: int,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """기록 수정 페이지"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    db_manager = DBManager(conn)
    board_info = db_manager.get_board_info(board_id)

    if not board_info:
        return RedirectResponse(url="/boards", status_code=status.HTTP_302_FOUND)

    table_meta = db_manager.get_metadata(board_id, "table") or {}
    columns_data = table_meta.get("columns", [])
    create_edit_config = db_manager.get_metadata(board_id, "create_edit")

    # 레코드 조회
    physical_table_name = board_info["physical_table_name"]
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {physical_table_name} WHERE id = ?", (record_id,))
    row = cursor.fetchone()

    if not row:
        return RedirectResponse(url=f"/boards/{board_id}/records", status_code=status.HTTP_302_FOUND)

    record = dict(row)

    return request.app.state.templates.TemplateResponse(
        "record/edit.html",
        {
            "request": request,
            "user": user,
            "board": board_info,
            "record": record,
            "columns": columns_data,
            "create_edit_config": create_edit_config
        }
    )

# ============================================================================
# 5-Step Board Creation Wizard
# ============================================================================

# Step 1: 테이블 생성 (컬럼 정의)
@router.get("/new/step1", response_class=HTMLResponse)
async def wizard_step1_form(
    request: Request,
    board_id: Optional[int] = None,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Step 1: 기본 정보 및 컬럼 정의 페이지 (신규 생성 또는 기존 수정)"""
    logger.info(f"[GET] GET /boards/new/step1 요청 받음")
    logger.info(f"[GET] 파라미터 - board_id={board_id}")

    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    board_info = None
    columns_data = None
    board_meta = None

    # board_id가 있으면 기존 데이터 조회
    if board_id:
        logger.info(f"[GET] board_id={board_id}로 기존 데이터 조회 시작...")
        db_manager = DBManager(conn)
        board_info = db_manager.get_board_info(board_id)

        if not board_info:
            logger.error(f"[GET] ✗ 보드를 찾을 수 없음 - board_id={board_id}")
            return RedirectResponse(url="/boards/new/step1", status_code=status.HTTP_302_FOUND)

        logger.info(f"[GET] ✓ 보드 정보 찾음: {board_info['name']}")

        board_meta = db_manager.get_metadata(board_id, "table") or {}
        logger.info(f"[GET] ✓ 메타데이터 조회 완료")
        logger.info(f"[GET] 메타데이터: {board_meta}")

        columns_data = board_meta.get("columns", [])
        logger.info(f"[GET] ✓ 컬럼 데이터 추출: {len(columns_data)}개")
        for i, col in enumerate(columns_data, 1):
            logger.info(f"[GET]   → col{i}: {col.get('label')} ({col.get('data_type')})")
    else:
        logger.info(f"[GET] 신규 생성 모드 (board_id 없음)")

    logger.info(f"[GET] ✓ 템플릿 렌더링 시작...")
    return request.app.state.templates.TemplateResponse(
        "board/wizard/step1.html",
        {
            "request": request,
            "user": user,
            "board": board_info,
            "board_meta": board_meta,
            "columns": columns_data,
            "board_id": board_id
        }
    )

@router.post("/new/step1")
async def wizard_step1_submit(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Step 1: Board 생성 및 컬럼 메타데이터 저장 (신규 생성 또는 기존 수정)"""
    try:
        form_data = await request.json()
        logger.info(f"[1] POST /boards/new/step1 요청 받음")

        board_id = form_data.get("board_id")  # 수정 모드인지 신규 모드인지 판단
        board_name = form_data.get("name")
        board_note = form_data.get("note", "")
        is_file_attach = form_data.get("is_file_attach", False)
        columns_data = form_data.get("columns", [])

        logger.info(f"[2] 데이터 파싱 - board_id={board_id}, 보드명={board_name}, 컬럼수={len(columns_data)}")

        db_manager = DBManager(conn)
        cursor = conn.cursor()

        # ===== 신규 생성 모드 =====
        if not board_id:
            logger.info(f"[3] ★ 신규 생성 모드 시작: '{board_name}' 보드 생성 (컬럼 {len(columns_data)}개)")

            # 1. 최대 ID를 구해서 다음 ID 계산
            logger.info(f"[4] 다음 보드 ID 계산 중...")
            cursor.execute("SELECT MAX(id) FROM boards")
            result = cursor.fetchone()
            next_board_id = (result[0] or 0) + 1
            physical_table_name = f"table_{next_board_id}"
            logger.info(f"[5] ✓ 계산 완료: board_id={next_board_id}, 물리테이블명={physical_table_name}")

            # 2. Board 신규 생성 (physical_table_name 포함)
            logger.info(f"[6] boards 테이블에 보드 정보 삽입 중...")
            cursor.execute(
                "INSERT INTO boards (name, note, physical_table_name) VALUES (?, ?, ?)",
                (board_name, board_note, physical_table_name)
            )
            board_id = cursor.lastrowid
            logger.info(f"[7] ✓ 삽입 완료: board_id={board_id}")

            # 3. 컬럼명 자동 생성 및 메타데이터 준비 (설계 문서 준수)
            logger.info(f"[8] 컬럼 메타데이터 준비 중...")
            columns_with_names = []
            for idx, field in enumerate(columns_data, 1):
                col_name = f"col{idx}"
                col_data = {
                    "label": field.get("label"),
                    "data_type": field.get("data_type"),
                    "name": col_name
                }

                # comment는 선택사항
                if field.get("comment"):
                    col_data["comment"] = field.get("comment")

                columns_with_names.append(col_data)
                logger.info(f"     → {col_name}: {col_data['label']} ({col_data['data_type']})")
            logger.info(f"[9] ✓ 메타데이터 준비 완료: {len(columns_with_names)}개 컬럼")

            columns_meta = {
                "name": board_name,
                "note": board_note,
                "is_file_attach": is_file_attach,
                "physical_table_name": physical_table_name,
                "id": board_id,
                "columns": columns_with_names
            }
            logger.info(f"[10] meta_data 테이블에 메타데이터 저장 중...")
            db_manager.save_metadata(board_id, "table", columns_meta)
            logger.info(f"[11] ✓ 메타데이터 저장 완료")

            # 4. 물리 테이블 생성
            logger.info(f"[12] 물리 테이블 생성 중...")
            from app.utils.db_manager import map_sqlite_type
            ddl_columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
            for field in columns_with_names:
                col_type = map_sqlite_type(field.get("data_type", "string"))
                col_name = field.get("name")
                ddl_columns.append(f"{col_name} {col_type}")
                logger.info(f"     → DDL: {col_name} {col_type}")

            ddl_columns.append("created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            ddl_columns.append("updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

            create_table_sql = f"CREATE TABLE {physical_table_name} ({', '.join(ddl_columns)})"
            logger.info(f"[13] SQL 실행: {create_table_sql}")
            logger.info(f"[14] '{physical_table_name}' 물리 테이블 생성 실행 중...")
            cursor.execute(create_table_sql)
            logger.info(f"[15] ✓ 물리 테이블 생성 성공")

            # 5. 테이블 검증 로깅
            logger.info(f"[16] 테이블 구조 검증 중...")
            cursor.execute(f"PRAGMA table_info({physical_table_name})")
            table_info = cursor.fetchall()
            logger.info(f"[17] ✓ 검증 완료: {len(table_info)}개 컬럼 확인됨")
            for col in table_info:
                logger.info(f"     → {col[1]}: {col[2]} (notnull={col[3]}, pk={col[5]})")

            logger.info(f"[18] 트랜잭션 커밋 중...")
            conn.commit()
            logger.info(f"[19] ★★★ 신규 보드 생성 완료! ★★★")
            logger.info(f"     - Board ID: {board_id}")
            logger.info(f"     - Board Name: {board_name}")
            logger.info(f"     - Physical Table: {physical_table_name}")
            logger.info(f"     - Columns: {len(columns_with_names)}개")

        # ===== 수정 모드 =====
        else:
            logger.info(f"[3] ★ 수정 모드 시작: board_id={board_id}, '{board_name}' 보드 수정 (항목 추가만 허용)")

            # 1. 기존 Board 정보 조회
            logger.info(f"[4] 기존 보드 정보 조회 중...")
            existing_board = db_manager.get_board_info(board_id)
            if not existing_board:
                logger.error(f"[5] ✗ 오류: 보드를 찾을 수 없음 (ID={board_id})")
                raise HTTPException(status_code=404, detail="Board not found")

            physical_table_name = existing_board["physical_table_name"]
            logger.info(f"[5] ✓ 기존 보드 찾음: {existing_board['name']} (테이블: {physical_table_name})")

            # 2. 기존 메타데이터에서 컬럼 정보 조회
            logger.info(f"[6] 기존 컬럼 정보 조회 중...")
            existing_table_meta = db_manager.get_metadata(board_id, "table") or {}
            existing_columns = existing_table_meta.get("columns", [])
            existing_column_count = len(existing_columns)
            logger.info(f"[7] ✓ 기존 컬럼 {existing_column_count}개 조회됨")
            for col in existing_columns:
                logger.info(f"     → {col.get('name')}: {col.get('label')} ({col.get('data_type')})")

            # 3. 새로 제출된 컬럼과 기존 컬럼 비교
            logger.info(f"[8] 제출된 컬럼 정보 비교 중...")
            new_column_count = len(columns_data)
            logger.info(f"     → 제출된 컬럼 수: {new_column_count}개, 기존 컬럼 수: {existing_column_count}개")

            # 3-1. 기존 컬럼이 삭제되었는지 확인
            if new_column_count < existing_column_count:
                logger.error(f"[9] ✗ 오류: 기존 컬럼 삭제 불가 - {existing_column_count}개 → {new_column_count}개")
                conn.rollback()
                raise HTTPException(
                    status_code=400,
                    detail=f"기존 항목의 삭제는 허용되지 않습니다. 추가만 가능합니다. (기존: {existing_column_count}개, 제출: {new_column_count}개)"
                )

            # 3-2. 기존 컬럼이 수정되었는지 확인
            if new_column_count >= existing_column_count:
                for idx in range(existing_column_count):
                    existing_col = existing_columns[idx]
                    new_col = columns_data[idx]

                    existing_label = existing_col.get("label")
                    new_label = new_col.get("label")

                    if existing_label != new_label:
                        logger.error(f"[9] ✗ 오류: 기존 항목 수정 불가 - col{idx+1}의 라벨 변경 감지")
                        conn.rollback()
                        raise HTTPException(
                            status_code=400,
                            detail=f"기존 항목의 수정은 허용되지 않습니다. 추가만 가능합니다. (col{idx+1}: {existing_label} → {new_label})"
                        )

            # 4. Board 정보 UPDATE
            logger.info(f"[10] boards 테이블 정보 업데이트 중...")
            cursor.execute(
                "UPDATE boards SET name = ?, note = ? WHERE id = ?",
                (board_name, board_note, board_id)
            )
            logger.info(f"[11] ✓ 보드 정보 업데이트 완료")

            # 5. 새로운 컬럼만 추출
            logger.info(f"[12] 새로 추가된 컬럼 추출 중...")
            new_columns_to_add = []
            from app.utils.db_manager import map_sqlite_type

            for idx in range(existing_column_count, new_column_count):
                field = columns_data[idx]
                col_name = f"col{idx+1}"
                col_data = {
                    "label": field.get("label"),
                    "data_type": field.get("data_type"),
                    "name": col_name
                }
                if field.get("comment"):
                    col_data["comment"] = field.get("comment")
                new_columns_to_add.append(col_data)
                logger.info(f"     → {col_name}: {col_data['label']} ({col_data['data_type']})")

            logger.info(f"[13] ✓ {len(new_columns_to_add)}개 새 컬럼 추출 완료")

            # 6. ALTER TABLE ADD COLUMN 실행
            if len(new_columns_to_add) > 0:
                logger.info(f"[14] ALTER TABLE 명령 실행 중...")
                for col in new_columns_to_add:
                    col_type = map_sqlite_type(col.get("data_type", "string"))
                    col_name = col.get("name")
                    alter_sql = f"ALTER TABLE {physical_table_name} ADD COLUMN {col_name} {col_type}"
                    logger.info(f"     → SQL: {alter_sql}")
                    cursor.execute(alter_sql)
                    logger.info(f"     ✓ {col_name} 추가 완료")
            else:
                logger.info(f"[14] 추가될 새 컬럼이 없습니다.")

            # 7. 메타데이터 준비 (기존 + 새로운 컬럼)
            logger.info(f"[15] 메타데이터 업데이트 준비 중...")
            all_columns = existing_columns + new_columns_to_add

            columns_meta = {
                "name": board_name,
                "note": board_note,
                "is_file_attach": is_file_attach,
                "physical_table_name": physical_table_name,
                "id": board_id,
                "columns": all_columns
            }
            logger.info(f"[16] ✓ 메타데이터 준비 완료: 총 {len(all_columns)}개 컬럼")

            # 8. 메타데이터 UPDATE
            logger.info(f"[17] meta_data 테이블 업데이트 중...")
            db_manager.save_metadata(board_id, "table", columns_meta)
            logger.info(f"[18] ✓ 메타데이터 업데이트 완료")

            # 9. 테이블 검증
            logger.info(f"[19] 테이블 구조 검증 중...")
            cursor.execute(f"PRAGMA table_info({physical_table_name})")
            table_info = cursor.fetchall()
            logger.info(f"[20] ✓ 검증 완료: {len(table_info)}개 컬럼 확인됨")
            for col in table_info:
                logger.info(f"     → {col[1]}: {col[2]}")

            logger.info(f"[21] 트랜잭션 커밋 중...")
            conn.commit()
            logger.info(f"[22] ★★★ 보드 수정 완료! ★★★")
            logger.info(f"     - Board ID: {board_id}")
            logger.info(f"     - Board Name: {board_name}")
            logger.info(f"     - Physical Table: {physical_table_name}")
            logger.info(f"     - 기존 컬럼: {existing_column_count}개, 새 컬럼: {len(new_columns_to_add)}개, 총: {len(all_columns)}개")

        logger.info(f"[25] ✓ 응답 반환: board_id={board_id}")
        return {"board_id": board_id, "redirect": f"/boards/new/step2/{board_id}"}

    except HTTPException as he:
        logger.error(f"[ERROR] HTTP 예외 발생 - Status={he.status_code}, Detail={he.detail}")
        conn.rollback()
        raise
    except Exception as e:
        logger.error(f"[ERROR] Step 1에서 예외 발생: {type(e).__name__}")
        logger.error(f"[ERROR] 메시지: {str(e)}")
        import traceback
        logger.error(f"[ERROR] 스택 트레이스:\n{traceback.format_exc()}")
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Step 2: 목록 설정
@router.get("/new/step2/{board_id}", response_class=HTMLResponse)
async def wizard_step2_form(
    request: Request,
    board_id: int,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Step 2: 목록 화면 설정"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    db_manager = DBManager(conn)
    board_info = db_manager.get_board_info(board_id)

    if not board_info:
        return RedirectResponse(url="/boards/new/step1", status_code=status.HTTP_302_FOUND)

    table_meta = db_manager.get_metadata(board_id, "table") or {}
    columns_data = table_meta.get("columns", [])
    list_meta = db_manager.get_metadata(board_id, "list")

    return request.app.state.templates.TemplateResponse(
        "board/wizard/step2.html",
        {
            "request": request,
            "user": user,
            "board": board_info,
            "columns": columns_data,
            "list_config": list_meta
        }
    )

@router.post("/new/step2/{board_id}")
async def wizard_step2_submit(
    board_id: int,
    request: Request,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Step 2: 목록 설정 저장"""
    try:
        form_data = await request.json()
        list_config = form_data.get("list_config", {})

        logger.info(f"[STEP2-1] 🚀 Step 2 Submit 시작 - board_id={board_id}")
        logger.info(f"[STEP2-2] 전송된 form_data 구조: {list(form_data.keys())}")

        # 목록 설정 상세 로깅
        logger.info(f"[STEP2-3] list_config 받음:")
        logger.info(f"     - view_mode: {list_config.get('view_mode', 'N/A')}")
        logger.info(f"     - display_columns: {len(list_config.get('display_columns', []))}개")
        if list_config.get('display_columns'):
            for idx, col in enumerate(list_config.get('display_columns', [])):
                logger.info(f"       [{idx+1}] {col.get('name')} ({col.get('label')})")

        pagination = list_config.get('pagination', {})
        logger.info(f"     - pagination.enabled: {pagination.get('enabled')}")
        logger.info(f"     - pagination.page_size: {pagination.get('page_size')}")

        sort = list_config.get('default_sort', [])
        if sort:
            logger.info(f"     - default_sort: {sort[0].get('column')} ({sort[0].get('order')})")

        search = list_config.get('search', {})
        logger.info(f"     - search.enabled: {search.get('enabled')}")
        logger.info(f"     - search.simple_fields: {search.get('simple_fields', [])}")

        logger.info(f"[STEP2-4] 데이터베이스에 저장 중...")
        import json
        logger.info(f"[STEP2-5] 저장할 JSON (pretty):\n{json.dumps(list_config, indent=2, ensure_ascii=False)}")

        db_manager = DBManager(conn)
        db_manager.save_metadata(board_id, "list", list_config)

        logger.info(f"[STEP2-6] ✓ 데이터베이스에 저장 완료")
        logger.info(f"[STEP2-7] 메타데이터 검증: board_id={board_id}, type='list'")

        # 저장된 데이터 재확인
        saved_data = db_manager.get_metadata(board_id, "list")
        if saved_data:
            logger.info(f"[STEP2-8] ✅ 저장된 데이터 검증 완료: {len(saved_data.get('display_columns', []))}개 컬럼")
        else:
            logger.warn(f"[STEP2-8] ⚠️ 저장된 데이터 검증 실패: None 반환됨")

        logger.info(f"[STEP2-9] Step 3으로 리다이렉트 중...")
        return {"redirect": f"/boards/new/step3/{board_id}"}

    except Exception as e:
        conn.rollback()
        logger.error(f"[STEP2-ERROR] 예외 발생: {type(e).__name__}")
        logger.error(f"[STEP2-ERROR] 메시지: {str(e)}")
        import traceback
        logger.error(f"[STEP2-ERROR] 스택 트레이스:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

# Step 3: 입력폼 설정
@router.get("/new/step3/{board_id}", response_class=HTMLResponse)
async def wizard_step3_form(
    request: Request,
    board_id: int,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Step 3: 입력 화면 설정"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    db_manager = DBManager(conn)
    board_info = db_manager.get_board_info(board_id)

    if not board_info:
        return RedirectResponse(url="/boards/new/step1", status_code=status.HTTP_302_FOUND)

    table_meta = db_manager.get_metadata(board_id, "table") or {}
    columns_data = table_meta.get("columns", [])
    create_edit_meta = db_manager.get_metadata(board_id, "create_edit")

    return request.app.state.templates.TemplateResponse(
        "board/wizard/step3.html",
        {
            "request": request,
            "user": user,
            "board": board_info,
            "columns": columns_data,
            "create_edit_config": create_edit_meta
        }
    )

@router.post("/new/step3/{board_id}")
async def wizard_step3_submit(
    board_id: int,
    request: Request,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Step 3: 입력 설정 저장"""
    try:
        form_data = await request.json()
        create_edit = form_data.get("create_edit", {})

        logger.info(f"[STEP3-1] 🚀 Step 3 Submit 시작 - board_id={board_id}")
        logger.info(f"[STEP3-2] 전송된 form_data 구조: {list(form_data.keys())}")

        # 입력폼 설정 상세 로깅
        fields = create_edit.get("fields", [])
        logger.info(f"[STEP3-3] create_edit 받음: {len(fields)}개 필드")

        for idx, field in enumerate(fields, 1):
            logger.info(f"     [{idx}] 필드명: {field.get('name')}")
            logger.info(f"         - label: {field.get('label')}")
            logger.info(f"         - data_type: {field.get('data_type')}")
            logger.info(f"         - element: {field.get('element')}")
            logger.info(f"         - element_type: {field.get('element_type')}")
            logger.info(f"         - required: {field.get('required')}")
            logger.info(f"         - order: {field.get('order')}")

            # 조건부 필드 로깅
            if 'width' in field:
                logger.info(f"         - width: {field.get('width')}")
            if 'inline_group' in field:
                logger.info(f"         - inline_group: {field.get('inline_group')}")
            if 'default_value' in field:
                logger.info(f"         - default_value: {field.get('default_value')}")
            if 'min_value' in field:
                logger.info(f"         - min_value: {field.get('min_value')}")
            if 'max_value' in field:
                logger.info(f"         - max_value: {field.get('max_value')}")
            if 'help_text' in field:
                logger.info(f"         - help_text: {field.get('help_text')}")
            if 'options' in field:
                options = field.get('options', [])
                logger.info(f"         - options: {len(options)}개")
                for opt in options:
                    logger.info(f"           • {opt.get('value')} = {opt.get('label')}")

        logger.info(f"[STEP3-4] 데이터베이스에 저장 중...")
        import json
        logger.info(f"[STEP3-5] 저장할 JSON (pretty):\n{json.dumps(create_edit, indent=2, ensure_ascii=False)}")

        db_manager = DBManager(conn)
        db_manager.save_metadata(board_id, "create_edit", create_edit)

        logger.info(f"[STEP3-6] ✓ 데이터베이스에 저장 완료")
        logger.info(f"[STEP3-7] 메타데이터 검증: board_id={board_id}, type='create_edit'")

        # 저장된 데이터 재확인
        saved_data = db_manager.get_metadata(board_id, "create_edit")
        if saved_data:
            saved_fields = saved_data.get("fields", [])
            logger.info(f"[STEP3-8] ✅ 저장된 데이터 검증 완료: {len(saved_fields)}개 필드")
            for idx, field in enumerate(saved_fields, 1):
                logger.info(f"       [{idx}] {field.get('name')} ({field.get('label')})")
        else:
            logger.warn(f"[STEP3-8] ⚠️ 저장된 데이터 검증 실패: None 반환됨")

        logger.info(f"[STEP3-9] Step 4로 리다이렉트 중...")
        return {"redirect": f"/boards/new/step4/{board_id}"}

    except Exception as e:
        conn.rollback()
        logger.error(f"[STEP3-ERROR] 예외 발생: {type(e).__name__}")
        logger.error(f"[STEP3-ERROR] 메시지: {str(e)}")
        import traceback
        logger.error(f"[STEP3-ERROR] 스택 트레이스:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

# Step 4: 상세보기 설정
@router.get("/new/step4/{board_id}", response_class=HTMLResponse)
async def wizard_step4_form(
    request: Request,
    board_id: int,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Step 4: 상세보기(View) 설정"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    db_manager = DBManager(conn)
    board_info = db_manager.get_board_info(board_id)

    if not board_info:
        return RedirectResponse(url="/boards/new/step1", status_code=status.HTTP_302_FOUND)

    table_meta = db_manager.get_metadata(board_id, "table") or {}
    columns_data = table_meta.get("columns", [])
    create_config = db_manager.get_metadata(board_id, "create_edit")
    view_meta = db_manager.get_metadata(board_id, "view")

    return request.app.state.templates.TemplateResponse(
        "board/wizard/step4.html",
        {
            "request": request,
            "user": user,
            "board": board_info,
            "columns": columns_data,
            "create_config": create_config,
            "view_config": view_meta
        }
    )

@router.post("/new/step4/{board_id}")
async def wizard_step4_submit(
    board_id: int,
    request: Request,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Step 4: 상세보기(View) 설정 저장"""
    try:
        form_data = await request.json()
        view_config = form_data.get("view", {})

        logger.info(f"[STEP4-1] 🚀 Step 4 Submit 시작 - board_id={board_id}")
        logger.info(f"[STEP4-2] 전송된 form_data 구조: {list(form_data.keys())}")

        # 표시 필드 상세 로깅
        display_fields = view_config.get("display_fields", [])
        logger.info(f"[STEP4-3] view 설정 받음: {len(display_fields)}개 필드")

        for idx, field in enumerate(display_fields, 1):
            logger.info(f"     [{idx}] 필드명: {field.get('name')}")
            logger.info(f"         - label: {field.get('label')}")
            logger.info(f"         - display_type: {field.get('display_type')}")
            logger.info(f"         - order: {field.get('order')}")

            # 조건부 필드 로깅
            if 'width' in field:
                logger.info(f"         - width: {field.get('width')}")
            if 'inline_group' in field:
                logger.info(f"         - inline_group: {field.get('inline_group')}")
            if 'full_width' in field:
                logger.info(f"         - full_width: {field.get('full_width')}")
            if 'hide_label' in field:
                logger.info(f"         - hide_label: {field.get('hide_label')}")
            if 'style_class' in field:
                logger.info(f"         - style_class: {field.get('style_class')}")
            if 'section' in field:
                logger.info(f"         - section: {field.get('section')}")
            if 'section_title' in field:
                logger.info(f"         - section_title: {field.get('section_title')}")

            # Display type 별 옵션 로깅
            display_type = field.get('display_type')
            if display_type == 'date' and 'format' in field:
                logger.info(f"         - format: {field.get('format')}")
            elif display_type == 'datetime':
                if 'format' in field:
                    logger.info(f"         - format: {field.get('format')}")
                if 'relative' in field:
                    logger.info(f"         - relative: {field.get('relative')}")
            elif display_type == 'stars':
                if 'max_stars' in field:
                    logger.info(f"         - max_stars: {field.get('max_stars')}")
                if 'show_number' in field:
                    logger.info(f"         - show_number: {field.get('show_number')}")
            elif display_type == 'currency':
                if 'currency_code' in field:
                    logger.info(f"         - currency_code: {field.get('currency_code')}")
                if 'decimal_places' in field:
                    logger.info(f"         - decimal_places: {field.get('decimal_places')}")
                if 'thousands_separator' in field:
                    logger.info(f"         - thousands_separator: {field.get('thousands_separator')}")
            elif display_type == 'boolean':
                if 'true_text' in field:
                    logger.info(f"         - true_text: {field.get('true_text')}")
                if 'false_text' in field:
                    logger.info(f"         - false_text: {field.get('false_text')}")
                if 'show_icon' in field:
                    logger.info(f"         - show_icon: {field.get('show_icon')}")
            elif display_type == 'badge' and 'badge_color_map' in field:
                logger.info(f"         - badge_color_map: {field.get('badge_color_map')}")
            elif display_type == 'list':
                if 'display_as' in field:
                    logger.info(f"         - display_as: {field.get('display_as')}")
                if 'separator' in field:
                    logger.info(f"         - separator: {field.get('separator')}")
                if 'hide_if_empty' in field:
                    logger.info(f"         - hide_if_empty: {field.get('hide_if_empty')}")

        logger.info(f"[STEP4-4] 데이터베이스에 저장 중...")
        import json
        logger.info(f"[STEP4-5] 저장할 JSON (pretty):\n{json.dumps(view_config, indent=2, ensure_ascii=False)}")

        db_manager = DBManager(conn)
        db_manager.save_metadata(board_id, "view", view_config)

        logger.info(f"[STEP4-6] ✓ 데이터베이스에 저장 완료")
        logger.info(f"[STEP4-7] 메타데이터 검증: board_id={board_id}, type='view'")

        # 저장된 데이터 재확인
        saved_data = db_manager.get_metadata(board_id, "view")
        if saved_data:
            saved_fields = saved_data.get("display_fields", [])
            logger.info(f"[STEP4-8] ✅ 저장된 데이터 검증 완료: {len(saved_fields)}개 필드")
            for idx, field in enumerate(saved_fields, 1):
                logger.info(f"       [{idx}] {field.get('name')} ({field.get('label')})")
        else:
            logger.warn(f"[STEP4-8] ⚠️ 저장된 데이터 검증 실패: None 반환됨")

        logger.info(f"[STEP4-9] 마무리 페이지로 리다이렉트 중...")
        return {"redirect": f"/boards/new/finish/{board_id}"}

    except Exception as e:
        conn.rollback()
        logger.error(f"[STEP4-ERROR] 예외 발생: {type(e).__name__}")
        logger.error(f"[STEP4-ERROR] 메시지: {str(e)}")
        import traceback
        logger.error(f"[STEP4-ERROR] 스택 트레이스:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

# Finish: 완료 확인
@router.get("/new/finish/{board_id}", response_class=HTMLResponse)
async def wizard_finish(
    request: Request,
    board_id: int,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """보드 생성 완료 페이지"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    db_manager = DBManager(conn)
    board_info = db_manager.get_board_info(board_id)

    if not board_info:
        return RedirectResponse(url="/boards/new/step1", status_code=status.HTTP_302_FOUND)

    return request.app.state.templates.TemplateResponse(
        "board/wizard/finish.html",
        {
            "request": request,
            "user": user,
            "board": board_info
        }
    )

# ============================================================================
# Legacy Endpoints (for backward compatibility)
# ============================================================================

@router.get("/create", response_class=HTMLResponse)
async def create_board_page(user: User = Depends(get_current_user_from_cookie)):
    """게시판 생성 페이지 (레거시 - /new/step1로 리다이렉트)"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    return RedirectResponse(url="/boards/new/step1", status_code=status.HTTP_302_FOUND)

@router.post("/create", response_model=BoardResponse)
def create_board(
    board_data: BoardCreate,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """
    게시판 생성 API (레거시 - 호환성 유지)
    """
    logger.info(f"🚀 Received Board Creation Request: {board_data.board.name}")
    try:
        db_manager = DBManager(conn)
        return db_manager.create_board(board_data)
    except Exception as e:
        # DBManager already logs error
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{board_id}/columns")
def get_board_columns(
    board_id: int,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """
    게시판 컬럼 메타데이터 조회 (Delegates to DBManager)
    """
    db_manager = DBManager(conn)
    result = db_manager.get_board_columns(board_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Columns metadata not found")

    return result

# ============================================================================
# Board Deletion
# ============================================================================

@router.get("/{board_id}/delete-info")
async def get_delete_info(
    board_id: int,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """게시판 삭제 전 필요한 정보 조회: 테이블 존재 여부, 레코드 수"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.info(f"[DELETE-INFO] board_id={board_id} 삭제 정보 조회 시작")

    try:
        db_manager = DBManager(conn)
        board_info = db_manager.get_board_info(board_id)

        if not board_info:
            logger.error(f"[DELETE-INFO] 보드를 찾을 수 없음: board_id={board_id}")
            raise HTTPException(status_code=404, detail="Board not found")

        physical_table_name = board_info["physical_table_name"]
        logger.info(f"[DELETE-INFO] 테이블명: {physical_table_name}")

        # 1. 테이블 존재 여부 확인
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (physical_table_name,)
        )
        table_exists = cursor.fetchone() is not None
        logger.info(f"[DELETE-INFO] 테이블 존재: {table_exists}")

        # 2. 레코드 수 조회
        record_count = 0
        if table_exists:
            cursor.execute(f"SELECT COUNT(*) FROM {physical_table_name}")
            record_count = cursor.fetchone()[0]
            logger.info(f"[DELETE-INFO] 레코드 수: {record_count}")

        return {
            "board_id": board_id,
            "board_name": board_info["name"],
            "table_exists": table_exists,
            "record_count": record_count
        }

    except Exception as e:
        logger.error(f"[DELETE-INFO] 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{board_id}/delete-confirm", response_class=HTMLResponse)
async def delete_confirm_page(
    request: Request,
    board_id: int,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """삭제 확인 페이지 (레코드가 있을 때만)"""
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    logger.info(f"[DELETE-CONFIRM] board_id={board_id} 삭제 확인 페이지 로드")

    try:
        db_manager = DBManager(conn)
        board_info = db_manager.get_board_info(board_id)

        if not board_info:
            logger.error(f"[DELETE-CONFIRM] 보드를 찾을 수 없음: board_id={board_id}")
            return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

        physical_table_name = board_info["physical_table_name"]

        # 레코드 수 조회
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {physical_table_name}")
        record_count = cursor.fetchone()[0]
        logger.info(f"[DELETE-CONFIRM] 레코드 수: {record_count}")

        return request.app.state.templates.TemplateResponse(
            "board/delete_confirm.html",
            {
                "request": request,
                "user": user,
                "board": board_info,
                "record_count": record_count
            }
        )

    except Exception as e:
        logger.error(f"[DELETE-CONFIRM] 오류: {e}")
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

@router.delete("/{board_id}")
async def delete_board(
    board_id: int,
    user: User = Depends(get_current_user_from_cookie),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """게시판 삭제 API"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.info(f"[DELETE] board_id={board_id} 삭제 시작")

    try:
        db_manager = DBManager(conn)
        board_info = db_manager.get_board_info(board_id)

        if not board_info:
            logger.error(f"[DELETE] 보드를 찾을 수 없음: board_id={board_id}")
            raise HTTPException(status_code=404, detail="Board not found")

        physical_table_name = board_info["physical_table_name"]
        logger.info(f"[DELETE] 물리 테이블명: {physical_table_name}")

        cursor = conn.cursor()

        # 1. 물리 테이블 삭제
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {physical_table_name}")
            logger.info(f"[DELETE] ✓ 물리 테이블 삭제: {physical_table_name}")
        except Exception as e:
            logger.warning(f"[DELETE] 테이블 삭제 실패 (무시됨): {e}")

        # 2. meta_data 테이블에서 해당 보드의 모든 메타데이터 삭제
        cursor.execute("DELETE FROM meta_data WHERE board_id = ?", (board_id,))
        logger.info(f"[DELETE] ✓ meta_data 레코드 삭제")

        # 3. boards 테이블에서 해당 보드 삭제
        cursor.execute("DELETE FROM boards WHERE id = ?", (board_id,))
        logger.info(f"[DELETE] ✓ boards 레코드 삭제")

        # 4. 커밋
        conn.commit()
        logger.info(f"[DELETE] ✓ 트랜잭션 커밋 - 게시판 삭제 완료: board_id={board_id}")

        return {"message": "Board deleted successfully", "board_id": board_id}

    except Exception as e:
        conn.rollback()
        logger.error(f"[DELETE] 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))
