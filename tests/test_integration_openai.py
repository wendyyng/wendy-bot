import os
import sys
import json
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Require explicit opt-in to run this integration test to avoid accidental
# calls/charges. Set both `OPENAI_API_KEY` and `RUN_OPENAI_INTEGRATION=1`.
skip_reason = (
    "Set OPENAI_API_KEY and RUN_OPENAI_INTEGRATION=1 to run OpenAI integration tests"
)

pytestmark = pytest.mark.skipif(
    not (os.getenv('OPENAI_API_KEY') and os.getenv('RUN_OPENAI_INTEGRATION') == '1'),
    reason=skip_reason,
)

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from app import app


def test_chat_endpoint_with_openai():
    """Lightweight integration: POST to /api/chat and assert structured success."""
    client = app.test_client()

    payload = {
        "messages": [
            {"role": "user", "content": "What is Wendy's last name?"}
        ]
    }

    resp = client.post('/api/chat', json=payload)
    assert resp.status_code in (200, 502, 500)

    body = resp.get_json() or {}
    if resp.status_code == 200:
        assert 'response' in body and isinstance(body['response'], str)
    else:
        # If OpenAI or system error occurred, ensure structured error returned
        assert 'error' in body and body['error'] in ('openai_error', 'system_error')
