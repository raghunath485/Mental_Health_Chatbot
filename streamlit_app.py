import streamlit as st
import pandas as pd
import plotly.express as px
import time
from chatbot import get_bot_response
from emotion_detector import detect_emotion
import mood_database as db


st.set_page_config(
    page_title="Mental Wellness Buddy",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>

.stApp{
background: linear-gradient(135deg,#0f172a,#1e293b);
color:white;
font-family: "Segoe UI", sans-serif;
}


.block-container{
padding-top:2rem;
}


.chat-container{
background: rgba(255,255,255,0.05);
border-radius:20px;
padding:20px;
backdrop-filter: blur(12px);
border:1px solid rgba(255,255,255,0.08);
}


.stChatMessage{
border-radius:18px !important;
padding:14px !important;
border:1px solid rgba(255,255,255,0.05);
background: rgba(255,255,255,0.04) !important;
}


.metric-card{
background: rgba(255,255,255,0.05);
padding:15px;
border-radius:15px;
text-align:center;
border:1px solid rgba(255,255,255,0.08);
}


.stButton > button{
background: linear-gradient(135deg,#6366f1,#8b5cf6);
color:white;
border:none;
border-radius:12px;
font-weight:600;
padding:10px 16px;
}


.stButton > button:hover{
background: linear-gradient(135deg,#4f46e5,#7c3aed);
}


.typing{
font-size:14px;
opacity:0.7;
animation: blink 1s infinite;
}

@keyframes blink{
0%{opacity:0.2}
50%{opacity:1}
100%{opacity:0.2}
}

</style>
""", unsafe_allow_html=True)


db.init_user_table()


if "logged_in" not in st.session_state:
    st.session_state.logged_in=False

if "messages" not in st.session_state:
    st.session_state.messages=[]

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id=None

if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard=False

if "show_signup" not in st.session_state:
    st.session_state.show_signup=False



def login_page():

    col1,col2,col3=st.columns([1,2,1])

    with col2:

        st.markdown("<div class='chat-container'>",unsafe_allow_html=True)

        st.title("🧠 Mental Wellness Buddy")

        if not st.session_state.show_signup:

            st.subheader("Login")

            with st.form("login_form"):

                u=st.text_input("Username")
                p=st.text_input("Password",type="password")

                if st.form_submit_button("Login",use_container_width=True):

                    uid=db.verify_user(u,p)

                    if uid:
                        st.session_state.logged_in=True
                        st.session_state.user_id=uid
                        st.rerun()

                    else:
                        st.error("Invalid username or password")

            if st.button("Create Account",use_container_width=True):
                st.session_state.show_signup=True
                st.rerun()

        else:

            st.subheader("Create Account")

            with st.form("signup"):

                u=st.text_input("New Username")
                p1=st.text_input("Password",type="password")
                p2=st.text_input("Confirm Password",type="password")

                if st.form_submit_button("Register",use_container_width=True):

                    if p1!=p2:
                        st.error("Passwords do not match")

                    else:

                        ok,uid,err=db.create_account(u,p1)

                        if ok:
                            st.session_state.logged_in=True
                            st.session_state.user_id=uid
                            st.session_state.show_signup=False
                            st.rerun()

                        else:
                            st.error(err)

            if st.button("Back to Login",use_container_width=True):
                st.session_state.show_signup=False
                st.rerun()

        st.markdown("</div>",unsafe_allow_html=True)



def dashboard():

    st.title("📊 Mood Intelligence Dashboard")

    if st.button("⬅ Back to Chat"):
        st.session_state.show_dashboard=False
        st.rerun()

    mood=db.get_mood_history(st.session_state.user_id)

    if not mood:
        st.info("Start chatting to generate insights")
        return

    df=pd.DataFrame(mood)

    col1,col2=st.columns(2)

    with col1:

        st.markdown("### Emotion Distribution")

        fig=px.pie(
            df,
            names="emotion",
            hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )

        st.plotly_chart(fig,use_container_width=True)

    with col2:

        st.markdown("### Emotion Timeline")

        fig=px.line(
            df,
            x="timestamp",
            y="emotion",
            markers=True
        )

        st.plotly_chart(fig,use_container_width=True)



def main_chat():

    if st.session_state.show_dashboard:
        dashboard()
        return


    with st.sidebar:

        st.title("Wellness Insights")

        if st.button("Open Dashboard"):
            st.session_state.show_dashboard=True
            st.rerun()

        st.divider()

        mood=db.get_mood_history(st.session_state.user_id)

        if mood:

            df=pd.DataFrame(mood)

            latest=df["emotion"].iloc[0]

            st.markdown(
            f"<div class='metric-card'>Latest Emotion<br><b>{latest.upper()}</b></div>",
            unsafe_allow_html=True)

        st.divider()

        if st.button("New Chat"):
            st.session_state.messages=[]
            st.session_state.current_session_id=None
            st.rerun()

        st.divider()

        if st.button("Logout"):
            st.session_state.logged_in=False
            st.rerun()


    st.title("💬 Buddy Chat")

    st.markdown("<div class='chat-container'>",unsafe_allow_html=True)

    for msg in st.session_state.messages:

        avatar="🙋" if msg["role"]=="user" else "🧘"

        with st.chat_message(msg["role"],avatar=avatar):

            st.markdown(msg["content"])

    st.markdown("</div>",unsafe_allow_html=True)


    if prompt:=st.chat_input("How are you feeling today?"):

        if st.session_state.current_session_id is None:

            st.session_state.current_session_id=db.create_new_session(
                st.session_state.user_id,
                prompt
            )

        db.save_chat_message(st.session_state.current_session_id,"user",prompt)

        st.session_state.messages.append({
            "role":"user",
            "content":prompt
        })

        with st.chat_message("user",avatar="🙋"):
            st.markdown(prompt)


        with st.chat_message("assistant",avatar="🧘"):
            typing=st.empty()
            typing.markdown("<div class='typing'>Buddy is thinking...</div>",unsafe_allow_html=True)

            time.sleep(1)

            emotion,_=detect_emotion(prompt)

            db.save_mood(st.session_state.user_id,prompt,emotion)

            reply=get_bot_response(prompt,emotion,st.session_state.messages)

            typing.empty()

            st.markdown(reply)


        db.save_chat_message(
            st.session_state.current_session_id,
            "assistant",
            reply
        )

        st.session_state.messages.append({
            "role":"assistant",
            "content":reply
        })


if not st.session_state.logged_in:
    login_page()
else:
    main_chat()
