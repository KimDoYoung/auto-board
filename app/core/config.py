# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from dotenv import load_dotenv
import os

# 프로필 설정 (환경변수 AUTOBOARD_PROFILE 우선, 없으면 'local')
active_profile = os.getenv("AUTOBOARD_PROFILE", "local")

# 파일 로딩 순서: .env (공통) -> .env.{profile} (환경별 덮어쓰기)
# 명시적으로 로드하여 해결 (Pydantic이 간혹 경로 문제로 못 읽을 수 있음)

load_dotenv(".env")
load_dotenv(f".env.{active_profile}", override=True)

env_files = [".env", f".env.{active_profile}"]

class Settings(BaseSettings):
    #---------------------------------------------------------
    # 앱 기본 정보
    #---------------------------------------------------------
    APP_NAME: str = "Auto-Board"
    VERSION: str = "0.0.1"

    #---------------------------------------------------------
    # 프로필
    #---------------------------------------------------------
    # Note: os.getenv in default is fine, but Pydantic reads env vars automatically if configs are set.
    # We will keep explicit defaults as requested.
    PROFILE_NAME: str = os.getenv("AUTOBOARD_PROFILE", "local")
    
    #---------------------------------------------------------
    # 데이터 디렉토리 (Path objects for easy usage)
    #---------------------------------------------------------
    BASE_DIR: Path = Path(os.getenv("BASE_DIR", "./data"))
    DB_PATH: str = os.getenv("DB_PATH", "./data/db/autoboard.db")
    

    FILES_DIR: Path = Path(os.getenv("FILES_DIR", "./data/files"))
       
    #---------------------------------------------------------
    # 보안
    #---------------------------------------------------------
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    
    #---------------------------------------------------------
    # 실행 
    #---------------------------------------------------------
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    # Boolean env var handling in simple os.getenv is tricky ("False" str is True). 
    # Better to let Pydantic handle bool conversion from env, but we provide default.
    RELOAD: bool = True 
    DEBUG: bool = True
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Path = Path(os.getenv("LOG_FILE", "./data/logs/autoboard.log"))

    model_config = SettingsConfigDict(
        env_file=env_files,
        env_ignore_empty=True,
        extra="ignore"
    )
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure base and required sub-directories exist
        self.BASE_DIR.mkdir(parents=True, exist_ok=True)
        self.FILES_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        Path(self.DB_PATH).parent.mkdir(parents=True, exist_ok=True)

settings = Settings()