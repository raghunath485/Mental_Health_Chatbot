import streamlit as st
import pandas as pd
import time
from chatbot import get_bot_response
from emotion_detector import detect_emotion
import mood_database as db

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Wellness Buddy", 
    page_icon="🧠", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. Custom CSS Styling ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at 50% 50%, #1a1a2e 0%, #16213e 100%); color: #e9ecef; }
    .auth-card { 
        background: rgba(255, 255, 255, 0.05); 
        backdrop-filter: blur(10px); 
        border-radius: 20px; 
        padding: 40px; 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        margin-top: 50px; 
    }
    .stButton > button { 
        border-radius: 12px; 
        background: linear-gradient(135deg, #4e54c8 0%, #8f94fb 100%); 
        border: none; 
        color: white; 
        font-weight: 600; 
    }
    .stChatMessage { 
        background: rgba(255, 255, 255, 0.03) !important; 
        border-radius: 15px !important; 
        border: 1px solid rgba(255, 255, 255, 0.05) !important; 
    }
    </style>
    """, unsafe_allow_html=True)

db.init_user_table()

# --- 3. Session State Initialization ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

def login_page():
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.title("🧠 Wellness Buddy")
        
        if not st.session_state.show_signup:
            st.subheader("Sign In")
            with st.form("manual_login"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Sign In", use_container_width=True):
                    uid = db.verify_user(u, p)
                    if uid:
                        st.session_state.logged_in, st.session_state.user_id = True, uid
                        st.rerun()
                    else: st.error("Invalid Credentials.")
            
            if st.button("Create New Account", use_container_width=True):
                st.session_state.show_signup = True
                st.rerun()
        else:
            st.subheader("Create Account")
            with st.form("signup_form"):
                new_u = st.text_input("New Username")
                new_p = st.text_input("New Password", type="password")
                new_p2 = st.text_input("Confirm Password", type="password")
                if st.form_submit_button("Sign Up", use_container_width=True):
                    if new_p != new_p2:
                        st.error("Passwords do not match.")
                    else:
                        ok, user_id, err = db.create_account(new_u, new_p)
                        if ok:
                            st.session_state.logged_in, st.session_state.user_id = True, user_id
                            st.session_state.show_signup = False
                            st.rerun()
                        else: st.error(err)
            if st.button("Back to Login", use_container_width=True):
                st.session_state.show_signup = False
                st.rerun()

        st.caption("Developed by Raghunath Panda")
        st.markdown('</div>', unsafe_allow_html=True)

def main_app():
    with st.sidebar:
        st.markdown("### 📊 Emotion History Dashboard")
        
        # Dashboard Components
        mood_data = db.get_mood_history(st.session_state.user_id)
        if mood_data:
            df = pd.DataFrame(mood_data)
            
            # Summary Metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Latest State", df['emotion'].iloc[0].upper())
            with col2:
                dominant_mood = df['emotion'].mode()[0].upper()
                st.metric("Dominant Mood", dominant_mood)
            
            # Detailed History Log
            with st.expander("🕒 View Detailed History"):
                for _, row in df.head(10).iterrows():
                    st.markdown(f"**{row['timestamp']}** | *{row['emotion'].upper()}*\n> {row['message'][:60]}...\n---")
            
            # Bar Chart
            st.bar_chart(df['emotion'].value_counts(), color="#8f94fb")
        else:
            st.info("Start chatting to build your dashboard!")

        st.divider()
        if st.button("➕ Start New Chat", use_container_width=True):
            st.session_state.messages, st.session_state.current_session_id = [], None
            st.rerun()
        
        st.markdown("### 📂 Previous Chats")
        history_list = db.get_user_sessions(st.session_state.user_id)
        for s_id, title in history_list:
            if st.button(f"💬 {title[:20]}...", key=f"session_{s_id}", use_container_width=True):
                st.session_state.current_session_id = s_id
                st.session_state.messages = db.get_session_messages(s_id)
                st.rerun()

        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    st.title("Buddy Chat")
    for msg in st.session_state.messages:
        avatar = "🙋‍♂️" if msg["role"] == "user" else "🧘"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    if prompt := st.chat_input("How are you feeling today?"):
        if st.session_state.current_session_id is None:
            st.session_state.current_session_id = db.create_new_session(st.session_state.user_id, prompt)

        db.save_chat_message(st.session_state.current_session_id, "user", prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🙋‍♂️"):
            st.markdown(prompt)

        # Silent emotion tracking
        emotion, _ = detect_emotion(prompt)
        db.save_mood(st.session_state.user_id, prompt, emotion)
        
        # Natural response generation without technical headers
        reply = get_bot_response(prompt, emotion, st.session_state.messages)

        db.save_chat_message(st.session_state.current_session_id, "assistant", reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant", avatar="🧘"):
            st.markdown(reply)

if not st.session_state.logged_in:
    login_page()
else:
    main_app()