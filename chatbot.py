from textblob import TextBlob
import random

self_care_tips = [
    "Maybe take a few slow deep breaths.",
    "A short walk or stretch might help your body relax.",
    "Listening to calm music can sometimes ease the mind.",
    "You could try a quick two-minute mindfulness pause.",
    "Do not forget to drink some water and take a short rest.",
    "A few minutes of slow breathing can sometimes calm the mind."
]

encouragements = [
    "You are doing better than you think.",
    "Tough moments do not last forever. You can get through this.",
    "Small steps still move you forward.",
    "You are not alone in feeling this way.",
    "Try to be gentle with yourself today."
]


def generate_empathy(emotion):
    empathy_bank = {
        "sadness": [
            "I'm really glad you shared that with me.",
            "It sounds like things have been difficult lately.",
            "Thank you for opening up about how you feel."
        ],
        "anger": [
            "It sounds like something frustrating happened.",
            "I hear the frustration in what you're saying.",
            "That must have been upsetting."
        ],
        "fear": [
            "It sounds like you're feeling worried.",
            "Anxiety can feel overwhelming sometimes.",
            "I hear that you're feeling uneasy."
        ],
        "joy": [
            "That's really nice to hear.",
            "I'm glad something positive happened.",
            "It sounds like you're having a good moment."
        ]
    }
    responses = empathy_bank.get(emotion)
    if responses:
        return random.choice(responses)
    return "Thank you for sharing how you feel."

music_recommendations = {
    "sadness": "🎵 Calm music playlist: https://youtu.be/2OEL4P1Rz04",
    "fear": "🎵 Relaxing ambient sounds: https://youtu.be/lFcSrYw-ARY",
    "anger": "🎵 Soft instrumental music: https://youtu.be/DWcJFNfaw9c",
    "joy": "🎵 Happy uplifting music: https://youtu.be/ZbZSe6N_BXs"
}

motivational_quotes = [
    "💬 Every day may not be good, but there is something good in every day.",
    "💬 Small progress is still progress.",
    "💬 You are stronger than you think.",
    "💬 Difficult moments can help us grow."
]

quick_exercises = [
    "🧘 Try a 2-minute breathing exercise.",
    "🧘 Stretch your shoulders and neck for 30 seconds.",
    "🧘 Take a short walk and focus on your breathing."
]

def generate_recommendations(emotion):
    music = music_recommendations.get(
        emotion,
        "🎵 Listening to calm music might help you relax."
    )
    quote = random.choice(motivational_quotes)
    exercise = random.choice(quick_exercises)
    return f"""
Suggested for you:

{music}

{exercise}

{quote}
"""

def guided_relaxation():
    exercises = [
        "Try this breathing exercise:\n\nInhale for 4 seconds\nHold for 4 seconds\nExhale for 6 seconds\nRepeat 5 times.",
        "Try a grounding exercise:\n\nName 5 things you can see\n4 things you can touch\n3 things you can hear\n2 things you can smell\n1 thing you can taste.",
        "Take a short relaxation pause:\n\nClose your eyes for 10 seconds.\nRelax your shoulders.\nTake slow deep breaths."
    ]
    return random.choice(exercises)

def detect_emergency(text):
    emergency_keywords = [
        "i want to die",
        "kill myself",
        "suicide",
        "end my life",
        "better off dead",
        "i wish i was dead",
        "life is meaningless",
        "no reason to live",
        "i can't go on",
        "i don't want to live anymore"
    ]
    text = text.lower()
    return any(keyword in text for keyword in emergency_keywords)

def detect_mood(user_text):
    text_lower = user_text.lower()
    negative_keywords = [
        "stress","sad","lonely","anxious","panic","depressed",
        "upset","hurt","crying","worried","overthinking",
        "tired","exhausted","burned out","overwhelmed",
        "hopeless","helpless","worthless","frustrated","angry"
    ]
    mild_negative_keywords = [
        "a bit stressed","slightly sad","a bit worried",
        "feeling low","rough day","bad day"
    ]
    if any(word in text_lower for word in negative_keywords):
        return "negative"
    if any(word in text_lower for word in mild_negative_keywords):
        return "mild_negative"
    analysis = TextBlob(user_text)
    score = analysis.sentiment.polarity
    if score > 0.25:
        return "positive"
    elif score < -0.3:
        return "negative"
    elif score < -0.1:
        return "mild_negative"
    else:
        return "neutral"

def craft_reply(mood, emotion):
    tip = random.choice(self_care_tips)
    boost = random.choice(encouragements)
    if emotion == "sadness":
        return (
            "I can sense some sadness in what you shared.\n\n"
            f"Suggestion: {tip}\n"
            f"Reminder: {boost}\n\n"
        )
    if emotion == "anger":
        return (
            "It sounds like you might be feeling frustrated.\n"
            "Taking a few deep breaths or stepping away for a moment could help.\n\n"
        )
    if emotion == "fear":
        return (
            "It seems like you may be feeling anxious.\n\n"
            + guided_relaxation() + "\n\n"
        )
    if emotion == "joy":
        responses = [
            "That is wonderful to hear.",
            "I am glad you are feeling good.",
            "It sounds like you're having a positive moment."
        ]
        return random.choice(responses) + "\n\n"
    if mood == "mild_negative":
        return (
            "It sounds like things are a bit difficult right now.\n\n"
            f"Suggestion: {tip}\n\n"
        )
    if mood == "negative":
        return (
            "I am sorry that you are feeling low right now.\n\n"
            + guided_relaxation() +
            f"\n\nReminder: {boost}\n\n"
        )
    if mood == "positive":
        responses = [
            "That sounds like a positive moment.",
            "I am glad things are going well.",
            "That is nice to hear."
        ]
        return random.choice(responses) + "\n\n"
    return "I am here and listening. You can share more if you would like.\n\n"

def get_bot_response(user_input, emotion, history=None):
    text = user_input.lower().strip()
    if detect_emergency(text):
        return (
            "It seems you may be going through something very difficult.\n\n"
            "You do not have to face this alone.\n"
            "Please consider reaching out to someone you trust or a professional.\n\n"
            "India Mental Health Helplines:\n"
            "Kiran: 9152987821\n"
            "AASRA: +91-22-27546669"
        )
    if len(text.split()) <= 2:
        return (
            "It sounds like you want to talk about how you are feeling.\n"
            "Would you like to share a little more about it?"
        )
    if text.startswith("today") or text.startswith("i feel today"):
        return (
            "Thank you for sharing that.\n"
            "Writing about your thoughts can sometimes help.\n"
            "Would you like to tell me more about your day?"
        )
    mood = detect_mood(user_input)
    empathy = generate_empathy(emotion)
    base_reply = craft_reply(mood, emotion)
    recommendations = generate_recommendations(emotion)
    return f"{empathy}\n\n{base_reply}{recommendations}"