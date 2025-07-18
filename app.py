from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.message import EmailMessage
import email.charset
import os 
import openai
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
from openai_integration import get_completion, get_completion_from_messages

openai.api_key  = os.getenv('OPENAI_API_KEY')
system_role_content = os.getenv('SYSTEM_ROLE_CONTENT')
email_sender = os.getenv('EMAIL_ADDRESS')         
email_password = os.getenv('EMAIL_PASSWORD')     
email_recipient = os.getenv('EMAIL_TO') or email_sender  

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

# Use UTF-8 as default encoding for all email content
email.charset.add_charset('utf-8', email.charset.SHORTEST, None, 'utf-8')

def send_email(subject, body):
    try:
        msg = EmailMessage()
        msg.set_content(body, charset='utf-8') 
        msg['Subject'] = str(subject)           
        msg['From'] = str(email_sender)
        msg['To'] = str(email_recipient)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_sender, email_password)
            server.send_message(msg)

    except Exception as e:
        print(f"Error sending email: {str(e)}")

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
        last_user_message = next((m['content'] for m in reversed(user_messages) if m['role'] == 'user'), None)
        if last_user_message:
            send_email("New Chatbot Question", f"User asked: {last_user_message}")

        completion = get_completion_from_messages(user_messages, temperature=1)
        return jsonify({"response": completion})

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request."}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))