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
    :root {
        --bg-1: #041018;
        --bg-2: #0a1f2a;
        --bg-3: #102d33;
        --glass: rgba(8, 22, 32, 0.68);
        --glass-strong: rgba(10, 25, 36, 0.82);
        --line: rgba(173, 244, 255, 0.14);
        --line-strong: rgba(173, 244, 255, 0.22);
        --text-main: #effbfd;
        --text-soft: #9fc7cf;
        --mint: #73f0c1;
        --aqua: #6ccdf7;
        --gold: #ffd37d;
        --shadow: 0 24px 60px rgba(0, 0, 0, 0.28);
    }

    .stApp {
        background:
            radial-gradient(circle at 15% 20%, rgba(115, 240, 193, 0.14), transparent 24%),
            radial-gradient(circle at 85% 12%, rgba(108, 205, 247, 0.16), transparent 20%),
            radial-gradient(circle at 50% 75%, rgba(255, 211, 125, 0.08), transparent 22%),
            linear-gradient(135deg, var(--bg-1) 0%, var(--bg-2) 48%, var(--bg-3) 100%);
        color: var(--text-main);
        font-family: "Trebuchet MS", "Segoe UI", sans-serif;
    }

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        background-image:
            linear-gradient(rgba(255, 255, 255, 0.018) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.018) 1px, transparent 1px);
        background-size: 48px 48px;
        mask-image: radial-gradient(circle at center, black 48%, transparent 95%);
        opacity: 0.4;
    }

    .block-container {
        padding-top: 1.3rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }

    .panel {
        background: linear-gradient(180deg, rgba(12, 29, 42, 0.82), rgba(8, 19, 29, 0.72));
        border: 1px solid var(--line);
        border-radius: 24px;
        padding: 1.15rem 1.2rem;
        box-shadow: var(--shadow);
        backdrop-filter: blur(20px);
    }

    .hero {
        position: relative;
        overflow: hidden;
        background:
            radial-gradient(circle at top right, rgba(108, 205, 247, 0.18), transparent 30%),
            linear-gradient(135deg, rgba(14, 40, 49, 0.94), rgba(10, 27, 37, 0.84));
        border: 1px solid var(--line-strong);
        border-radius: 30px;
        padding: 1.55rem;
        margin-bottom: 1rem;
        box-shadow: 0 26px 70px rgba(0, 0, 0, 0.32);
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 280px;
        height: 280px;
        right: -80px;
        top: -90px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(115, 240, 193, 0.14), transparent 65%);
        filter: blur(2px);
    }

    .eyebrow {
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.16em;
        font-size: 0.72rem;
        color: var(--mint);
        margin-bottom: 0.55rem;
        padding: 0.42rem 0.65rem;
        border: 1px solid rgba(115, 240, 193, 0.22);
        border-radius: 999px;
        background: rgba(115, 240, 193, 0.08);
    }

    .title {
        font-size: 2.45rem;
        line-height: 1.06;
        font-weight: 700;
        margin-bottom: 0.55rem;
        max-width: 780px;
    }

    .hero-copy {
        max-width: 760px;
        color: #cbe6ed;
        line-height: 1.65;
        margin-bottom: 1rem;
    }

    .hero-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.8rem;
        margin-top: 1rem;
    }

    .hero-chip {
        background: rgba(255, 255, 255, 0.045);
        border: 1px solid rgba(173, 244, 255, 0.1);
        border-radius: 18px;
        padding: 0.85rem 0.9rem;
    }

    .hero-chip-label {
        color: var(--text-soft);
        font-size: 0.77rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 0.32rem;
    }

    .hero-chip-value {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-main);
    }

    .support-note {
        background: linear-gradient(90deg, rgba(255, 211, 125, 0.12), rgba(255, 211, 125, 0.04));
        border: 1px solid rgba(255, 211, 125, 0.2);
        border-left: 4px solid var(--gold);
        border-radius: 16px;
        padding: 0.9rem 1rem;
        margin-bottom: 1rem;
        color: #fff3ce;
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.14);
    }

    .section-kicker {
        color: var(--aqua);
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        margin-bottom: 0.3rem;
    }

    .metric-tile {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.055), rgba(255, 255, 255, 0.03));
        border: 1px solid rgba(173, 244, 255, 0.11);
        border-radius: 22px;
        padding: 1rem;
        min-height: 118px;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
    }

    .metric-label {
        color: var(--text-soft);
        font-size: 0.8rem;
        margin-bottom: 0.45rem;
        text-transform: uppercase;
        letter-spacing: 0.11em;
    }

    .metric-value {
        font-size: 1.9rem;
        font-weight: 700;
        color: var(--text-main);
        margin-bottom: 0.3rem;
    }

    .session-caption {
        font-size: 0.82rem;
        color: var(--text-soft);
        margin-top: 0.2rem;
    }

    .reflection-card {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.045), rgba(255, 255, 255, 0.02));
        border: 1px solid rgba(173, 244, 255, 0.08);
        border-radius: 20px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }

    .reflection-meta {
        color: var(--mint);
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 0.35rem;
    }

    .chat-shell {
        background: linear-gradient(180deg, rgba(9, 23, 34, 0.86), rgba(7, 18, 27, 0.78));
        border: 1px solid var(--line);
        border-radius: 28px;
        padding: 1.1rem;
        box-shadow: var(--shadow);
        backdrop-filter: blur(20px);
    }

    .chat-shell-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        margin-bottom: 0.95rem;
        padding-bottom: 0.95rem;
        border-bottom: 1px solid rgba(173, 244, 255, 0.09);
    }

    .chat-shell-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .chat-shell-copy {
        color: var(--text-soft);
        font-size: 0.94rem;
    }

    .status-pill {
        white-space: nowrap;
        padding: 0.5rem 0.8rem;
        border-radius: 999px;
        border: 1px solid rgba(115, 240, 193, 0.2);
        background: rgba(115, 240, 193, 0.08);
        color: var(--mint);
        font-size: 0.8rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .sidebar-card {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.045), rgba(255, 255, 255, 0.02));
        border: 1px solid rgba(173, 244, 255, 0.09);
        border-radius: 18px;
        padding: 0.9rem;
        margin-bottom: 0.85rem;
    }

    .stSidebar > div:first-child {
        background: linear-gradient(180deg, rgba(5, 16, 23, 0.97), rgba(8, 22, 32, 0.95));
        border-right: 1px solid rgba(173, 244, 255, 0.08);
    }

    .stButton > button {
        width: 100%;
        border-radius: 14px;
        border: 1px solid rgba(173, 244, 255, 0.13);
        background: linear-gradient(135deg, rgba(25, 94, 87, 0.95), rgba(27, 116, 145, 0.95));
        color: white;
        font-weight: 600;
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.18);
        transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        border-color: rgba(173, 244, 255, 0.24);
        box-shadow: 0 16px 34px rgba(0, 0, 0, 0.24);
    }

    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(173, 244, 255, 0.12);
        border-radius: 14px;
        color: var(--text-main);
    }

    .stChatInputContainer > div {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(173, 244, 255, 0.12);
        border-radius: 18px;
    }

    .stChatMessage {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(173, 244, 255, 0.08);
        border-radius: 22px !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02);
    }

    .stCaption {
        color: var(--text-soft) !important;
    }

    @media (max-width: 900px) {
        .title {
            font-size: 2rem;
        }
        .hero-grid {
            grid-template-columns: 1fr;
        }
        .chat-shell-header {
            flex-direction: column;
            align-items: flex-start;
        }
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
            <div class='title'>A futuristic check-in space that still feels calm, warm, and human.</div>
            <div class='hero-copy'>Mental Wellness Buddy blends reflective support with a more advanced visual language so it feels like a modern care console, not a generic chatbot. The goal is still the same: help users pause, notice patterns, and feel safe enough to keep talking.</div>
            <div class='hero-grid'>
                <div class='hero-chip'>
                    <div class='hero-chip-label'>Tone</div>
                    <div class='hero-chip-value'>Gentle, steady, non-judgmental</div>
                </div>
                <div class='hero-chip'>
                    <div class='hero-chip-label'>Experience</div>
                    <div class='hero-chip-value'>Glassmorphism with soft neon calm</div>
                </div>
                <div class='hero-chip'>
                    <div class='hero-chip-label'>Purpose</div>
                    <div class='hero-chip-value'>Daily reflection, support, and pattern tracking</div>
                </div>
            </div>
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
    left, center, right = st.columns([0.9, 1.35, 0.9])
    with center:
        render_header()
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-kicker'>Private access</div>", unsafe_allow_html=True)
        if not st.session_state.show_signup:
            st.subheader("Sign in")
            st.caption("Use your account to keep mood history and return to past conversations.")
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
            st.caption("Your chat history stays local in SQLite, and passwords are stored as hashes.")
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

    st.markdown("<div class='section-kicker'>Wellness analytics</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"<div class='metric-tile'><div class='metric-label'>Total check-ins</div><div class='metric-value'>{summary['total_checkins']}</div><div class='session-caption'>Each entry helps reveal emotional patterns over time.</div></div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"<div class='metric-tile'><div class='metric-label'>Dominant emotion</div><div class='metric-value'>{summary['dominant_emotion'].title()}</div><div class='session-caption'>This is the strongest recurring signal in recent logs.</div></div>",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"<div class='metric-tile'><div class='metric-label'>Check-in streak</div><div class='metric-value'>{summary['streak_days']} day(s)</div><div class='session-caption'>Consistency matters more than perfection.</div></div>",
            unsafe_allow_html=True,
        )

    chart_left, chart_right = st.columns(2)
    with chart_left:
        st.markdown("### Emotion distribution")
        fig = px.pie(
            df,
            names="emotion",
            hole=0.6,
            color="emotion",
            color_discrete_sequence=px.colors.sequential.Tealgrn,
        )
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            legend_title_text="Emotion",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#effbfd"),
        )
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
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title=None,
            yaxis_title="Check-ins",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#effbfd"),
        )
        st.plotly_chart(fig, use_container_width=True)

    insight_left, insight_right = st.columns([1.15, 1])
    with insight_left:
        st.markdown("### Recent reflections")
        recent_df = df.head(6).copy()
        for _, row in recent_df.iterrows():
            st.markdown(
                f"<div class='reflection-card'><div class='reflection-meta'>{row['emotion'].title()} | {row['timestamp']}</div><div>{row['message']}</div></div>",
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
        st.markdown(
            "<div class='sidebar-card'><div class='section-kicker'>Navigation</div><div style='color:#cbe6ed;'>Move between live support, quick starts, and saved conversations without losing the calming atmosphere.</div></div>",
            unsafe_allow_html=True,
        )
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

    latest_emotion = "Waiting for check-in"
    if st.session_state.messages:
        assistant_messages = [msg for msg in st.session_state.messages if msg.get("emotion")]
        if assistant_messages:
            latest_emotion = assistant_messages[-1]["emotion"].title()

    st.markdown(
        f"""
        <div class='chat-shell'>
            <div class='chat-shell-header'>
                <div>
                    <div class='section-kicker'>Live support</div>
                    <div class='chat-shell-title'>Buddy conversation channel</div>
                    <div class='chat-shell-copy'>Share what happened, what you are feeling, or what kind of support would help most right now.</div>
                </div>
                <div class='status-pill'>Current signal: {latest_emotion}</div>
            </div>
        """,
        unsafe_allow_html=True,
    )

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
