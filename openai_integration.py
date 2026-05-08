import os
from openai import OpenAI

_API_KEY = os.getenv("OPENAI_API_KEY")
if not _API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable is required")

client = OpenAI(api_key=_API_KEY)


def get_completion(prompt, model="gpt-4.1-mini"):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content


def _normalize_messages(messages):
    allowed = {"system", "user", "assistant"}
    out = []
    for m in messages:
        role = (m.get("role") or "user").lower()
        if role not in allowed:
            # coerce unknown roles to user
            role = "user"
        content = m.get("content") or m.get("message") or ""
        out.append({"role": role, "content": content})
    return out


def get_completion_from_messages(messages, model="gpt-4.1-mini", temperature=0):
    """Accepts a list of {role, content} dicts and returns assistant content.

    Roles are normalized to `system`, `user`, `assistant`. Temperature is
    passed through. Requires `OPENAI_API_KEY` in the environment.
    """
    if not isinstance(messages, list):
        raise ValueError("messages must be a list of {role, content} dicts")

    messages = _normalize_messages(messages)

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content
