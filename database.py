import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "chat_history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_name TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            role TEXT,
            content TEXT,
            metadata TEXT,
            created_at TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)
    conn.commit()
    conn.close()

def create_session(name=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()
    name = name or f"Chat {now[:16]}"
    c.execute("INSERT INTO sessions (session_name, created_at, updated_at) VALUES (?, ?, ?)",
              (name, now, now))
    session_id = c.lastrowid
    conn.commit()
    conn.close()
    return session_id

def save_message(session_id, role, content, metadata=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""
        INSERT INTO messages (session_id, role, content, metadata, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (session_id, role, content, json.dumps(metadata or {}), now))
    c.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (now, session_id))
    conn.commit()
    conn.close()

def load_session_messages(session_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT role, content, metadata, created_at
        FROM messages WHERE session_id = ?
        ORDER BY created_at ASC
    """, (session_id,))
    rows = c.fetchall()
    conn.close()
    messages = []
    for row in rows:
        msg = {
            "role": row[0],
            "content": row[1],
            "metadata": json.loads(row[2]) if row[2] else {},
            "created_at": row[3]
        }
        messages.append(msg)
    return messages

def get_all_sessions():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, session_name, updated_at FROM sessions ORDER BY updated_at DESC")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "updated_at": r[2]} for r in rows]

def delete_session(session_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    c.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()

def rename_session(session_id, new_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE sessions SET session_name = ? WHERE id = ?", (new_name, session_id))
    conn.commit()
    conn.close()