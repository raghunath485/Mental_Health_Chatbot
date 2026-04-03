from functools import lru_cache

import streamlit as st
from transformers import pipeline


EMOTION_KEYWORDS = {
    "joy": ["happy", "relieved", "grateful", "excited", "hopeful", "good"],
    "sadness": ["sad", "empty", "lonely", "hurt", "crying", "down"],
    "anger": ["angry", "furious", "annoyed", "mad", "frustrated"],
    "fear": ["anxious", "afraid", "worried", "panic", "scared", "nervous"],
}


@st.cache_resource(show_spinner=False)
def load_emotion_model():
    try:
        return pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
        )
    except Exception:
        return None


emotion_pipeline = load_emotion_model()


def heuristic_emotion(text):
    normalized = (text or "").lower()
    for emotion, keywords in EMOTION_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return emotion, 0.55
    return "neutral", 0.4


def detect_emotion(text):
    if not text or text.strip() == "":
        return "neutral", 0.0

    if emotion_pipeline is None:
        return heuristic_emotion(text)

    try:
        result = emotion_pipeline(text)
        emotion = result[0]["label"]
        score = float(result[0]["score"])
        return emotion, score
    except Exception:
        return heuristic_emotion(text)
