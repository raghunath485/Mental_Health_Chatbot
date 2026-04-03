import time

import pandas as pd
import plotly.express as px
import streamlit as st

from chatbot import generate_wellness_snapshot, get_bot_response
from emotion_detector import detect_emotion
import mood_database as db


st.set_page_config(
    page_title="Mental Wellness Buddy",
    page_icon="MW",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(102, 194, 165, 0.18), transparent 30%),
            radial-gradient(circle at top right, rgba(52, 152, 219, 0.15), transparent 25%),
            linear-gradient(135deg, #07131f, #0f2333 55%, #122b2f);
        color: #f4fbfd;
        font-family: "Segoe UI", sans-serif;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .panel {
        background: rgba(7, 19, 31, 0.72);
        border: 1px solid rgba(196, 243, 255, 0.12);
        border-radius: 22px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 18px 40px rgba(0, 0, 0, 0.18);
    }
    .hero {
        background: linear-gradient(135deg, rgba(39, 174, 96, 0.2), rgba(52, 152, 219, 0.16));
        border: 1px solid rgba(196, 243, 255, 0.15);
        border-radius: 24px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .eyebrow {
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.78rem;
        color: #99d9cf;
        margin-bottom: 0.35rem;
    }
    .title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }
    .support-note {
        background: rgba(255, 196, 0, 0.12);
        border-left: 4px solid #f5c542;
        border-radius: 14px;
        padding: 0.85rem 1rem;
        margin-bottom: 1rem;
        color: #fff5cf;
    }
    .metric-tile {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(196, 243, 255, 0.08);
        border-radius: 18px;
        padding: 1rem;
        min-height: 112px;
    }
    .metric-label {
        color: #a3c8d4;
        font-size: 0.85rem;
        margin-bottom: 0.35rem;
    }
    .metric-value {
        font-size: 1.7rem;
        font-weight: 700;
        color: #f4fbfd;
    }
    .session-caption {
        font-size: 0.8rem;
        color: #a9c2cf;
        margin-top: 0.25rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        border: 1px solid rgba(196, 243, 255, 0.12);
        background: linear-gradient(135deg, #1f6f5f, #207ea8);
        color: white;
        font-weight: 600;
    }
    .stChatMessage {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(196, 243, 255, 0.08);
        border-radius: 18px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


db.init_user_table()

DEFAULT_SUGGESTIONS = [
    "I feel overwhelmed with work and cannot switch off.",
    "I have been lonely lately and want to talk.",
    "Today felt better than yesterday and I want to understand why.",
]

for key, value in {
    "logged_in": False,
    "messages": [],
    "current_session_id": None,
    "show_dashboard": False,
    "show_signup": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = value



def reset_chat_state():
    st.session_state.messages = []
    st.session_state.current_session_id = None



def start_new_chat(seed_text=None):
    reset_chat_state()
    if seed_text:
        handle_prompt(seed_text)



def load_session(session_id):
    st.session_state.current_session_id = session_id
    st.session_state.messages = [
        {"role": row["role"], "content": row["content"], "emotion": row.get("emotion")}
        for row in db.get_session_messages(session_id)
    ]



def render_header():
    st.markdown(
        """
        <div class='hero'>
            <div class='eyebrow'>Mental Wellness Companion</div>
            <div class='title'>A calmer, more accountable daily check-in space</div>
            <div>This app now behaves more like a real support product: it stores conversation history, surfaces mood trends, and responds more carefully to higher-risk language.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class='support-note'>
            This app is for reflection and emotional check-ins, not medical diagnosis or emergency care. If you may be in immediate danger, contact local emergency services or a crisis hotline now.
        </div>
        """,
        unsafe_allow_html=True,
    )



def login_page():
    left, center, right = st.columns([1, 1.25, 1])
    with center:
        render_header()
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        if not st.session_state.show_signup:
            st.subheader("Sign in")
            st.caption("Use your account to keep mood history and pick up past conversations.")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login", use_container_width=True)
                if submitted:
                    uid = db.verify_user(username, password)
                    if uid:
                        st.session_state.logged_in = True
                        st.session_state.user_id = uid
                        st.rerun()
                    st.error("Invalid username or password.")

            if st.button("Create account", use_container_width=True):
                st.session_state.show_signup = True
                st.rerun()
        else:
            st.subheader("Create account")
            st.caption("Passwords are stored as hashes, and your chat history stays local in SQLite.")
            with st.form("signup_form"):
                username = st.text_input("Choose a username")
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm password", type="password")
                submitted = st.form_submit_button("Register", use_container_width=True)
                if submitted:
                    if password != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        ok, uid, error = db.create_account(username, password)
                        if ok:
                            st.session_state.logged_in = True
                            st.session_state.user_id = uid
                            st.session_state.show_signup = False
                            st.rerun()
                        st.error(error)

            if st.button("Back to login", use_container_width=True):
                st.session_state.show_signup = False
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)



def dashboard():
    render_header()
    if st.button("Back to chat"):
        st.session_state.show_dashboard = False
        st.rerun()

    mood_history = db.get_mood_history(st.session_state.user_id)
    if not mood_history:
        st.info("No mood check-ins yet. Start a conversation and the dashboard will fill in automatically.")
        return

    summary = db.get_emotion_summary(st.session_state.user_id)
    df = pd.DataFrame(mood_history)
    weekly_df = pd.DataFrame(summary["weekly_distribution"])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"<div class='metric-tile'><div class='metric-label'>Total check-ins</div><div class='metric-value'>{summary['total_checkins']}</div></div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"<div class='metric-tile'><div class='metric-label'>Dominant emotion</div><div class='metric-value'>{summary['dominant_emotion'].title()}</div></div>",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"<div class='metric-tile'><div class='metric-label'>Check-in streak</div><div class='metric-value'>{summary['streak_days']} day(s)</div></div>",
            unsafe_allow_html=True,
        )

    chart_left, chart_right = st.columns(2)
    with chart_left:
        st.markdown("### Emotion distribution")
        fig = px.pie(
            df,
            names="emotion",
            hole=0.55,
            color="emotion",
            color_discrete_sequence=px.colors.sequential.Tealgrn,
        )
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), legend_title_text="Emotion")
        st.plotly_chart(fig, use_container_width=True)

    with chart_right:
        st.markdown("### Last 7 days")
        fig = px.bar(
            weekly_df,
            x="date",
            y="count",
            color="dominant_emotion",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), xaxis_title=None, yaxis_title="Check-ins")
        st.plotly_chart(fig, use_container_width=True)

    insight_left, insight_right = st.columns([1.2, 1])
    with insight_left:
        st.markdown("### Recent reflections")
        recent_df = df.head(6).copy()
        for _, row in recent_df.iterrows():
            st.markdown(
                f"<div class='panel'><strong>{row['emotion'].title()}</strong> on {row['timestamp']}<br>{row['message']}</div>",
                unsafe_allow_html=True,
            )
    with insight_right:
        st.markdown("### Wellness snapshot")
        st.markdown(f"<div class='panel'>{generate_wellness_snapshot(mood_history[:10])}</div>", unsafe_allow_html=True)
        st.markdown("### Coaching prompts")
        st.markdown(
            "<div class='panel'>Try asking: What pattern do you see in my week? Or say: Help me reset after a stressful day.</div>",
            unsafe_allow_html=True,
        )



def render_sidebar():
    with st.sidebar:
        st.title("Care workspace")
        if st.button("Open dashboard"):
            st.session_state.show_dashboard = True
            st.rerun()

        st.markdown("### Quick start")
        for prompt in DEFAULT_SUGGESTIONS:
            if st.button(prompt, key=f"starter-{prompt}"):
                start_new_chat(prompt)
                st.rerun()

        st.divider()

        mood_history = db.get_mood_history(st.session_state.user_id, limit=5)
        summary = db.get_emotion_summary(st.session_state.user_id)
        latest_emotion = mood_history[0]["emotion"].title() if mood_history else "None yet"
        st.markdown(
            f"<div class='metric-tile'><div class='metric-label'>Latest emotion</div><div class='metric-value'>{latest_emotion}</div><div class='session-caption'>Streak: {summary['streak_days']} day(s)</div></div>",
            unsafe_allow_html=True,
        )

        st.divider()
        st.markdown("### Conversations")
        if st.button("Start new chat"):
            start_new_chat()
            st.rerun()

        sessions = db.get_user_sessions(st.session_state.user_id)
        if not sessions:
            st.caption("No saved conversations yet.")
        for session in sessions[:8]:
            label = session["title"] or "Conversation"
            if st.button(label, key=f"session-{session['id']}"):
                load_session(session["id"])
                st.rerun()
            st.caption(f"{session['message_count']} messages")

        st.divider()
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.show_dashboard = False
            reset_chat_state()
            st.rerun()



def handle_prompt(prompt):
    if st.session_state.current_session_id is None:
        st.session_state.current_session_id = db.create_new_session(st.session_state.user_id, prompt)

    db.save_chat_message(st.session_state.current_session_id, "user", prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    emotion, confidence = detect_emotion(prompt)
    db.save_mood(st.session_state.user_id, prompt, emotion, confidence)

    reply = get_bot_response(prompt, emotion, st.session_state.messages)
    db.save_chat_message(st.session_state.current_session_id, "assistant", reply, emotion)
    st.session_state.messages.append({"role": "assistant", "content": reply, "emotion": emotion})
    return reply, emotion, confidence



def main_chat():
    if st.session_state.show_dashboard:
        dashboard()
        return

    render_sidebar()
    render_header()

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Check in")
    st.caption("Share what happened, what you are feeling, or what kind of support you need right now.")

    if not st.session_state.messages:
        st.info("Start with a sentence or use one of the suggested prompts in the sidebar.")

    for msg in st.session_state.messages:
        avatar = "You" if msg["role"] == "user" else "Buddy"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("emotion"):
                st.caption(f"Detected emotion: {msg['emotion']}")

    prompt = st.chat_input("How are you feeling today?")
    if prompt:
        with st.chat_message("user", avatar="You"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="Buddy"):
            thinking = st.empty()
            thinking.markdown("Working through your check-in carefully...")
            time.sleep(0.6)
            reply, emotion, confidence = handle_prompt(prompt)
            thinking.empty()
            st.markdown(reply)
            st.caption(f"Detected emotion: {emotion} ({confidence:.0%} confidence)")

        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


if not st.session_state.logged_in:
    login_page()
else:
    main_chat()
