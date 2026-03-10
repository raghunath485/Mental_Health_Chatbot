import sqlite3
from datetime import datetime
from werkzeug.security import check_password_hash

DB_NAME = "database/mood_history.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_user_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            emotion TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

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
    cursor.execute("""
        INSERT INTO mood_logs (user_id, message, emotion, timestamp)
        VALUES (?, ?, ?, ?)
    """, (user_id, message, emotion, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
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