"""Tool implementations exposed to the agent.

Each tool has two deliberately separate parts:
  - a JSON schema (TOOLS_SCHEMA) describing the tool's name, purpose, and
    expected parameters to the model. This is the only part the model ever
    sees, and effectively functions as a piece of prompt.
  - a Python function (wired into TOOL_IMPLEMENTATIONS) that performs the
    actual work when the model requests the tool. The model never sees this
    code and has no visibility into what it does or which credentials, if
    any, it uses.
"""
import ast
import operator
from datetime import datetime

# Restricted arithmetic evaluator: only numeric expressions are evaluated,
# never arbitrary Python via a raw eval() on model-provided input.
_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError(f"Disallowed expression: {ast.dump(node)}")


def calculator(expression: str) -> str:
    try:
        tree = ast.parse(expression, mode="eval")
        result = _eval_node(tree.body)
        return str(result)
    except Exception as e:
        return f"Error: {e}"


def current_datetime() -> str:
    """A second, deliberately unrelated tool: lets us observe how the model
    selects between multiple available tools."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Schema sent to the model: this is EXACTLY the format expected by the
# `tools` parameter of Anthropic's Messages API.
TOOLS_SCHEMA = [
    {
        "name": "calculator",
        "description": "Evaluates a simple arithmetic expression (+ - * / **) and returns the result.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The expression to evaluate, e.g. '47 * 89'",
                }
            },
            "required": ["expression"],
        },
    },
    {
        "name": "current_datetime",
        "description": "Returns the current date and time (local time of the machine running the agent).",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]

# Dispatch table: tool name (as referenced by the model) -> actual Python implementation
TOOL_IMPLEMENTATIONS = {
    "calculator": calculator,
    "current_datetime": current_datetime,
}
