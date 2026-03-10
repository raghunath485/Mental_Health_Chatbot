import streamlit as st
import pandas as pd
import time
from chatbot import get_bot_response
from emotion_detector import detect_emotion
from mood_database import save_mood, get_mood_history, init_user_table, verify_user
from werkzeug.security import generate_password_hash
import sqlite3

st.set_page_config(
    page_title="Wellness Buddy", 
    page_icon="🧠", 
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stChatMessage { border-radius: 15px; border: 1px solid #30363d; margin-bottom: 10px; }
    .auth-footer { text-align: center; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

init_user_table()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_register" not in st.session_state:
    st.session_state.show_register = False

def login_page():
    st.title("🧠 Mental Wellness Buddy")
    
    if not st.session_state.show_register:
        st.subheader("Sign In")
        with st.form("login_form"):
            user = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In", use_container_width=True):
                uid = verify_user(user, pw)
                if uid:
                    st.session_state.logged_in = True
                    st.session_state.user_id = uid
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
        
        st.markdown('<div class="auth-footer">', unsafe_allow_html=True)
        if st.button("New user? Create an account"):
            st.session_state.show_register = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.subheader("Create Account")
        with st.form("signup_form"):
            new_user = st.text_input("Choose Username")
            new_pw = st.text_input("Choose Password", type="password")
            confirm_pw = st.text_input("Confirm Password", type="password")
            if st.form_submit_button("Register Account", use_container_width=True):
                if new_pw != confirm_pw:
                    st.error("Passwords do not match.")
                else:
                    try:
                        conn = sqlite3.connect("database/mood_history.db")
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO users (username, password) VALUES (?,?)", 
                                       (new_user, generate_password_hash(new_pw)))
                        conn.commit()
                        conn.close()
                        st.success("Registration successful! Please sign in.")
                        st.session_state.show_register = False
                        time.sleep(1)
                        st.rerun()
                    except:
                        st.error("Username already exists.")
        
        if st.button("Already have an account? Sign In"):
            st.session_state.show_register = False
            st.rerun()

def main_app():
    with st.sidebar:
        st.title("📊 Wellness Hub")
        history = get_mood_history(st.session_state.user_id)
        if history:
            df = pd.DataFrame(history)
            st.metric(label="Recent State", value=df['emotion'].iloc[0].title())
            st.write("### Emotional Balance")
            st.bar_chart(df['emotion'].value_counts())
        
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.messages = []
            st.rerun()

    st.title("Buddy Chat")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Tell me what's on your mind..."):
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Buddy is listening..."):
            emotion, _ = detect_emotion(prompt)
            save_mood(st.session_state.user_id, prompt, emotion)
            response = get_bot_response(prompt, emotion)
            bot_reply = f"**Detected Emotion: {emotion.title()}**\n\n{response}"

        with st.chat_message("assistant", avatar="🧠"):
            st.markdown(bot_reply)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

if not st.session_state.logged_in:
    login_page()
else:
    main_app()