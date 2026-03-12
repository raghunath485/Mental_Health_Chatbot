# 🧠 Mental Wellness Buddy

An AI-powered mental health assistant that helps users track emotions, receive supportive responses, and practice relaxation techniques.

This project combines **emotion detection, AI chatbot responses, mood tracking, and persistent chat history** to create a supportive digital wellness companion.

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
Responds empathetically based on detected emotions and remembers previous context within a session.

### 😌 Emotion Detection
Detects emotions such as:
* Joy
* Sadness
* Anger
* Fear

### 🚨 Crisis Detection
Detects emergency phrases and provides **mental health helpline information** to ensure user safety.

### 🧘 Guided Relaxation
Suggests exercises like:
* Breathing exercises
* Grounding techniques
* Short relaxation pauses

### 📊 Mood Tracking & Analytics
Stores emotional history in an SQLite database and displays trends via an interactive dashboard.

### 📓 Threaded Chat History
Users can start new sessions or revisit past conversations, maintained through a secure database.

### 🧠 AI Recommendation Engine
Based on user emotions the system recommends:
* Calm music playlists
* Motivational quotes
* Quick relaxation exercises

### 🔐 Multi-Layer Login System
Supports secure manual authentication (Password Hashing) and **Google OAuth 2.0** integration.

---

# 🏗️ Architecture

User → Streamlit Interface → Python Backend → Emotion Detection → Chatbot Engine → SQLite Database

**Workflow:**
1. User sends message through the Glassmorphism UI.
2. Emotion detection model analyzes text for sentiment.
3. Chatbot generates a contextual, empathetic response.
4. Mood data and chat messages are stored in the relational database.
5. Analytics dashboard visualizes emotional trends from history.

---

# 🛠️ Tech Stack

### Backend
* Python
* Streamlit Session State
* Werkzeug (Security)

### AI / NLP
* TextBlob
* HuggingFace Transformers (Emotion Detection)

### Frontend
* Streamlit (Custom CSS & Glassmorphism)
* Plotly / Pandas (Analytics)

### Database
* SQLite3

### Authentication
* Google Cloud Console (OAuth 2.0)
* Flask-Bcrypt Style Hashing

---

# 📂 Project Structure

```text
mental_health_chatbot
│
├── streamlit_app.py        # Main App Entry Point
├── chatbot.py              # Empathetic Response Logic
├── emotion_detector.py     # NLP Sentiment Analysis
├── mood_database.py        # SQLite Management & Queries
│
├── database/               # Local DB Storage
├── static/                 # UI Assets & Icons
│
├── requirements.txt        # Project Dependencies
└── README.md               # Documentation