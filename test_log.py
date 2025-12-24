from app.core.logger import get_logger
import time

print("--- Starting Log Test ---")
logger = get_logger("test_logger")
logger.info("TEST: This message should appear in TERMINAL and FILE.")
print("--- End Log Test ---")
