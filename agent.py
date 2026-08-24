"""
Minimal agent loop: perceive -> decide -> act -> observe.

call_model() automatically switches backend:
- if ANTHROPIC_API_KEY is set in the environment (loaded from .env)
  -> real model (Claude Haiku, a fraction of a cent per turn)
- otherwise -> scripted mock (fake_brain), zero cost.

`max_turns` is a deliberate safety guard: without it, a bug (the model
repeatedly requesting a tool) turns an ordinary software bug into a bill
that keeps growing.
"""
import os
from dotenv import load_dotenv

load_dotenv()  # loads .env into this Python process's environment variables

from tools import TOOLS_SCHEMA, TOOL_IMPLEMENTATIONS
from fake_brain import call_fake_model

_USE_REAL_MODEL = bool(os.getenv("ANTHROPIC_API_KEY"))

if _USE_REAL_MODEL:
    from real_brain import call_real_model

SYSTEM_PROMPT = (
    "You are an agent that answers the user's questions. "
    "Use the calculator tool for any arithmetic instead of computing it "
    "yourself, and the current_datetime tool if asked for the current date "
    "or time. Keep answers concise."
)


def call_model(messages, tools, system):
    if _USE_REAL_MODEL:
        return call_real_model(messages, tools, system)
    return call_fake_model(messages, tools, system)


def agent_turn(messages, max_turns: int = 5):
    """Advances the conversation by one user turn until the model produces
    a final answer, looping through as many tool round-trips as needed.
    `messages` is mutated in place: it is the shared context, persisted
    across successive user turns in the interactive loop."""
    for turn in range(1, max_turns + 1):
        response = call_model(messages, TOOLS_SCHEMA, SYSTEM_PROMPT)

        # The context grows: the model's response is appended as-is
        messages.append({"role": "assistant", "content": response["content"]})

        for block in response["content"]:
            if block["type"] == "text":
                print(f"[MODEL] {block['text']}")

        if response["stop_reason"] != "tool_use":
            return

        # The model requested one or more tools: execute them for real,
        # catching any failure so it is reported back TO THE MODEL instead
        # of crashing the loop.
        tool_results = []
        for block in response["content"]:
            if block["type"] != "tool_use":
                continue
            name = block["name"]
            tool_input = block["input"]
            print(f"[TOOL] calling {name}({tool_input})")

            impl = TOOL_IMPLEMENTATIONS.get(name)
            if impl is None:
                result = f"Error: unknown tool '{name}'."
            else:
                try:
                    result = impl(**tool_input)
                except Exception as e:
                    result = f"Error while running the tool: {e}"

            print(f"[TOOL] result: {result}")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block["id"],
                "content": str(result),
            })

        # Results are sent back to the model, which will see them next turn
        messages.append({"role": "user", "content": tool_results})

    print("[Turn ended: max tool round-trips reached.]")


def main():
    mode = "REAL MODEL (Haiku)" if _USE_REAL_MODEL else "MOCK MODEL (free)"
    print(f"[mode: {mode}] — type 'quit' to exit.\n")

    messages = []  # the context, shared across every question in this session
    while True:
        try:
            user_input = input("You: ").strip()
        except EOFError:
            break
        if user_input.lower() in ("quit", "exit"):
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})
        agent_turn(messages)


if __name__ == "__main__":
    main()
