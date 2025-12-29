"""
Auto-Board: 개인용 기록물 관리
"""

import signal
import sys
import sqlite3
from pathlib import Path

# 프로젝트 루트 디렉토리를 sys.path에 추가 (python ./app/main.py 실행을 위해)
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """FastAPI 애플리케이션 생성"""
    app = FastAPI(
        title="Auto-Board",
        description="개인용 기록물 관리",
        version=settings.VERSION,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
    )
    
    # 라우터, 정적파일, 이벤트 핸들러 등록
    add_routes(app)
    add_statics(app)
    add_templates(app)
    add_events(app)
    
    return app


def get_directory_path(subdir: str) -> Path:
    """PyInstaller 환경을 고려한 디렉토리 경로 반환"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 번들 실행 중
        bundle_dir = Path(sys._MEIPASS)
        return bundle_dir / "app" / subdir
    else:
        # 개발 환경
        base_dir = Path(__file__).parent
        return base_dir / subdir


def add_statics(app: FastAPI):
    """정적 파일 설정"""
    static_dir = get_directory_path("static")
    
    # static 디렉토리 존재 확인 및 생성
    if not static_dir.exists():
        logger.warning(f"Static 디렉토리가 없습니다: {static_dir}")
        static_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"📁 Static 디렉토리: {static_dir}")
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


def add_templates(app: FastAPI):
    """템플릿 설정"""
    template_dir = get_directory_path("templates")
    
    if not template_dir.exists():
        logger.warning(f"Template 디렉토리가 없습니다: {template_dir}")
        template_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"📁 Template 디렉토리: {template_dir}")
    templates = Jinja2Templates(directory=str(template_dir))
    
    # App state에 저장
    app.state.templates = templates


def add_routes(app: FastAPI):
    """라우터 등록"""
    # 라우터 import는 여기서
    from app.routes.home import router as home_router
    from app.routes.board import router as board_router
    from app.routes.records import router as records_router
    from app.routes.checker import router as checker_router
    from app.routes.files import router as files_router

    app.include_router(home_router)
    app.include_router(board_router) # prefix is defined in board.py
    app.include_router(records_router) # prefix is defined in records.py
    app.include_router(checker_router)
    app.include_router(files_router)


def add_events(app: FastAPI):
    """이벤트 핸들러 등록"""
    
    @app.on_event("startup")
    async def startup_event():
        """애플리케이션 시작 시 초기화"""
        logger.info("=" * 60)
        logger.info(f"✳️  {settings.APP_NAME} v{settings.VERSION}")
        logger.info(f"📋 Profile: {settings.PROFILE_NAME}")
        logger.info("=" * 60)
        logger.info(f"🌐 Host: {settings.HOST}:{settings.PORT}")
        logger.info(f"💾 Base Directory: {settings.BASE_DIR}")
        logger.info(f"🐛 Debug: {'✅ ON' if settings.DEBUG else '❌ OFF'}")
        logger.info(f"📝 Log Level: {settings.LOG_LEVEL}")
        logger.info(f"📂 Log File: {settings.LOG_FILE}")
        logger.info(f"📂 DB Path: {settings.DB_PATH}")

        # Uvicorn 로그도 파일에 남기도록 설정
        get_logger("uvicorn")
        get_logger("uvicorn.access")
        get_logger("uvicorn.error")
        
        # DB 초기화
        init_db()
        
        logger.info("=" * 60)
        logger.info("✅ 초기화 완료")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """애플리케이션 종료 시 정리 작업"""
        logger.info("=" * 60)
        logger.info(f"🛑 {settings.APP_NAME} 종료")
        logger.info("=" * 60)



def init_db():
    """데이터베이스 초기화"""
    db_path = settings.DB_PATH
    
    if not Path(db_path).exists():
        logger.info(f"🆕 데이터베이스 파일이 없습니다. 생성을 시작합니다: {db_path}")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    # DB 연결 및 스키마 초기화 (파일 존재 여부 상관없이 테이블 없으면 생성 체크)
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # SQL 파일 경로 찾기
        sql_path = get_directory_path("resources/sqls/autoboard_ddl.sql")
        
        if not sql_path.exists():
             logger.error(f"❌ SQL 파일을 찾을 수 없습니다: {sql_path}")
             raise FileNotFoundError(f"SQL file not found: {sql_path}")

        # DDL 실행
        with open(sql_path, "r", encoding="utf-8") as f:
            schema_ddl = f.read()
            cursor.executescript(schema_ddl)
            logger.info(f"✅ 스키마 초기화 완료 ({sql_path.name})")
        

        
    except Exception as e:
        logger.error(f"❌ 데이터베이스 초기화 실패: {e}")
        # DB 파일이 생성되었으나 초기화 실패 시 삭제 고려? (현재는 유지)
        raise e
    finally:
        if 'conn' in locals():
            conn.close()


# 앱 인스턴스 생성
app = create_app()


def signal_handler(signum, frame):
    """시그널 핸들러"""
    logger.info(f"\n⚠️  시그널 수신: {signum}")
    logger.info("🛑 서버 종료 중...")
    sys.exit(0)


def run_server():
    """서버 실행"""
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🚀 서버 시작...")
    
    uvicorn_kwargs = {
        "app": "app.main:app",
        "host": settings.HOST,
        "port": settings.PORT,
        "reload": settings.RELOAD if hasattr(settings, 'RELOAD') else False,
        "log_level": settings.LOG_LEVEL.lower(),
    }
    
    # PyInstaller 환경에서는 reload 비활성화
    if getattr(sys, 'frozen', False):
        uvicorn_kwargs["reload"] = False
    
    uvicorn.run(**uvicorn_kwargs)


if __name__ == "__main__":
    run_server()