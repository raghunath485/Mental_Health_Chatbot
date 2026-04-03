import time

import pandas as pd
import plotly.express as px
import streamlit as st

try:
    import chatbot as chatbot_module
except Exception as chatbot_import_error:
    chatbot_module = None
    CHATBOT_IMPORT_ERROR = str(chatbot_import_error)
else:
    CHATBOT_IMPORT_ERROR = None

from emotion_detector import detect_emotion
import mood_database as db


def generate_wellness_snapshot(history):
    if chatbot_module and hasattr(chatbot_module, "generate_wellness_snapshot"):
        return chatbot_module.generate_wellness_snapshot(history)
    return "Snapshot is temporarily unavailable because the chatbot module did not fully load."



def get_bot_response(user_input, emotion, history=None):
    if chatbot_module and hasattr(chatbot_module, "get_bot_response"):
        return chatbot_module.get_bot_response(user_input, emotion, history)
    return (
        "I am here with you, but part of the support engine failed to load. "
        "Please refresh the app or redeploy after syncing the latest code and dependencies."
    )


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
        --bg-1: #f5fbfc;
        --bg-2: #edf8f6;
        --bg-3: #f8f4ec;
        --surface: rgba(255, 255, 255, 0.82);
        --surface-strong: rgba(255, 255, 255, 0.94);
        --line: rgba(16, 87, 86, 0.1);
        --line-strong: rgba(16, 87, 86, 0.16);
        --text-main: #153536;
        --text-soft: #55797a;
        --mint: #2f9d8f;
        --aqua: #3478b7;
        --gold: #b98534;
        --shadow: 0 20px 50px rgba(31, 74, 83, 0.1);
    }

    .stApp {
        background:
            radial-gradient(circle at 12% 18%, rgba(73, 191, 164, 0.12), transparent 22%),
            radial-gradient(circle at 88% 14%, rgba(90, 166, 219, 0.12), transparent 20%),
            radial-gradient(circle at 52% 78%, rgba(223, 188, 131, 0.12), transparent 24%),
            linear-gradient(135deg, var(--bg-1) 0%, var(--bg-2) 48%, var(--bg-3) 100%);
        color: var(--text-main);
        font-family: "Aptos", "Segoe UI", sans-serif;
    }

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        background:
            linear-gradient(180deg, rgba(255, 255, 255, 0.25), transparent 30%);
        opacity: 0.7;
    }

    .block-container {
        padding-top: 1.3rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }

    .panel {
        background: linear-gradient(180deg, var(--surface-strong), var(--surface));
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 1.15rem 1.2rem;
        box-shadow: var(--shadow);
        backdrop-filter: blur(14px);
    }

    .hero {
        position: relative;
        overflow: hidden;
        background:
            radial-gradient(circle at top right, rgba(83, 187, 180, 0.18), transparent 30%),
            linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(242, 250, 248, 0.9));
        border: 1px solid var(--line-strong);
        border-radius: 28px;
        padding: 1.7rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow);
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 240px;
        height: 240px;
        right: -70px;
        top: -80px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(73, 191, 164, 0.15), transparent 68%);
        filter: blur(2px);
    }

    .eyebrow {
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        font-size: 0.72rem;
        color: var(--mint);
        margin-bottom: 0.55rem;
        padding: 0.42rem 0.65rem;
        border: 1px solid rgba(47, 157, 143, 0.18);
        border-radius: 999px;
        background: rgba(47, 157, 143, 0.08);
    }

    .title {
        font-family: "Georgia", "Times New Roman", serif;
        font-size: 2.7rem;
        line-height: 1.03;
        font-weight: 700;
        margin-bottom: 0.7rem;
        max-width: 700px;
        color: #183938;
    }

    .hero-copy {
        max-width: 720px;
        color: #4b6f70;
        line-height: 1.7;
        margin-bottom: 1rem;
        font-size: 1rem;
    }

    .hero-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.8rem;
        margin-top: 1rem;
    }

    .hero-chip {
        background: rgba(248, 255, 253, 0.72);
        border: 1px solid rgba(16, 87, 86, 0.08);
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
        background: linear-gradient(90deg, rgba(255, 239, 208, 0.9), rgba(255, 248, 231, 0.75));
        border: 1px solid rgba(185, 133, 52, 0.18);
        border-left: 4px solid var(--gold);
        border-radius: 16px;
        padding: 0.9rem 1rem;
        margin-bottom: 1rem;
        color: #6f531b;
        box-shadow: 0 10px 24px rgba(102, 87, 49, 0.08);
    }

    .section-kicker {
        color: var(--aqua);
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        margin-bottom: 0.3rem;
    }

    .metric-tile {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.95), rgba(249, 253, 252, 0.88));
        border: 1px solid rgba(16, 87, 86, 0.08);
        border-radius: 22px;
        padding: 1rem;
        min-height: 118px;
        box-shadow: 0 10px 25px rgba(25, 76, 77, 0.06);
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
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(250, 253, 252, 0.9));
        border: 1px solid rgba(16, 87, 86, 0.08);
        border-radius: 20px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 8px 22px rgba(25, 76, 77, 0.05);
    }

    .reflection-meta {
        color: var(--mint);
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 0.35rem;
    }

    .chat-shell {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(248, 252, 251, 0.9));
        border: 1px solid var(--line);
        border-radius: 28px;
        padding: 1.1rem;
        box-shadow: var(--shadow);
        backdrop-filter: blur(16px);
    }

    .chat-shell-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        margin-bottom: 0.95rem;
        padding-bottom: 0.95rem;
        border-bottom: 1px solid rgba(16, 87, 86, 0.08);
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
        border: 1px solid rgba(47, 157, 143, 0.16);
        background: rgba(47, 157, 143, 0.08);
        color: var(--mint);
        font-size: 0.8rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .sidebar-card {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.88), rgba(250, 253, 252, 0.82));
        border: 1px solid rgba(16, 87, 86, 0.08);
        border-radius: 18px;
        padding: 0.9rem;
        margin-bottom: 0.85rem;
    }

    .stSidebar > div:first-child {
        background: linear-gradient(180deg, rgba(248, 252, 251, 0.98), rgba(241, 249, 247, 0.96));
        border-right: 1px solid rgba(16, 87, 86, 0.07);
    }

    .stButton > button {
        width: 100%;
        border-radius: 14px;
        border: 1px solid rgba(47, 157, 143, 0.12);
        background: linear-gradient(135deg, #2f9d8f, #4a8bc2);
        color: white;
        font-weight: 600;
        box-shadow: 0 10px 24px rgba(46, 112, 114, 0.14);
        transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        border-color: rgba(173, 244, 255, 0.24);
        box-shadow: 0 16px 34px rgba(0, 0, 0, 0.24);
    }

    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.84);
        border: 1px solid rgba(16, 87, 86, 0.12);
        border-radius: 14px;
        color: var(--text-main);
    }

    .stChatInputContainer > div {
        background: rgba(255, 255, 255, 0.86);
        border: 1px solid rgba(16, 87, 86, 0.12);
        border-radius: 18px;
    }

    .stChatMessage {
        background: rgba(255, 255, 255, 0.86) !important;
        border: 1px solid rgba(16, 87, 86, 0.09);
        border-radius: 22px !important;
        box-shadow: 0 8px 18px rgba(25, 76, 77, 0.05);
    }

    [data-testid="stChatMessageAvatar"] {
        display: none;
    }

    [data-testid="stChatMessageContent"] {
        margin-left: 0 !important;
    }

    .stCaption {
        color: var(--text-soft) !important;
    }

    @media (max-width: 900px) {
        .title {
            font-size: 2.15rem;
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
            <div class='title'>A calm digital space for reflection, support, and emotional clarity.</div>
            <div class='hero-copy'>Mental Wellness Buddy is designed to feel modern without becoming cold. It gives users a gentle place to check in, notice patterns, and keep conversations going over time.</div>
            <div class='hero-grid'>
                <div class='hero-chip'>
                    <div class='hero-chip-label'>Tone</div>
                    <div class='hero-chip-value'>Gentle, steady, non-judgmental</div>
                </div>
                <div class='hero-chip'>
                    <div class='hero-chip-label'>Look</div>
                    <div class='hero-chip-value'>Soft glass, light gradients, subtle depth</div>
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
    if CHATBOT_IMPORT_ERROR:
        st.warning(f"Chat engine loaded in fallback mode: {CHATBOT_IMPORT_ERROR}")



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
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("emotion"):
                st.caption(f"Detected emotion: {msg['emotion']}")

    prompt = st.chat_input("How are you feeling today?")
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
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



