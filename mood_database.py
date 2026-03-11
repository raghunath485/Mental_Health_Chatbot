import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Consistent database path for all entry points
DB_NAME = os.path.join("database", "mood_history.db")
os.makedirs(os.path.dirname(DB_NAME), exist_ok=True)

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Enables accessing columns by name
    return conn

def init_user_table():
    """Initializes all required tables for the project."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS mood_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, message TEXT, emotion TEXT, timestamp TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS chat_sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, title TEXT, created_at TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS chat_messages (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER, role TEXT, content TEXT, timestamp TEXT)")
    conn.commit()
    conn.close()

def create_account(username, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        hashed_pw = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return True, user_id, None
    except sqlite3.IntegrityError:
        return False, None, "Username already exists."
    except Exception as e:
        return False, None, str(e)

def verify_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and check_password_hash(user["password"], password):
        return user["id"]
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
    cursor = conn.cursor()
    cursor.execute("SELECT message, emotion, timestamp FROM mood_logs WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

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
    cursor.execute("SELECT id, title FROM chat_sessions WHERE user_id = ? ORDER BY id DESC", (user_id,))
    sessions = cursor.fetchall()
    conn.close()
    return sessions

def get_session_messages(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM chat_messages WHERE session_id = ? ORDER BY id ASC", (session_id,))
    messages = [{"role": row["role"], "content": row["content"]} for row in cursor.fetchall()]
    conn.close()
    return messages