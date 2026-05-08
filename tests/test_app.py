import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tests.mock_client import MockOpenAIClient

# Provide a fake `openai` module so imports succeed in the test environment
import types
fake_openai = types.ModuleType('openai')
class _FakeOpenAI:
    def __init__(self, api_key=None):
        self.api_key = api_key
        class _C:
            def create(self, *a, **k):
                return None
        self.chat = types.SimpleNamespace(completions=_C())

fake_openai.OpenAI = _FakeOpenAI
import sys
sys.modules['openai'] = fake_openai

# Ensure OPENAI_API_KEY is set for the module under test
import os as _os
_os.environ.setdefault('OPENAI_API_KEY', 'test')

# Import the module under test after providing the fake `openai`
import openai_integration
# import app after sys.path configured
from app import app


def test_single_message(monkeypatch):
    mock = MockOpenAIClient(response_text="Mocked reply")
    monkeypatch.setattr(openai_integration, 'client', mock)
    os.environ['SYSTEM_ROLE_CONTENT'] = "You are test system prompt."

    client = app.test_client()
    resp = client.post('/api/chat', json={'message': 'hello'})
    assert resp.status_code == 200
    assert resp.get_json() == {'response': 'Mocked reply'}


def test_messages_list(monkeypatch):
    mock = MockOpenAIClient(response_text="Mocked reply 2")
    monkeypatch.setattr(openai_integration, 'client', mock)
    os.environ['SYSTEM_ROLE_CONTENT'] = "You are test system prompt."

    client = app.test_client()
    resp = client.post('/api/chat', json={
        'messages': [{'role': 'user', 'content': 'Who is Wendy?'}],
        'temperature': 0.5
    })
    assert resp.status_code == 200
    assert resp.get_json() == {'response': 'Mocked reply 2'}
