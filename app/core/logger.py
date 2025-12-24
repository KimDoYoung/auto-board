import logging
from concurrent_log_handler import ConcurrentRotatingFileHandler
from app.core.config import settings
import os


# Global file handler to be reused
_file_handler = None

def get_file_handler():
    global _file_handler
    if _file_handler:
        return _file_handler
        
    LOG_FILE = str(settings.LOG_FILE)
    
        
    _file_handler = ConcurrentRotatingFileHandler(
        LOG_FILE, "a", 5*1024*1024, 7, encoding='utf-8'
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    _file_handler.setFormatter(formatter)
    return _file_handler

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)
    
    # Add file handler if not present
    file_handler = get_file_handler()
    if file_handler not in logger.handlers:
        logger.addHandler(file_handler)
        
    # Add console handler if local and no handlers existed (to avoid double console logging if uvicorn set it up)
    # But for fresh loggers, we want console.
    # Simple check: if ONLY file handler is there (meaning we just added it), add console.
    # Or strict check: if no StreamHandler.
    
    logger.disabled = False
    
    if settings.PROFILE_NAME == "local":
        # FileHandler inherits from StreamHandler, so we must be specific
        # We want to check if there is a handler that is strictly for console/stream (not a file)
        has_console = any(
            isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler) 
            for h in logger.handlers
        )
        if not has_console:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            # Force stdout
            import sys
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

    return logger


# 로그 파일 읽기 함수 추가
def read_log_file(lines=1000):
    """로그 파일의 마지막 N줄을 읽어옵니다."""
    try:
        with open(settings.LOG_FILE, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            return all_lines[-lines:] if len(all_lines) > lines else all_lines
    except FileNotFoundError:
        return ["로그 파일을 찾을 수 없습니다."]
    except Exception as e:
        return [f"로그 파일 읽기 오류: {str(e)}"]