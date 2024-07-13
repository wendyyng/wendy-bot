from flask import Flask, request, jsonify
from flask_cors import CORS
import os 
import openai
from dotenv import load_dotenv, find_dotenv
from openai_integration import get_completion, get_completion_from_messages


load_dotenv(find_dotenv())


app = Flask(__name__)
CORS(app)  # Enable CORS for all origins


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')

        completion = get_completion(prompt=message, model="gpt-3.5-turbo")

        return jsonify({"response": completion})

    except Exception as e:
        # Log the exception to diagnose the issue
        print(f"Error processing request: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request."}), 500

if __name__ == '__main__':
    app.run(debug=True)
