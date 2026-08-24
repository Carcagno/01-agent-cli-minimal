"""
A scripted stand-in for the model, used to build and test the agent loop's
plumbing (block parsing, tool dispatch, growing context) without spending
any API tokens. It mimics the normalized response shape used throughout
this project -> {"stop_reason": ..., "content": [...]} — see real_brain.py
for the real implementation, which exposes the same interface.

Replayed scenario (first exchange only — this stub validates plumbing, it
does not simulate a realistic multi-turn conversation):
  Turn 1 -> the model decides to call the "calculator" tool
  Turn 2 -> after receiving the tool result, it replies with text
"""

_step = {"n": 0}


def call_fake_model(messages, tools, system=None):
    # `system` is accepted for interface parity but ignored: this stub only
    # replays a fixed scenario, it doesn't actually read instructions.
    _step["n"] += 1

    if _step["n"] == 1:
        return {
            "stop_reason": "tool_use",
            "content": [
                {"type": "text", "text": "Let me calculate that."},
                {
                    "type": "tool_use",
                    "id": "toolu_fake_001",
                    "name": "calculator",
                    "input": {"expression": "47 * 89"},
                },
            ],
        }

    return {
        "stop_reason": "end_turn",
        "content": [
            {"type": "text", "text": "47 * 89 = 4183."}
        ],
    }
