import sqlite3
from datetime import datetime


DB_NAME = "database/mood_history.db"




def get_connection():
    return sqlite3.connect(DB_NAME)




def init_db():

    conn = get_connection()
    cursor = conn.cursor()

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

    conn.commit()
    conn.close()




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
    cursor = conn.cursor()

    cursor.execute("""
        SELECT emotion, timestamp
        FROM mood_logs
        WHERE user_id=?
        ORDER BY timestamp DESC
    """, (user_id,))

    data = cursor.fetchall()

    conn.close()

    return data




def get_daily_moods(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DATE(timestamp), emotion
        FROM mood_logs
        WHERE user_id=?
        ORDER BY timestamp
    """, (user_id,))

    data = cursor.fetchall()

    conn.close()

    return data




def get_emotion_stats(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT emotion, COUNT(*)
        FROM mood_logs
        WHERE user_id=?
        GROUP BY emotion
    """, (user_id,))

    stats = cursor.fetchall()

    conn.close()

    return stats