
import pytest
import sqlite3
import json
from app.utils.db_manager import DBManager
from app.schemas.board import BoardCreate, BoardInfo, BoardMetaColumns, ColumnField

def test_create_board(db_connection):
    # Setup
    manager = DBManager(db_connection)
    
    # Prepare Mock Data
    board_info = BoardInfo(
        name="Test Board",
        physical_table_name="board_test",
        note="This is a test board"
    )
    
    columns = BoardMetaColumns(fields=[
        ColumnField(name="title", label="제목", data_type="string", required=True),
        ColumnField(name="count", label="조회수", data_type="integer", required=False, default_value=0)
    ])
    
    board_create_data = BoardCreate(board=board_info, columns=columns)
    
    # Execution
    response = manager.create_board(board_create_data)
    
    # Verification 1: Response
    assert response.message == "success"
    assert isinstance(response.board_id, int)
    
    # Verification 2: tables (boards)
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM boards WHERE id = ?", (response.board_id,))
    board_row = cursor.fetchone()
    assert board_row is not None
    assert board_row["name"] == "Test Board"
    assert board_row["physical_table_name"] == "board_test"

    # Verification 3: tables (meta_data)
    cursor.execute("SELECT * FROM meta_data WHERE board_id = ?", (response.board_id,))
    meta_row = cursor.fetchone()
    assert meta_row is not None
    assert meta_row["name"] == "columns"
    
    saved_meta = json.loads(meta_row["meta"])
    assert len(saved_meta["fields"]) == 2
    assert saved_meta["fields"][0]["name"] == "title"

    # Verification 4: Physical Table Creation
    # Check if table 'board_test' exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='board_test';")
    table_row = cursor.fetchone()
    assert table_row is not None
    
    # Check columns of physical table
    cursor.execute("PRAGMA table_info(board_test);")
    columns_info = cursor.fetchall()
    # Columns: id, title, count, created_at, updated_at
    col_names = [info[1] for info in columns_info]
    assert "id" in col_names
    assert "title" in col_names
    assert "count" in col_names
    assert "created_at" in col_names


def test_get_board_columns(db_connection):
    # Setup - Manually Insert Metadata
    cursor = db_connection.cursor()
    
    # Create required board first (constraint check might not exist in simplified valid DDL, but good practice)
    cursor.execute("INSERT INTO boards (name, physical_table_name) VALUES ('Mock', 'mock_tbl')")
    board_id = cursor.lastrowid
    
    columns_data = {
        "fields": [
             {"name": "author", "label": "작성자", "data_type": "string", "required": True},
        ]
    }
    
    cursor.execute(
        "INSERT INTO meta_data (board_id, name, meta, schema) VALUES (?, ?, ?, ?)",
        (board_id, "columns", json.dumps(columns_data), "v1")
    )
    db_connection.commit()
    
    # Execution
    manager = DBManager(db_connection)
    result = manager.get_board_columns(board_id)
    
    # Verification
    assert result is not None
    assert result["fields"][0]["name"] == "author"
    assert result["fields"][0]["label"] == "작성자"

def test_get_board_columns_not_found(db_connection):
    manager = DBManager(db_connection)
    result = manager.get_board_columns(99999) # Non-existent ID
    assert result is None
