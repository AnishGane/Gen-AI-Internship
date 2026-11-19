"""Offline tests: no API key or network needed. Run with `pytest`."""
import json
from types import SimpleNamespace

import Week9.agent.loop as loop
from Week9.agent.tools import execute_tool

def test_multiply_is_exact():
    out = json.loads(execute_tool("multiply_numbers", '{"a": 238, "b": 417}'))
    assert out["result"] == 99246.0

def test_divide_by_zero_returns_error():
    out = json.loads(execute_tool("divide_numbers", '{"a": 1, "b": 0}'))
    assert "error" in out

def test_unknown_tool_rejected():
    out = json.loads(execute_tool("delete_everything", "{}"))
    assert "Unknown tool" in out["error"]

def test_bad_inputs_rejected():
    assert "error" in json.loads(execute_tool("add_numbers", '{"a": "x", "b": 1}'))
    assert "error" in json.loads(execute_tool("add_numbers", '{"a": 1}'))
    assert "error" in json.loads(execute_tool("add_numbers", "not json"))

def _resp(content=None, tool_calls=None):
    msg = SimpleNamespace(content=content, tool_calls=tool_calls)
    return SimpleNamespace(choices=[SimpleNamespace(message=msg)], model="fake/model:free")

def test_loop_runs_tool_then_answers(monkeypatch):
    call = SimpleNamespace(
        id="call_1",
        function=SimpleNamespace(name="multiply_numbers", arguments='{"a": 238, "b": 417}'),
    )
    replies = iter([_resp(tool_calls=[call]), _resp(content="It is 99246.")])
    seen = []

    def fake_chat(client, messages, tools, models):
        seen.append(list(messages))
        return next(replies)

    monkeypatch.setattr(loop, "chat", fake_chat)
    answer = loop.run_agent(None, ["fake"], "238 x 417?", verbose=False)

    assert answer == "It is 99246."
    tool_msg = seen[1][-1]  # what the model saw on the 2nd call
    assert tool_msg["role"] == "tool" and "99246" in tool_msg["content"]

def test_loop_stops_at_max_steps(monkeypatch):
    call = SimpleNamespace(
        id="c", function=SimpleNamespace(name="get_utc_time", arguments="{}")
    )
    monkeypatch.setattr(loop, "chat", lambda *a, **k: _resp(tool_calls=[call]))
    assert "max_steps" in loop.run_agent(None, ["fake"], "loop", max_steps=2, verbose=False)