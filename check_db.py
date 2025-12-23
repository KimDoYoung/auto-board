import sqlite3
import os

db_path = "c:/tmp/auto-board/autoboard.db"
if not os.path.exists(db_path):
    print("DB file not found")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", [t[0] for t in tables])
