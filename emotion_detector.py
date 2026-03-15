from transformers import pipeline
import streamlit as st


@st.cache_resource
def load_emotion_model():
    """
    Load the emotion detection model once and cache it.
    This prevents the model from reloading on every Streamlit rerun.
    """
    emotion_pipeline = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base"
    )
    return emotion_pipeline


# Load the cached model
emotion_pipeline = load_emotion_model()


def detect_emotion(text):
    """
    Detect emotion from user input text.
    Returns emotion label and confidence score.
    """

    if not text or text.strip() == "":
        return "neutral", 0.0

    result = emotion_pipeline(text)

    emotion = result[0]["label"]
    score = result[0]["score"]

    return emotion, score
