#!/bin/bash

# Clean Database Script
# Deletes all records from boards and meta_data tables

DB_PATH="/c/tmp/auto-board/db/autoboard.db"

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    echo "❌ 데이터베이스를 찾을 수 없음: $DB_PATH"
    exit 1
fi

echo "🧹 데이터베이스 청소 시작..."
echo "📍 DB 경로: $DB_PATH"
echo ""

# [1] Get all physical table names from boards table
echo "[1] 📋 동적 테이블 조회 중..."
TABLES=$(sqlite3 "$DB_PATH" "SELECT physical_table_name FROM boards;")

# [2] Drop all physical tables
if [ -n "$TABLES" ]; then
    echo "[2] 🗑️  동적 테이블 삭제 중..."
    while IFS= read -r TABLE; do
        if [ -n "$TABLE" ]; then
            echo "     → $TABLE 삭제 중..."
            sqlite3 "$DB_PATH" "DROP TABLE IF EXISTS $TABLE;" 2>/dev/null
            if [ $? -eq 0 ]; then
                echo "       ✓ $TABLE 삭제 완료"
            fi
        fi
    done <<< "$TABLES"
else
    echo "[2] ℹ️  삭제할 동적 테이블 없음"
fi

# [3] Delete meta_data records
echo "[3] 🗑️  meta_data 테이블 정리 중..."
sqlite3 "$DB_PATH" "DELETE FROM meta_data;" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✓ meta_data 정리 완료"
fi

# [4] Delete boards records
echo "[4] 🗑️  boards 테이블 정리 중..."
sqlite3 "$DB_PATH" "DELETE FROM boards;" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✓ boards 정리 완료"
fi

# [5] Verify cleanup
echo ""
echo "✅ 데이터베이스 청소 완료"
echo ""
echo "📊 현재 상태:"
sqlite3 "$DB_PATH" << EOF
SELECT
    'boards' as table_name,
    COUNT(*) as count
FROM boards
UNION ALL
SELECT
    'meta_data' as table_name,
    COUNT(*) as count
FROM meta_data;
EOF
