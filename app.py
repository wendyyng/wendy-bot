from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import logging
import json
import unicodedata
import os 
import openai
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
from openai_integration import get_completion, get_completion_from_messages

system_role_content = os.getenv('SYSTEM_ROLE_CONTENT')

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

# Structured JSON logger for the app
logger = logging.getLogger("wendy_bot")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(message)s'))
if not logger.handlers:
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

def strip_non_ascii(text):
    # Normalize text to remove problematic characters like \xa0
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_messages = data.get('messages', [])

        # Inject system prompt if not already included
        if not any(m.get("role") == "system" for m in user_messages):
            user_messages.insert(0, {
                "role": "system",
                "content": system_role_content
            })
        
        # Get the latest user message (not system or assistant)
        last_user_message = next(
            (m['content'] for m in reversed(user_messages) if m['role'] == 'user'),
            None
        )

        if last_user_message:
            user_ip = request.remote_addr or 'unknown'
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Previously this sent an email; replace with structured JSON logging
            logger.info(json.dumps({
                "event": "chat_request",
                "timestamp": timestamp,
                "ip": user_ip,
                "message": last_user_message
            }, ensure_ascii=False))

        try:
            completion = get_completion_from_messages(user_messages, temperature=1)
            return jsonify({"response": completion}), 200
        except Exception as oe:
            # Differentiate OpenAI errors vs other errors. If the OpenAI client
            # raises a specific exception type in your environment you can
            # import and catch it (e.g., openai.error.OpenAIError). Here we
            # inspect the exception to provide a structured response.
            err_msg = str(oe)
            logger.error(json.dumps({
                "event": "openai_error",
                "error": err_msg
            }, ensure_ascii=False))
            return jsonify({"error": "openai_error", "message": err_msg}), 502

    except Exception as e:
        # System-level errors (bad request payloads, coding errors, etc.)
        err_msg = str(e)
        logger.error(json.dumps({
            "event": "system_error",
            "error": err_msg
        }, ensure_ascii=False))
        return jsonify({"error": "system_error", "message": err_msg}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))