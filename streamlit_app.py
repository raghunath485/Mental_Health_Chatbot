import streamlit as st
from chatbot import get_bot_response
from emotion_detector import detect_emotion
from mood_database import save_mood, get_mood_history



st.set_page_config(
    page_title="Mental Wellness Buddy",
    page_icon="🧠",
    layout="centered"
)



st.markdown("""
<style>

.stApp {
background: linear-gradient(135deg,#6e8efb,#a777e3);
}

.header {
text-align:center;
color:white;
font-size:32px;
font-weight:bold;
margin-bottom:5px;
}

.subtext {
text-align:center;
color:white;
opacity:0.9;
margin-bottom:30px;
}

.chat-box {
background: rgba(255,255,255,0.2);
backdrop-filter: blur(15px);
padding:20px;
border-radius:20px;
box-shadow: 0 20px 50px rgba(0,0,0,0.25);
}

.user {
background:#5865f2;
color:white;
padding:12px 16px;
border-radius:18px;
margin:8px 0;
margin-left:auto;
width:fit-content;
max-width:75%;
}

.bot {
background:#eef1ff;
color:#222;
padding:12px 16px;
border-radius:18px;
margin:8px 0;
width:fit-content;
max-width:75%;
}

</style>
""", unsafe_allow_html=True)



st.markdown('<div class="header">🧠 Mental Wellness Buddy</div>', unsafe_allow_html=True)
st.markdown('<div class="subtext">Your supportive AI companion. Talk freely — I’m here to listen.</div>', unsafe_allow_html=True)



if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_id" not in st.session_state:
    st.session_state.user_id = 1



st.markdown('<div class="chat-box">', unsafe_allow_html=True)

for msg in st.session_state.messages:

    if msg["role"] == "user":
        st.markdown(
            f'<div class="user">{msg["content"]}</div>',
            unsafe_allow_html=True
        )

    else:
        st.markdown(
            f'<div class="bot">{msg["content"]}</div>',
            unsafe_allow_html=True
        )

st.markdown('</div>', unsafe_allow_html=True)



prompt = st.chat_input("Type how you feel...")

if prompt:

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    emotion, confidence = detect_emotion(prompt)

    save_mood(st.session_state.user_id, prompt, emotion)

    response = get_bot_response(prompt, emotion)

    bot_reply = f"😊 **Emotion detected:** {emotion}\n\n{response}"

    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply
    })

    st.rerun()



st.sidebar.title("📊 Mood Dashboard")

if st.sidebar.button("Show Mood History"):

    history = get_mood_history(st.session_state.user_id)

    if history:

        for row in history[-10:]:

            st.sidebar.write(
                f"{row['emotion']} — {row['message'][:40]}"
            )

    else:
        st.sidebar.write("No mood history yet.")



if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()



if st.session_state.messages:

    last_message = st.session_state.messages[-1]["content"].lower()

    crisis_words = [
        "suicide",
        "kill myself",
        "end my life"
    ]

    if any(word in last_message for word in crisis_words):

        st.error("""
🚨 If you are feeling overwhelmed, please seek help.

India Mental Health Helpline: **9152987821**

Emergency: **112**

You are not alone. Support is available.
""")