from textblob import TextBlob
import random

self_care_tips = [
    "Maybe take a few slow deep breaths.",
    "A short walk or stretch might help your body relax.",
    "Listening to calm music can sometimes ease the mind.",
    "You could try a quick two-minute mindfulness pause.",
    "Do not forget to drink some water and take a short rest."
]

encouragements = [
    "You are doing better than you think.",
    "Tough moments do not last forever. You can get through this.",
    "Small steps still move you forward.",
    "You are not alone in feeling this way.",
    "Try to be gentle with yourself today."
]

def detect_mood(user_text):
    text_lower = user_text.lower()

    crisis_keywords = [
        "suicide",
        "kill myself",
        "end my life",
        "want to die",
        "i want to die",
        "wish i was dead",
        "better off dead",
        "end everything",
        "no reason to live",
        "life is not worth living"
    ]

    negative_keywords = [
        "stress", "stressed", "stressful",
        "sad", "very sad", "feeling sad",
        "lonely", "alone", "isolated",
        "anxious", "anxiety", "panic",
        "depressed", "depression",
        "upset", "hurt", "crying",
        "worried", "worry", "overthinking",
        "tired", "exhausted", "burned out",
        "overwhelmed", "pressure", "under pressure",
        "scolded", "failed", "failure",
        "hopeless", "helpless", "worthless",
        "frustrated", "angry", "irritated",
        "not okay", "not feeling good",
        "mentally tired", "emotionally tired"
    ]

    mild_negative_keywords = [
        "little stressed",
        "a bit stressed",
        "slightly sad",
        "kind of tired",
        "a bit worried",
        "feeling low",
        "not great",
        "rough day",
        "bad day"
    ]

    if any(phrase in text_lower for phrase in crisis_keywords):
        return "crisis"

    if any(phrase in text_lower for phrase in negative_keywords):
        return "negative"

    if any(phrase in text_lower for phrase in mild_negative_keywords):
        return "mild_negative"

    analysis = TextBlob(user_text)
    score = analysis.sentiment.polarity

    if score > 0.2:
        return "positive"
    elif score < -0.25:
        return "negative"
    elif score < -0.05:
        return "mild_negative"
    else:
        return "neutral"

def craft_reply(mood):
    if mood == "positive":
        responses = [
            "That is good to hear. I am glad things are going well.",
            "It sounds like you are having a positive moment. Keep it up.",
            "I am happy to hear that."
        ]
        return random.choice(responses)

    elif mood == "mild_negative":
        responses = [
            "It sounds like things are a bit difficult right now.",
            "I can sense some stress. Taking a short break might help.",
            "It seems something is bothering you. I am here to listen."
        ]
        return random.choice(responses)

    elif mood == "negative":
        tip = random.choice(self_care_tips)
        boost = random.choice(encouragements)
        return (
            "I am sorry that you are feeling low right now.\n"
            f"Suggestion: {tip}\n"
            f"Reminder: {boost}"
        )

    elif mood == "neutral":
        responses = [
            "I am here and listening. You can share more if you would like.",
            "Would you like to tell me a bit more about what is on your mind?",
            "I am right here with you."
        ]
        return random.choice(responses)

    elif mood == "crisis":
        return (
            "I am concerned about what you shared.\n"
            "Please consider reaching out to someone you trust immediately.\n"
            "Kiran Mental Health Helpline (India): 9152987821"
        )

def get_bot_response(user_input):
    mood = detect_mood(user_input)
    return craft_reply(mood)