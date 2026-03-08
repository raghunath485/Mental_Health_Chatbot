# 🧠 Mental Wellness Buddy

An AI-powered mental health assistant that helps users track emotions, receive supportive responses, and practice relaxation techniques.

This project combines **emotion detection, AI chatbot responses, mood tracking, and voice interaction** to create a supportive digital wellness companion.

---

# 📌 Problem Statement

Mental health support is often difficult to access immediately. Many people experience stress, anxiety, or emotional challenges but may not always have someone available to talk to.

Mental Wellness Buddy provides:

* Instant emotional support
* Mood tracking
* Relaxation guidance
* AI-based recommendations

The goal is to help users **reflect on their emotions and manage stress in a healthy way**.

---

# 🚀 Features

### 🤖 AI Chatbot

Responds empathetically based on detected emotions.

### 😌 Emotion Detection

Detects emotions such as:

* Joy
* Sadness
* Anger
* Fear

### 🚨 Crisis Detection

Detects emergency phrases like:

* "I want to die"
* "Life is meaningless"

Provides **mental health helpline information**.

### 🧘 Guided Relaxation

Suggests exercises like:

* Breathing exercises
* Grounding techniques
* Short relaxation pauses

### 📊 Mood Tracking

Stores emotional history in a database.

### 📓 Journaling

Users can write daily thoughts and reflections.

### 🎤 Voice Interaction

Users can speak instead of typing.

### 🧠 AI Recommendation Engine

Based on user emotions the system recommends:

* Calm music playlists
* Motivational quotes
* Quick relaxation exercises

### 📈 Mood Dashboard

Displays mood history and emotional trends.

### 🔐 User Login System

Supports user authentication and personal mood history.

---

# 🏗️ Architecture

User → Web Interface → Flask Server → Emotion Detection → Chatbot Engine → Database

Workflow:

1. User sends message
2. Emotion detection model analyzes text
3. Chatbot generates response
4. Mood data stored in database
5. AI recommendation engine suggests activities

---

# 🛠️ Tech Stack

### Backend

* Python
* Flask
* Flask-Login

### AI / NLP

* TextBlob
* Emotion detection model

### Frontend

* HTML
* CSS
* JavaScript
* Bootstrap

### Database

* SQLite

### Other Tools

* SpeechRecognition (voice input)
* Chart.js (dashboard analytics)

---

# 📂 Project Structure

```
mental_health_chatbot
│
├── app.py
├── chatbot.py
├── emotion_detector.py
├── mood_database.py
│
├── templates
│   ├── index.html
│   ├── dashboard.html
│   ├── login.html
│   └── register.html
│
├── static
│   └── coach.png
│
├── requirements.txt
└── README.md
```

---

# 🖥️ Screenshots

### Chat Interface

(Add screenshot here)

### Mood Dashboard

(Add screenshot here)

### Emergency Detection

(Add screenshot here)

---

# ⚙️ Installation

Clone repository:

```
git clone https://github.com/yourusername/mental-wellness-buddy.git
```

Move into folder:

```
cd mental-wellness-buddy
```

Create virtual environment:

```
python -m venv venv
```

Activate environment:

```
source venv/bin/activate
```

Install dependencies:

```
pip install -r requirements.txt
```

Run the server:

```
python app.py
```

Open browser:

```
http://127.0.0.1:5000
```

---

# 🌐 Deployment

The project can be deployed on:

* Render
* Railway
* AWS
* Docker

Example deployment:

```
https://mental-wellness-buddy.onrender.com
```

---

# 🔮 Future Improvements

* Mobile application
* Personalized therapy plans
* AI conversation memory
* Real-time stress detection
* Integration with wearable devices

---

# 👨‍💻 Author

**Raghunath Panda**

KIIT University
Artificial Intelligence Project

---

# ⭐ If you like this project

Give it a ⭐ on GitHub!

# 🌟 About
Mental Wellness Buddy is an AI-powered web application that provides emotional support through a chatbot. It detects user emotions using NLP, generates supportive responses, and tracks mood patterns in a dashboard. The platform includes user authentication, mood analytics, and crisis detection to promote emotional awareness and well-being.
