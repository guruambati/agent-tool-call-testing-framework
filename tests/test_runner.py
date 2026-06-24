"""
test_runner.py
==============
14 tests covering: tool registration, dispatch, retry behavior,
session memory, context store, turn counter, audit log.
"""

import pytest
from src.agent.runner import AgentRunner
from src.tools.calculator import CalculatorTool


class TestToolRegistration:

    def test_register_and_call_tool(self, runner):
        calc = CalculatorTool()
        runner.register_tool("calculator", calc.run)
        result = runner.call_tool("calculator", {"operation": "add", "a": 3, "b": 4})
        assert result["success"] is True
        assert result["result"]["result"] == 7

    def test_unregistered_tool_raises(self, runner):
        with pytest.raises(ValueError, match="not registered"):
            runner.call_tool("nonexistent", {})

    def test_available_tools_lists_registered(self, wired_runner):
        assert "calculator"      in wired_runner.available_tools
        assert "weather"         in wired_runner.available_tools
        assert "email_sender"    in wired_runner.available_tools
        assert "database_lookup" in wired_runner.available_tools

    def test_unregister_removes_tool(self, wired_runner):
        wired_runner.unregister_tool("weather")
        assert "weather" not in wired_runner.available_tools

    def test_call_after_unregister_raises(self, wired_runner):
        wired_runner.unregister_tool("weather")
        with pytest.raises(ValueError, match="not registered"):
            wired_runner.call_tool("weather", {"city": "Tokyo"})


class TestRetryBehavior:

    def test_succeeds_on_third_attempt(self, runner):
        """Tool fails first 2 times then succeeds — should return success."""
        state = {"count": 0}

        def flaky(**kwargs):
            state["count"] += 1
            if state["count"] < 3:
                raise ConnectionError("Simulated network error")
            return {"ok": True}

        runner.register_tool("flaky", flaky)
        result = runner.call_tool("flaky", {})
        assert result["success"] is True
        assert result["attempts"] == 3

    def test_exhausted_retries_raises(self, runner):
        """Tool always fails — should raise after max_retries."""
        def always_fails(**kwargs):
            raise ConnectionError("Always fails")

        runner.register_tool("broken", always_fails)
        with pytest.raises(ConnectionError):
            runner.call_tool("broken", {})

    def test_non_retryable_error_raises_immediately(self, runner):
        """ValueError should not be retried — raises on first attempt."""
        call_count = {"n": 0}

        def bad_params(**kwargs):
            call_count["n"] += 1
            raise ValueError("Bad parameters")

        runner.register_tool("bad", bad_params)
        with pytest.raises(ValueError):
            runner.call_tool("bad", {})

        assert call_count["n"] == 1  # called exactly once — no retry

    def test_failed_call_recorded_in_audit_log(self, runner):
        def always_fails(**kwargs):
            raise ValueError("Intentional error")

        runner.register_tool("fails", always_fails)
        with pytest.raises(ValueError):
            runner.call_tool("fails", {})

        assert len(runner.state.tool_calls_made) == 1
        assert runner.state.tool_calls_made[0]["success"] is False


class TestSessionMemory:

    def test_context_set_and_get(self, runner):
        runner.set_context("user_city", "Hyderabad")
        assert runner.get_context("user_city") == "Hyderabad"

    def test_context_default_for_missing_key(self, runner):
        assert runner.get_context("missing", default="fallback") == "fallback"

    def test_turn_counter_increments_on_success(self, wired_runner):
        initial = wired_runner.state.turn
        wired_runner.call_tool("calculator", {"operation": "add", "a": 1, "b": 1})
        assert wired_runner.state.turn == initial + 1

    def test_tool_calls_recorded_in_audit_log(self, wired_runner):
        wired_runner.call_tool("calculator", {"operation": "multiply", "a": 3, "b": 3})
        log = wired_runner.state.tool_calls_made
        assert len(log) == 1
        assert log[0]["tool"] == "calculator"
        assert log[0]["success"] is True

    def test_session_id_preserved(self, runner):
        assert runner.state.session_id == "test-session"

    def test_no_session_raises_on_set_context(self):
        fresh = AgentRunner()
        with pytest.raises(RuntimeError, match="start_session"):
            fresh.set_context("key", "value")
