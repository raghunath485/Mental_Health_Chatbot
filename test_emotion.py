from emotion_detector import detect_emotion

text = "I feel very lonely today"

emotion, confidence = detect_emotion(text)

print("Detected Emotion:", emotion)
print("Confidence:", confidence)