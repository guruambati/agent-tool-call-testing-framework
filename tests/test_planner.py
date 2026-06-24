"""
test_planner.py
===============
10 tests covering: multi-step plans, abort-on-failure,
continue-on-failure, partial results, and empty plans.
"""

import pytest


class TestPlannerHappyPath:

    def test_all_steps_succeed(self, planner):
        plan = [
            {"tool": "calculator",      "params": {"operation": "add", "a": 10, "b": 5}},
            {"tool": "weather",         "params": {"city": "Tokyo"}},
            {"tool": "database_lookup", "params": {"table": "users", "limit": 2}},
        ]
        results = planner.execute(plan)
        assert len(results) == 3
        assert all(r["success"] for r in results)

    def test_result_contains_output(self, planner):
        plan = [{"tool": "calculator", "params": {"operation": "multiply", "a": 6, "b": 7}}]
        results = planner.execute(plan)
        assert results[0]["output"]["result"]["result"] == 42

    def test_empty_plan_returns_empty(self, planner):
        results = planner.execute([])
        assert results == []

    def test_single_step_plan(self, planner):
        plan = [{"tool": "weather", "params": {"city": "London"}}]
        results = planner.execute(plan)
        assert len(results) == 1
        assert results[0]["success"] is True


class TestPlannerAbortBehavior:

    def test_aborts_on_first_failure_by_default(self, planner):
        """Step 1 fails → step 2 never runs."""
        plan = [
            {"tool": "calculator",
             "params": {"operation": "divide", "a": 1, "b": 0}},  # ZeroDivisionError
            {"tool": "weather",
             "params": {"city": "Tokyo"}},  # should not run
        ]
        results = planner.execute(plan)
        assert len(results) == 1
        assert not results[0]["success"]

    def test_continues_when_abort_false(self, planner):
        """abort_on_failure=False → all steps run even after failure."""
        plan = [
            {"tool": "calculator",
             "params": {"operation": "divide", "a": 1, "b": 0},
             "abort_on_failure": False},
            {"tool": "weather",
             "params": {"city": "London"}},
        ]
        results = planner.execute(plan)
        assert len(results) == 2
        assert not results[0]["success"]
        assert results[1]["success"] is True

    def test_error_message_in_failed_result(self, planner):
        plan = [
            {"tool": "calculator",
             "params": {"operation": "divide", "a": 5, "b": 0}},
        ]
        results = planner.execute(plan)
        assert "error" in results[0]
        assert len(results[0]["error"]) > 0

    def test_abort_after_second_step(self, planner):
        plan = [
            {"tool": "calculator",      "params": {"operation": "add", "a": 1, "b": 1}},
            {"tool": "database_lookup", "params": {"table": "invoices"}},  # bad table
            {"tool": "weather",         "params": {"city": "Tokyo"}},
        ]
        results = planner.execute(plan)
        assert len(results) == 2
        assert results[0]["success"] is True
        assert results[1]["success"] is False


class TestPlannerAuditLog:

    def test_successful_steps_in_runner_log(self, planner, wired_runner):
        plan = [
            {"tool": "calculator", "params": {"operation": "add", "a": 2, "b": 2}},
            {"tool": "weather",    "params": {"city": "Sydney"}},
        ]
        planner.execute(plan)
        log = wired_runner.state.tool_calls_made
        assert len(log) == 2
        tools_called = [entry["tool"] for entry in log]
        assert "calculator" in tools_called
        assert "weather" in tools_called
