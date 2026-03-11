import os
import sqlite3
from datetime import datetime
from werkzeug.security import check_password_hash

DB_NAME = "database/mood_history.db"

# Ensure the database directory always exists, regardless of entry point
os.makedirs(os.path.dirname(DB_NAME), exist_ok=True)


def get_connection():
    return sqlite3.connect(DB_NAME)

def init_user_table():
    conn = get_connection()
    cursor = conn.cursor()
    # User authentication
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    # Analytics data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            message TEXT,
            emotion TEXT,
            timestamp TEXT
        )
    """)
    # Chat grouping
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            title TEXT,
            created_at TEXT
        )
    """)
    # Message storage
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            role TEXT,
            content TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()


def init_db():
    """
    Backwards-compatible initializer expected by the Flask app.
    Currently just delegates to init_user_table so all tables exist.
    """
    init_user_table()
def create_new_session(user_id, title):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_sessions (user_id, title, created_at) VALUES (?, ?, ?)",
                   (user_id, title, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def save_chat_message(session_id, role, content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                   (session_id, role, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_user_sessions(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM chat_sessions WHERE user_id=? ORDER BY id DESC", (user_id,))
    sessions = cursor.fetchall()
    conn.close()
    return sessions

def get_session_messages(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM chat_messages WHERE session_id=? ORDER BY id ASC", (session_id,))
    messages = [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
    conn.close()
    return messages

def verify_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and check_password_hash(user[1], password):
        return user[0]
    return None

def save_mood(user_id, message, emotion):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO mood_logs (user_id, message, emotion, timestamp) VALUES (?, ?, ?, ?)",
                   (user_id, message, emotion, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_mood_history(user_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT message, emotion, timestamp FROM mood_logs WHERE user_id=? ORDER BY timestamp DESC", (user_id,))
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return data


def get_emotion_stats(user_id):
    """
    Return a list of (emotion, count) tuples for the given user_id.
    Used by the /emotion-stats route in the Flask app.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT emotion, COUNT(*) as count
        FROM mood_logs
        WHERE user_id = ?
        GROUP BY emotion
        """,
        (user_id,),
    )
    stats = cursor.fetchall()
    conn.close()
    return stats