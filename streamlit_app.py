import streamlit as st
import pandas as pd
import time
import sqlite3
from chatbot import get_bot_response
from emotion_detector import detect_emotion
import mood_database as db
from werkzeug.security import generate_password_hash
from streamlit_google_auth import Authenticate

st.set_page_config(page_title="Wellness Buddy", page_icon="🧠", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at 50% 50%, #1a1a2e 0%, #16213e 100%); color: #e9ecef; }
    .auth-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border-radius: 20px; padding: 40px; border: 1px solid rgba(255, 255, 255, 0.1); margin-top: 50px; }
    .stButton > button { border-radius: 12px; background: linear-gradient(135deg, #4e54c8 0%, #8f94fb 100%); border: none; color: white; }
    </style>
    """, unsafe_allow_html=True)

db.init_user_table()

# Make sure you have client_secret.json in your github repo for this to work
authenticator = Authenticate(
    secret_names='client_secret.json',
    cookie_name='wellness_buddy_cookie',
    key='wellness_buddy_key',
    cookie_expiry_days=30,
)

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_session_id" not in st.session_state: st.session_state.current_session_id = None
if "messages" not in st.session_state: st.session_state.messages = []

def login_page():
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.title("🧠 Wellness Buddy")
        
        authenticator.check_authenticity()
        if not st.session_state.get('connected'):
            authenticator.login()
            if st.session_state.get('connected'):
                st.session_state.logged_in = True
                st.session_state.user_id = st.session_state['user_info'].get('email')
                st.rerun()
            st.markdown("<p style='text-align: center;'>OR</p>", unsafe_allow_html=True)
        
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In"):
                uid = db.verify_user(u, p)
                if uid:
                    st.session_state.logged_in, st.session_state.user_id = True, uid
                    st.rerun()
                else: st.error("Failed.")
        st.caption("Developed by Raghunath Panda")
        st.markdown('</div>', unsafe_allow_html=True)

def main_app():
    with st.sidebar:
        if st.button("➕ Start New Chat", use_container_width=True):
            st.session_state.messages, st.session_state.current_session_id = [], None
            st.rerun()
        
        st.divider()
        st.markdown("### 📂 History")
        past = db.get_user_sessions(st.session_state.user_id)
        for s_id, title in past:
            if st.button(f"💬 {title[:20]}", key=f"s_{s_id}", use_container_width=True):
                st.session_state.current_session_id = s_id
                st.session_state.messages = db.get_session_messages(s_id)
                st.rerun()

    st.title("Buddy Chat")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🙋‍♂️" if msg["role"]=="user" else "🧘"):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Message Buddy..."):
        if st.session_state.current_session_id is None:
            st.session_state.current_session_id = db.create_new_session(st.session_state.user_id, prompt)
        
        db.save_chat_message(st.session_state.current_session_id, "user", prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🙋‍♂️"): st.markdown(prompt)

        emotion, _ = detect_emotion(prompt)
        db.save_mood(st.session_state.user_id, prompt, emotion)
        reply = get_bot_response(prompt, emotion, st.session_state.messages)

        db.save_chat_message(st.session_state.current_session_id, "assistant", reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant", avatar="🧘"): st.markdown(reply)

if not st.session_state.logged_in: login_page()
else: main_app()