from flask import Flask, render_template, request, jsonify
from chatbot import get_bot_response

app = Flask(__name__)

@app.route("/")
def load_homepage():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def process_chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please type a message so I can help you."})

    bot_response = get_bot_response(user_message)
    return jsonify({"reply": bot_response})

if __name__ == "__main__":
    print("Starting Mental Wellness Buddy server...")
    app.run(debug=True)