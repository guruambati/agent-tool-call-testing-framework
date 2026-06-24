"""
planner.py
==========
PlanExecutor — runs a sequence of tool steps as an agent plan.

Each step is a dict:
    {
        "tool":             "calculator",
        "params":           {"operation": "add", "a": 1, "b": 2},
        "abort_on_failure": True   # optional, default True
    }

Results are accumulated and returned as a list.
"""

from __future__ import annotations

from src.agent.runner import AgentRunner


class PlanExecutor:
    """
    Executes a multi-step tool plan through an AgentRunner.

    Stops at the first failed step unless abort_on_failure=False.
    """

    def __init__(self, runner: AgentRunner):
        self._runner = runner

    def execute(self, plan: list[dict]) -> list[dict]:
        """
        Run every step in order.

        Returns a list of step result dicts:
            {"step": <original step>, "output": <tool result>, "success": True}
            {"step": <original step>, "error": <msg>,          "success": False}
        """
        results = []
        for step in plan:
            tool_name        = step["tool"]
            params           = step.get("params", {})
            abort_on_failure = step.get("abort_on_failure", True)

            try:
                output = self._runner.call_tool(tool_name, params)
                results.append({"step": step, "output": output, "success": True})

            except Exception as exc:
                results.append({"step": step, "error": str(exc), "success": False})
                if abort_on_failure:
                    break

        return results

    @property
    def completed_steps(self) -> int:
        return self._runner.state.turn if self._runner.state else 0
