import os
import sys
import threading
import time
import requests

# Ensure the project root is on sys.path so imports work when running this script
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Ensure tests import the Flask app from the repo
# Ensure a dummy OPENAI_API_KEY is present so openai_integration doesn't raise
os.environ.setdefault('OPENAI_API_KEY', 'test')

# Create a lightweight fake `openai` module so imports succeed without the real SDK
import types
fake_openai = types.ModuleType('openai')
class _FakeOpenAI:
    def __init__(self, api_key=None):
        self.api_key = api_key
        # minimal placeholder for `.chat.completions.create` used during import
        class _C:
            def create(self, *a, **k):
                return None
        self.chat = types.SimpleNamespace(completions=_C())

fake_openai.OpenAI = _FakeOpenAI
sys.modules['openai'] = fake_openai

import openai_integration

# Replace the real client with a mock
from tests.mock_client import MockOpenAIClient
mock_client = MockOpenAIClient(response_text="Hello from mock")
openai_integration.client = mock_client

# Ensure system role content is set for the test
os.environ['SYSTEM_ROLE_CONTENT'] = "You are a helpful mock system prompt."

# Import Flask app after monkeypatch so it uses the patched openai integration
from app import app


def run_server():
    app.run(port=5001, debug=False)


server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

# Wait a moment for the server to start
time.sleep(1)

# Test single-message request
resp = requests.post(
    "http://127.0.0.1:5001/api/chat",
    json={"message": "Hi mock"}
)
print("Single message status:", resp.status_code, resp.json())

# Test messages-history request
resp2 = requests.post(
    "http://127.0.0.1:5001/api/chat",
    json={
        "messages": [
            {"role": "user", "content": "Who is Wendy?"}
        ],
        "temperature": 0.5
    }
)
print("Messages list status:", resp2.status_code, resp2.json())

# Stop after test
time.sleep(0.5)
