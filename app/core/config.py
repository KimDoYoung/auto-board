# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os

# 프로필 설정 (환경변수 AUTOBOARD_PROFILE 우선, 없으면 'local')
active_profile = os.getenv("AUTOBOARD_PROFILE", "local")
# 파일 로딩 순서: .env (공통) -> .env.{profile} (환경별 덮어쓰기)
env_files = [".env", f".env.{active_profile}"]

class Settings(BaseSettings):
    # 앱 기본 정보
    APP_NAME: str = "Auto-Board"
    VERSION: str = "0.0.1"
    PROFILE_NAME: str = active_profile
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    DEBUG: bool = True
        
    # 데이터 디렉토리
    BASE_DIR: str = "./data"
    DB_NAME: str = "autoboard.db"
    FILES_DIR: str = "files"
    
    # 로그 설정
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = BASE_DIR + "/logs"
    LOG_FILE: str = LOG_DIR + "/autoboard.log"

    # 보안
    SECRET_KEY: str = "your-secret-key-change-this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    model_config = SettingsConfigDict(
        env_file=env_files,
        env_ignore_empty=True,
        extra="ignore"
    )
    
    @property
    def db_path(self) -> Path:
        return Path(self.BASE_DIR) / self.DB_NAME
    
    @property
    def files_path(self) -> Path:
        return Path(self.BASE_DIR) / self.FILES_DIR

settings = Settings()