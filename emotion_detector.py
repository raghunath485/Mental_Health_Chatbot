from transformers import pipeline


emotion_pipeline = None




def load_model():
    global emotion_pipeline

    if emotion_pipeline is None:
        emotion_pipeline = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            device=-1
        )

    return emotion_pipeline




def normalize_emotion(emotion):

    mapping = {
        "love": "joy",
        "surprise": "joy"
    }

    return mapping.get(emotion, emotion)




def detect_emotion(text):

    try:

        model = load_model()

        result = model(text)

        emotion = result[0]["label"]
        score = result[0]["score"]

        emotion = normalize_emotion(emotion)

        return emotion, score

    except Exception:


        return "neutral", 0.0