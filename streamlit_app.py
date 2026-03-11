import streamlit as st
import pandas as pd
import time
import sqlite3
from chatbot import get_bot_response
from emotion_detector import detect_emotion
from mood_database import save_mood, get_mood_history, init_user_table, verify_user
from werkzeug.security import generate_password_hash

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Wellness Buddy", 
    page_icon="🧠", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS Styling ---
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
    .stChatMessage {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Session State & Database Initialization ---
init_user_table()

for key in ["logged_in", "user_id", "messages", "show_register", "show_graph"]:
    if key not in st.session_state:
        st.session_state[key] = False if "show" in key or "logged" in key else (None if "id" in key else [])

# --- 4. Login and Registration Logic ---
def login_page():
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.title("🧠 Wellness Buddy")
        
        if not st.session_state.show_register:
            st.subheader("Sign In")
            with st.form("login_form"):
                user = st.text_input("Username")
                pw = st.text_input("Password", type="password")
                if st.form_submit_button("Sign In", use_container_width=True):
                    uid = verify_user(user, pw)
                    if uid:
                        st.session_state.logged_in, st.session_state.user_id = True, uid
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")
            
            if st.button("New user? Create Account", use_container_width=True):
                st.session_state.show_register = True
                st.rerun()
            
            st.caption("Developed by Raghunath Panda")
                
        else:
            st.subheader("Create Account")
            with st.form("signup_form"):
                new_user = st.text_input("Username")
                new_pw = st.text_input("Password", type="password")
                confirm = st.text_input("Confirm Password", type="password")
                if st.form_submit_button("Register", use_container_width=True):
                    if new_pw != confirm:
                        st.error("Passwords do not match.")
                    else:
                        try:
                            conn = sqlite3.connect("database/mood_history.db")
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO users (username, password) VALUES (?,?)", 
                                           (new_user, generate_password_hash(new_pw)))
                            conn.commit()
                            conn.close()
                            st.success("Account ready! Please sign in.")
                            st.session_state.show_register = False
                            time.sleep(1); st.rerun()
                        except:
                            st.error("Username already exists.")
            
            if st.button("Back to Login", use_container_width=True):
                st.session_state.show_register = False
                st.rerun()

            st.caption("Developed by Raghunath Panda")

        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. Main Chat Interface ---
def main_app():
    with st.sidebar:
        st.markdown("### 📊 Wellness Insights")
        history = get_mood_history(st.session_state.user_id)
        
        if history:
            df = pd.DataFrame(history)
            st.metric("Current State", df['emotion'].iloc[0].upper())
            if st.button("📈 Toggle Mood Graph", use_container_width=True):
                st.session_state.show_graph = not st.session_state.show_graph
            if st.session_state.show_graph:
                st.bar_chart(df['emotion'].value_counts(), color="#8f94fb")
            with st.expander("Recent History"):
                for entry in history[:3]:
                    st.write(f"**{entry['emotion'].title()}**: {entry['message'][:40]}...")
        else:
            st.info("Start chatting to see trends.")
        
        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in, st.session_state.messages = False, []
            st.rerun()

    st.title("Buddy Chat")
    
    # Render previous messages with updated avatars
    for msg in st.session_state.messages:
        avatar_icon = "🙋‍♂️" if msg["role"] == "user" else "🧘"
        with st.chat_message(msg["role"], avatar=avatar_icon):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Tell Buddy what's on your mind..."):
        # User Message
        with st.chat_message("user", avatar="🙋‍♂️"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Assistant Processing
        with st.spinner("Processing..."):
            emotion, _ = detect_emotion(prompt)
            save_mood(st.session_state.user_id, prompt, emotion)
            response = get_bot_response(prompt, emotion)
            bot_reply = f"#### Emotion: {emotion.title()}\n\n{response}"

        # Assistant Message
        with st.chat_message("assistant", avatar="🧘"):
            st.markdown(bot_reply)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

# --- 6. Router ---
if not st.session_state.logged_in:
    login_page()
else:
    main_app()