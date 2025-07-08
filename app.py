from flask import Flask, request, jsonify
from flask_cors import CORS
import os 
import openai
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
from openai_integration import get_completion, get_completion_from_messages

openai.api_key  = os.getenv('OPENAI_API_KEY')
system_role_content = os.getenv('SYSTEM_ROLE_CONTENT')

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

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

        completion = get_completion_from_messages(user_messages, temperature=1)
        return jsonify({"response": completion})

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request."}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))