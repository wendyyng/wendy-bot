from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
from openai_integration import get_completion, get_completion_from_messages

system_role_content = os.getenv('SYSTEM_ROLE_CONTENT')

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

@app.route('/api/chat', methods=['POST'])
def chat():
    
    try:
        data = request.json
        # Accept either a single `message` (string) or a `messages` list of dicts
        temperature = data.get('temperature', 1)
        raw_messages = data.get('messages')
        if raw_messages and isinstance(raw_messages, list):
            messages = raw_messages.copy()
        else:
            message = data.get('message', '')
            messages = [{'role': 'user', 'content': message}]

        # Inject system role from env if provided and not present
        if system_role_content:
            has_system = any((m.get('role') or '').lower() == 'system' for m in messages)
            if not has_system:
                messages.insert(0, {'role': 'system', 'content': system_role_content})

        completion = get_completion_from_messages(messages, temperature=temperature)
        
        return jsonify({"response": completion})

    except Exception as e:
        # Log the exception to diagnose the issue
        print(f"Error processing request: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request."}), 500

if __name__ == '__main__':
    app.run(debug=True)
