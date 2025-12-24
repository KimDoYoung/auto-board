from app.core.config import settings
from app.core.logger import get_logger
import sys
import logging

logger = get_logger("test_debug_2")
print(f"Logger: {logger.name}")
print(f"Handlers: {logger.handlers}")
for h in logger.handlers:
    print(f"  - {h} (Type: {type(h)})")
    if isinstance(h, logging.StreamHandler):
         print(f"    - Stream: {h.stream}")

logger.info("TEST: Console and File 2")
