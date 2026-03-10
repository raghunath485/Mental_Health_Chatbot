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
    .stApp {
        background: radial-gradient(circle at 50% 50%, #1a1a2e 0%, #16213e 100%);
        color: #e9ecef;
    }
    .auth-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 40px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-top: 50px;
    }
    .stButton > button {
        border-radius: 12px;
        background: linear-gradient(135deg, #4e54c8 0%, #8f94fb 100%);
        border: none;
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(78, 84, 200, 0.4);
    }
    .stChatMessage {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px !important;
        padding: 15px !important;
    }
    .sidebar-content {
        padding: 20px;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 15px;
    }
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
    _, col2, _ = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.title("🧠 Wellness Buddy")
        
        if not st.session_state.show_register:
            st.subheader("Welcome Back")
            with st.form("login_form", clear_on_submit=False):
                user = st.text_input("Username")
                pw = st.text_input("Password", type="password")
                submit = st.form_submit_button("Sign In", use_container_width=True)
                if submit:
                    uid = verify_user(user, pw)
                    if uid:
                        st.session_state.logged_in = True
                        st.session_state.user_id = uid
                        st.rerun()
                    else:
                        st.error("Authentication failed. Check your credentials.")
            
            st.write("---")
            if st.button("New here? Create an Account", use_container_width=True):
                st.session_state.show_register = True
                st.rerun()

        else:
            st.subheader("Join Us")
            with st.form("signup_form", clear_on_submit=False):
                new_user = st.text_input("Choose a Username")
                new_pw = st.text_input("Create Password", type="password")
                confirm_pw = st.text_input("Confirm Password", type="password")
                register = st.form_submit_button("Register Now", use_container_width=True)
                if register:
                    if new_pw != confirm_pw:
                        st.error("Passwords do not match.")
                    elif len(new_pw) < 6:
                        st.warning("Password should be at least 6 characters.")
                    else:
                        try:
                            conn = sqlite3.connect("database/mood_history.db")
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO users (username, password) VALUES (?,?)", 
                                           (new_user, generate_password_hash(new_pw)))
                            conn.commit()
                            conn.close()
                            st.success("Registration complete! You can now log in.")
                            st.session_state.show_register = False
                            time.sleep(1.5)
                            st.rerun()
                        except:
                            st.error("This username is already taken.")
            
            if st.button("Back to Login", use_container_width=True):
                st.session_state.show_register = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def main_app():
    with st.sidebar:
        st.markdown("### 📊 Your Wellness Hub")
        history = get_mood_history(st.session_state.user_id)
        
        if history:
            df = pd.DataFrame(history)
            
            st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
            current_mood = df['emotion'].iloc[0].upper()
            st.metric("Current State", current_mood)
            
            st.write("**Mood Distribution**")
            st.bar_chart(df['emotion'].value_counts(), color="#8f94fb")
            st.markdown('</div>', unsafe_allow_html=True)
            
            with st.expander("Previous Notes"):
                for entry in history[:3]:
                    st.caption(entry['timestamp'])
                    st.write(f"*{entry['message'][:50]}...*")
        else:
            st.info("Start a conversation to see your mood analytics here.")
        
        st.write("---")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.messages = []
            st.rerun()

    st.title("Buddy Chat")
    st.caption("A private space for your thoughts.")

    # Chat Container
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Tell Buddy what's on your mind..."):
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Processing..."):
            emotion, _ = detect_emotion(prompt)
            save_mood(st.session_state.user_id, prompt, emotion)
            response = get_bot_response(prompt, emotion)
            
            # Formatted Reply with design touch
            status_emoji = "✨" if emotion == "joy" else "🌙"
            bot_reply = f"#### {status_emoji} Emotion: {emotion.title()}\n\n{response}"

        with st.chat_message("assistant", avatar="🧠"):
            st.markdown(bot_reply)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

if not st.session_state.logged_in:
    login_page()
else:
    main_app()