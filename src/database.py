import sqlite3
from datetime import datetime

DATABASE_FILE = "queue.db"


def get_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queue (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            started_at TEXT,
            completed_at TEXT,
            consumer_id TEXT
        )
    """)
    
    conn.commit()
    conn.close()


def dict_from_row(row):
    if row is None:
        return None
    return dict(row)
