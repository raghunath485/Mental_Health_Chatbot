# Mental Wellness Buddy

Mental Wellness Buddy is now closer to a real-world wellness product than a classroom chatbot demo. It offers account-based check-ins, persistent conversation history, emotion tracking, a safety-aware response layer, and a dashboard that helps users notice patterns in their emotional health.

## What changed

This version focuses on product credibility:

- Safer crisis messaging with stronger high-risk language detection and multi-region crisis contacts.
- Persistent conversation history that lets users reopen past sessions.
- Better dashboard metrics including dominant emotion, recent streak, and 7-day activity trends.
- Resilient emotion detection with a heuristic fallback if the transformer model is unavailable.
- More honest product messaging: the UI and README now match the features that are actually implemented.

## Core features

- Account login and registration with password hashing.
- Emotion-aware chat responses for sadness, anger, fear, joy, and neutral states.
- SQLite-backed mood logging and chat session history.
- Wellness dashboard with mood distribution and weekly check-in summaries.
- Guided reflection prompts, breathing ideas, and grounding exercises.
- Local-first storage for simple development and demos.

## Project structure

```text
mental_health_chatbot/
|-- streamlit_app.py      # Main Streamlit product UI
|-- chatbot.py            # Safety-aware support and response generation
|-- emotion_detector.py   # Transformer emotion classifier with fallback logic
|-- mood_database.py      # SQLite schema, persistence, and analytics queries
|-- database/             # SQLite database location
|-- static/               # Assets
|-- templates/            # Legacy HTML templates
|-- requirements.txt
`-- README.md
```

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Launch the app:

```bash
streamlit run streamlit_app.py
```

## Notes for production hardening

If you want to take this further after the current upgrade, the next practical steps would be:

- Move secrets and config into environment variables.
- Add automated tests around database queries and chat safety behavior.
- Add rate limiting, audit logs, and consent/privacy messaging for real users.
- Replace SQLite with Postgres for multi-user deployment.
- Add proper human escalation workflows instead of only hotline messaging.

## Safety note

This project is a supportive reflection tool, not a replacement for licensed mental health care or emergency services.
