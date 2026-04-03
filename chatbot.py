import random
from collections import Counter

from textblob import TextBlob


SELF_CARE_TIPS = [
    "Try one minute of slow breathing: inhale for 4 and exhale for 6.",
    "Drink a glass of water and release some tension in your shoulders.",
    "Step away from the screen for a short walk or stretch.",
    "Write down one feeling and one thing you need right now.",
    "If it feels safe, reach out to one person you trust today.",
]

ENCOURAGEMENTS = [
    "You do not have to solve everything at once.",
    "Small steps still count as real progress.",
    "What you are feeling matters.",
    "You deserve support and care.",
    "Taking a pause is a healthy choice, not a failure.",
]

EMPATHY_BANK = {
    "sadness": [
        "I am glad you told me this.",
        "That sounds heavy, and it makes sense that you are feeling low.",
        "Thank you for sharing something vulnerable.",
    ],
    "anger": [
        "That sounds frustrating.",
        "I can hear the tension in what you shared.",
        "It makes sense that this situation would feel upsetting.",
    ],
    "fear": [
        "That sounds really stressful.",
        "Feeling anxious can make everything feel louder and harder.",
        "I hear that you are carrying a lot of worry right now.",
    ],
    "joy": [
        "I am happy to hear there is something positive in your day.",
        "That sounds like a meaningful bright spot.",
        "It is good to pause and notice a moment like that.",
    ],
    "neutral": [
        "Thank you for checking in.",
        "I am here with you.",
        "I am listening.",
    ],
}

MUSIC_RECOMMENDATIONS = {
    "sadness": "Music idea: a calm instrumental playlist or soft piano mix.",
    "fear": "Sound idea: ambient rain, nature sounds, or a grounding playlist.",
    "anger": "Music idea: low-tempo instrumental music to help your body settle.",
    "joy": "Music idea: keep the momentum with an uplifting playlist.",
    "neutral": "Music idea: choose something steady and gentle for a reset.",
}

QUICK_EXERCISES = [
    "Exercise: unclench your jaw, drop your shoulders, and take 5 slow breaths.",
    "Exercise: try the 5-4-3-2-1 grounding method to reconnect with the present.",
    "Exercise: stand up and stretch your neck, chest, and hands for 60 seconds.",
]

MOTIVATIONAL_QUOTES = [
    "Reflection: progress can be quiet and still be real.",
    "Reflection: rest is part of recovery, not the opposite of it.",
    "Reflection: you are allowed to ask for help before things get worse.",
    "Reflection: one difficult day does not define your whole story.",
]

CRISIS_CONTACTS = [
    "If you might act on these thoughts now, call emergency services right away.",
    "United States and Canada: call or text 988.",
    "India: Tele-MANAS 14416 or 1-800-891-4416, AASRA +91-22-2754-6669.",
    "If you are elsewhere, contact your local emergency number or nearest crisis hotline now.",
]

HIGH_RISK_KEYWORDS = [
    "kill myself",
    "suicide",
    "end my life",
    "want to die",
    "wish i was dead",
    "better off dead",
    "no reason to live",
    "i do not want to live anymore",
    "i dont want to live anymore",
    "i can't go on",
    "i cant go on",
]

MODERATE_RISK_KEYWORDS = [
    "self harm",
    "hurt myself",
    "harm myself",
    "cut myself",
    "overdose",
    "i want to disappear",
    "life is meaningless",
    "nothing matters",
]


def normalize_text(text):
    return " ".join((text or "").lower().strip().split())


def detect_risk_level(text):
    normalized = normalize_text(text)
    if any(keyword in normalized for keyword in HIGH_RISK_KEYWORDS):
        return "high"
    if any(keyword in normalized for keyword in MODERATE_RISK_KEYWORDS):
        return "moderate"
    return "low"


def detect_mood(user_text):
    text_lower = normalize_text(user_text)
    negative_keywords = [
        "stress",
        "sad",
        "lonely",
        "anxious",
        "panic",
        "depressed",
        "upset",
        "hurt",
        "crying",
        "worried",
        "overthinking",
        "tired",
        "exhausted",
        "burned out",
        "overwhelmed",
        "hopeless",
        "helpless",
        "worthless",
        "frustrated",
        "angry",
    ]
    mild_negative_keywords = [
        "a bit stressed",
        "slightly sad",
        "a bit worried",
        "feeling low",
        "rough day",
        "bad day",
    ]
    if any(word in text_lower for word in negative_keywords):
        return "negative"
    if any(word in text_lower for word in mild_negative_keywords):
        return "mild_negative"

    score = TextBlob(user_text).sentiment.polarity
    if score > 0.25:
        return "positive"
    if score < -0.3:
        return "negative"
    if score < -0.1:
        return "mild_negative"
    return "neutral"


def generate_empathy(emotion):
    responses = EMPATHY_BANK.get(emotion, EMPATHY_BANK["neutral"])
    return random.choice(responses)


def guided_relaxation():
    exercises = [
        "Try this breathing pattern: inhale for 4 seconds, hold for 4, exhale for 6. Repeat 5 times.",
        "Try grounding: name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste.",
        "Pause for 30 seconds: relax your shoulders, unclench your jaw, and slow your breathing.",
    ]
    return random.choice(exercises)


def generate_recommendations(emotion):
    music = MUSIC_RECOMMENDATIONS.get(emotion, MUSIC_RECOMMENDATIONS["neutral"])
    quote = random.choice(MOTIVATIONAL_QUOTES)
    exercise = random.choice(QUICK_EXERCISES)
    return f"{music}\n{exercise}\n{quote}"


def build_history_summary(history):
    if not history:
        return ""

    user_messages = [msg["content"] for msg in history if msg.get("role") == "user"][-3:]
    if len(user_messages) < 2:
        return ""

    combined = " ".join(user_messages)
    mood = detect_mood(combined)
    if mood in {"negative", "mild_negative"}:
        return "I also notice this has been weighing on you across more than one message."
    if mood == "positive":
        return "There is also a positive thread in what you have been sharing lately."
    return ""


def craft_reply(mood, emotion, history=None):
    tip = random.choice(SELF_CARE_TIPS)
    boost = random.choice(ENCOURAGEMENTS)
    history_note = build_history_summary(history)

    if emotion == "sadness":
        body = (
            f"Support step: {tip}\n"
            f"Reminder: {boost}\n"
            f"Reset idea: {guided_relaxation()}"
        )
    elif emotion == "anger":
        body = (
            "Support step: create a little space before reacting if you can.\n"
            f"Body reset: {guided_relaxation()}\n"
            f"Reminder: {boost}"
        )
    elif emotion == "fear":
        body = (
            f"Grounding idea: {guided_relaxation()}\n"
            f"Support step: {tip}\n"
            f"Reminder: {boost}"
        )
    elif emotion == "joy":
        body = (
            "It can help to name what is going well so you can come back to it later.\n"
            "Try writing down one thing that supported this better moment."
        )
    elif mood == "mild_negative":
        body = f"Support step: {tip}\nReminder: {boost}"
    elif mood == "negative":
        body = (
            f"Grounding idea: {guided_relaxation()}\n"
            f"Support step: {tip}\n"
            f"Reminder: {boost}"
        )
    elif mood == "positive":
        body = "That sounds like an important bright spot. Holding onto small wins can really help."
    else:
        body = "You can share as much or as little as you want, and we can take it one step at a time."

    if history_note:
        body = f"{history_note}\n{body}"

    return body


def build_check_in_prompt():
    prompts = [
        "If you want, tell me what happened today that seems to be affecting you most.",
        "If it helps, describe what your body feels like right now: tense, tired, restless, heavy, or calm.",
        "If you are unsure where to start, you can name one emotion and one need.",
    ]
    return random.choice(prompts)


def build_crisis_response(risk_level):
    intro = (
        "I am really glad you said this out loud. Your safety matters more than continuing this chat."
        if risk_level == "high"
        else "What you shared sounds serious, and I want to respond carefully."
    )
    contacts = "\n".join(f"- {line}" for line in CRISIS_CONTACTS)
    return (
        f"{intro}\n\n"
        "Please contact immediate human support right now:\n"
        f"{contacts}\n\n"
        "If you can, move closer to another person and tell them you need support now."
    )


def generate_wellness_snapshot(history):
    emotions = [item.get("emotion") for item in history if item.get("emotion")]
    if not emotions:
        return "Not enough check-ins yet to spot a pattern."

    top_emotion, count = Counter(emotions).most_common(1)[0]
    total = len(emotions)
    return f"Recent trend: {top_emotion} appeared in {count} of your last {total} logged check-ins."


def get_bot_response(user_input, emotion, history=None):
    text = normalize_text(user_input)
    risk_level = detect_risk_level(text)
    if risk_level in {"high", "moderate"}:
        return build_crisis_response(risk_level)

    if len(text.split()) <= 2:
        return f"I am here with you.\n\n{build_check_in_prompt()}"

    if text.startswith("today") or text.startswith("i feel today"):
        return (
            "Thank you for checking in.\n\n"
            "Writing about your day can make the feeling easier to understand.\n"
            f"{build_check_in_prompt()}"
        )

    mood = detect_mood(user_input)
    empathy = generate_empathy(emotion)
    base_reply = craft_reply(mood, emotion, history=history)
    recommendations = generate_recommendations(emotion)
    return f"{empathy}\n\n{base_reply}\n\nSuggested next steps:\n{recommendations}"

