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
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stChatMessage { border-radius: 15px; border: 1px solid #30363d; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

init_user_table()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

def login_page():
    st.title("🧠 Mental Wellness Buddy")
    st.markdown("### Welcome. Let's focus on your well-being.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Login")
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

    with col2:
        st.subheader("Create Account")
        with st.form("signup_form"):
            new_user = st.text_input("Choose Username")
            new_pw = st.text_input("Choose Password", type="password")
            if st.form_submit_button("Register", use_container_width=True):
                try:
                    conn = sqlite3.connect("database/mood_history.db")
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO users (username, password) VALUES (?,?)", 
                                   (new_user, generate_password_hash(new_pw)))
                    conn.commit()
                    conn.close()
                    st.success("Account ready! Please login.")
                except:
                    st.error("Username taken.")

def main_app():
    with st.sidebar:
        st.title("📊 Wellness Hub")
        
        history = get_mood_history(st.session_state.user_id)
        if history:
            df = pd.DataFrame(history)
            st.metric(label="Recent State", value=df['emotion'].iloc[0].title())
            
            st.write("### Emotional Balance")
            st.bar_chart(df['emotion'].value_counts())
            
            with st.expander("📜 Reflection History"):
                for entry in history[:5]:
                    st.caption(f"{entry['timestamp']}")
                    st.write(f"**{entry['emotion'].upper()}**: {entry['message'][:40]}...")
                    st.divider()
        else:
            st.info("Start chatting to see your mood trends!")

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.messages = []
            st.rerun()

    st.title("Buddy Chat")
    st.caption("A supportive space for your thoughts. Crisis? Call 9152987821.")

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