"""
The real "brain": an actual call to Anthropic's Messages API (Claude Haiku),
normalized into the same dict shape used by fake_brain.py
-> {"stop_reason": ..., "content": [...]}.

This is the only file that differs from the mock: the rest of the loop
(agent.py) has no awareness that the source changed.
"""
from anthropic import Anthropic

# The client reads ANTHROPIC_API_KEY from the environment automatically
# (loaded from .env by python-dotenv, see agent.py). No key is hardcoded here.
_client = Anthropic()

MODEL = "claude-haiku-4-5-20251001"


def call_real_model(messages, tools, system=None, max_tokens=300):
    kwargs = dict(model=MODEL, max_tokens=max_tokens, tools=tools, messages=messages)
    if system:
        kwargs["system"] = system

    response = _client.messages.create(**kwargs)

    content = []
    for block in response.content:
        if block.type == "text":
            content.append({"type": "text", "text": block.text})
        elif block.type == "tool_use":
            content.append({
                "type": "tool_use",
                "id": block.id,
                "name": block.name,
                "input": block.input,
            })

    return {"stop_reason": response.stop_reason, "content": content}
