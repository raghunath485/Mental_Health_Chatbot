from flask import Flask, render_template, request, jsonify, redirect, url_for
from emotion_detector import detect_emotion
from chatbot import get_bot_response

from mood_database import (
    init_db,
    init_user_table,
    save_mood,
    get_mood_history,
    get_emotion_stats
)

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    UserMixin,
    current_user
)

from werkzeug.security import generate_password_hash, check_password_hash

import sqlite3
import os

app = Flask(__name__)
app.secret_key = "mental_wellness_secret"

DB_FOLDER = "database"
DB_PATH = os.path.join(DB_FOLDER, "mood_history.db")

os.makedirs(DB_FOLDER, exist_ok=True)

init_db()
init_user_table()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    if current_user.is_authenticated:
        return render_template("index.html")
    return redirect(url_for("login"))

@app.route("/chat", methods=["POST"])
@login_required
def process_chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"reply": "Please type a message so I can help you."})
    emotion, confidence = detect_emotion(user_message)
    save_mood(current_user.id, user_message, emotion)
    bot_response = get_bot_response(user_message, emotion)
    return jsonify({
        "reply": bot_response,
        "emotion": emotion
    })

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/mood-data")
@login_required
def mood_data():
    data = get_mood_history(current_user.id)
    return jsonify(data)

@app.route("/emotion-stats")
@login_required
def emotion_stats():
    stats = get_emotion_stats(current_user.id)
    result = {}
    for emotion, count in stats:
        result[emotion] = count
    return jsonify(result)

@app.route("/signup", methods=["GET", "POST"])
@app.route("/register", methods=["GET", "POST"])
def signup():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm = request.form.get("confirm_password")
        if confirm and password != confirm:
            error = "Passwords do not match. Please try again."
            return render_template("signup.html", error=error)
        password_hash = generate_password_hash(password)
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username,password) VALUES (?,?)",
                (username, password_hash)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            error = "Username already exists. Please try another."
        finally:
            conn.close()
        if error:
            return render_template("signup.html", error=error)
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id,password FROM users WHERE username=?",
            (username,)
        )
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password):
            login_user(User(user["id"]))
            return redirect(url_for("home"))
        else:
            error = "Invalid username or password. Please try again."
    return render_template("login.html", error=error)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    print("Starting Mental Wellness Buddy server...")
    app.run(debug=True)