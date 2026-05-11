from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import json
from app import app

client = app.test_client()

payload = {
    "messages": [
        {"role": "user", "content": "What is Wendy's last name?"}
    ]
}

resp = client.post('/api/chat', json=payload)
print('STATUS:', resp.status_code)
try:
    print('BODY:', json.dumps(resp.get_json(), indent=2, ensure_ascii=False))
except Exception:
    print('BODY (raw):', resp.data)
