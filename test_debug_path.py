from app.core.config import settings
from app.core.logger import get_logger
import sys

print(f"Log Dir: {settings.log_dir}")
print(f"Log File: {settings.log_file}")

logger = get_logger("test_debug")
logger.info("TEST: Console and File")

if settings.log_file.exists():
    print("Log file exists!")
    with open(settings.log_file, "r") as f:
        print(f.read())
else:
    print("Log file does NOT exist.")
