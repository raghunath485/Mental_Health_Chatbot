import streamlit as st
import pandas as pd
from chatbot import get_bot_response
from emotion_detector import detect_emotion
from mood_database import save_mood, get_mood_history, init_user_table, verify_user
from werkzeug.security import generate_password_hash
import sqlite3

# Initial Setup
st.set_page_config(page_title="Wellness Buddy", page_icon="🧠", layout="centered")
init_user_table() # Ensure users table exists 

# Session State for Authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- AUTHENTICATION UI ---
def login_page():
    st.title("🧠 Mental Wellness Buddy")
    tab1, tab2 = st.tabs(["Login", "Create Account"])
    
    with tab1:
        with st.form("login_form"):
            user = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                uid = verify_user(user, pw)
                if uid:
                    st.session_state.logged_in = True
                    st.session_state.user_id = uid
                    st.rerun()
                else:
                    st.error("Invalid username or password")

    with tab2:
        with st.form("signup_form"):
            new_user = st.text_input("New Username")
            new_pw = st.text_input("New Password", type="password")
            if st.form_submit_button("Sign Up"):
                try:
                    conn = sqlite3.connect("database/mood_history.db")
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO users (username, password) VALUES (?,?)", 
                                   (new_user, generate_password_hash(new_pw)))
                    conn.commit()
                    conn.close()
                    st.success("Account created! Please login.")
                except:
                    st.error("Username already exists.")

# --- MAIN APP UI ---
def main_app():
    st.title("🧠 Mental Wellness Buddy")
    
    # Sidebar for Dashboard and Logout
    with st.sidebar:
        st.header("📊 Your Dashboard")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.messages = []
            st.rerun()
            
        st.divider()
        if st.button("Show Mood Trends"):
            history = get_mood_history(st.session_state.user_id)
            if history:
                df = pd.DataFrame(history)
                st.write("Recent Moods:")
                st.bar_chart(df['emotion'].value_counts())
            else:
                st.info("No data yet.")

    # Chat Interface 
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("How are you feeling?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI Processing Logic 
        emotion, _ = detect_emotion(prompt)
        save_mood(st.session_state.user_id, prompt, emotion)
        response = get_bot_response(prompt, emotion)
        
        full_reply = f"**Detected Emotion: {emotion}**\n\n{response}"
        
        with st.chat_message("assistant"):
            st.markdown(full_reply)
        st.session_state.messages.append({"role": "assistant", "content": full_reply})

# Routing Logic
if not st.session_state.logged_in:
    login_page()
else:
    main_app()