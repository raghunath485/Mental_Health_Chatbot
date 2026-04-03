import os
import sqlite3
from collections import Counter
from datetime import datetime, timedelta

from werkzeug.security import check_password_hash, generate_password_hash


DB_NAME = os.path.join("database", "mood_history.db")
os.makedirs(os.path.dirname(DB_NAME), exist_ok=True)


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_user_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            emotion TEXT,
            confidence REAL DEFAULT 0,
            timestamp TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            created_at TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            role TEXT,
            content TEXT,
            emotion TEXT,
            timestamp TEXT
        )
        """
    )

    for table, column, definition in [
        ("mood_logs", "confidence", "REAL DEFAULT 0"),
        ("chat_messages", "emotion", "TEXT"),
    ]:
        existing = [row["name"] for row in cursor.execute(f"PRAGMA table_info({table})").fetchall()]
        if column not in existing:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    conn.commit()
    conn.close()


def create_account(username, password):
    username = (username or "").strip()
    password = password or ""

    if len(username) < 3:
        return False, None, "Username must be at least 3 characters long."
    if len(password) < 6:
        return False, None, "Password must be at least 6 characters long."

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
    except Exception as exc:
        return False, None, str(exc)


def verify_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username = ?", ((username or "").strip(),))
    user = cursor.fetchone()
    conn.close()
    if user and check_password_hash(user["password"], password):
        return user["id"]
    return None


def save_mood(user_id, message, emotion, confidence=0.0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO mood_logs (user_id, message, emotion, confidence, timestamp) VALUES (?, ?, ?, ?, ?)",
        (user_id, message, emotion, confidence, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()


def get_mood_history(user_id, limit=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT message, emotion, confidence, timestamp FROM mood_logs WHERE user_id = ? ORDER BY timestamp DESC"
    params = [user_id]
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    rows = cursor.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def create_new_session(user_id, title):
    clean_title = (title or "New conversation").strip()[:60] or "New conversation"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_sessions (user_id, title, created_at) VALUES (?, ?, ?)",
        (user_id, clean_title, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id


def save_chat_message(session_id, role, content, emotion=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_messages (session_id, role, content, emotion, timestamp) VALUES (?, ?, ?, ?, ?)",
        (session_id, role, content, emotion, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()


def get_user_sessions(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    sessions = cursor.execute(
        """
        SELECT
            cs.id,
            cs.title,
            cs.created_at,
            MAX(cm.timestamp) AS last_message_at,
            COUNT(cm.id) AS message_count
        FROM chat_sessions cs
        LEFT JOIN chat_messages cm ON cs.id = cm.session_id
        WHERE cs.user_id = ?
        GROUP BY cs.id, cs.title, cs.created_at
        ORDER BY COALESCE(MAX(cm.timestamp), cs.created_at) DESC
        """,
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in sessions]


def get_session_messages(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    messages = [
        dict(row)
        for row in cursor.execute(
            "SELECT role, content, emotion, timestamp FROM chat_messages WHERE session_id = ? ORDER BY id ASC",
            (session_id,),
        ).fetchall()
    ]
    conn.close()
    return messages


def get_emotion_summary(user_id):
    history = get_mood_history(user_id)
    if not history:
        return {
            "total_checkins": 0,
            "dominant_emotion": "No data",
            "dominant_count": 0,
            "streak_days": 0,
            "weekly_distribution": [],
        }

    counts = Counter(item["emotion"] for item in history)
    dominant_emotion, dominant_count = counts.most_common(1)[0]

    days = sorted({item["timestamp"].split(" ")[0] for item in history}, reverse=True)
    streak_days = 0
    current_day = datetime.now().date()
    for day_text in days:
        logged_day = datetime.strptime(day_text, "%Y-%m-%d").date()
        if logged_day == current_day - timedelta(days=streak_days):
            streak_days += 1
        elif logged_day < current_day - timedelta(days=streak_days):
            break

    weekly_distribution = []
    for offset in range(6, -1, -1):
        day = datetime.now().date() - timedelta(days=offset)
        day_text = day.strftime("%Y-%m-%d")
        day_logs = [item for item in history if item["timestamp"].startswith(day_text)]
        weekly_distribution.append(
            {
                "date": day_text,
                "count": len(day_logs),
                "dominant_emotion": Counter(item["emotion"] for item in day_logs).most_common(1)[0][0]
                if day_logs
                else "none",
            }
        )

    return {
        "total_checkins": len(history),
        "dominant_emotion": dominant_emotion,
        "dominant_count": dominant_count,
        "streak_days": streak_days,
        "weekly_distribution": weekly_distribution,
    }
