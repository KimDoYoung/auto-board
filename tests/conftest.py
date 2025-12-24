import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
import sqlite3

@pytest.fixture
def db_connection():
    # Use in-memory database for testing
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    
    # Create necessary tables for testing (schema validation)
    # Read DDL from app/resources/sqls/autoboard_ddl.sql
    try:
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        sql_path = project_root / "app/resources/sqls/autoboard_ddl.sql"
        
        with open(sql_path, "r", encoding="utf-8") as f:
            ddl_script = f.read()
            
        cursor = conn.cursor()
        cursor.executescript(ddl_script)
        conn.commit()
    except Exception as e:
        pytest.fail(f"Failed to initialize test DB from SQL file: {e}")
    
    yield conn
    
    conn.close()
