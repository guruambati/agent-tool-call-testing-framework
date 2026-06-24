"""
runner.py
=========
AgentRunner — tool dispatch with retry logic and session memory.

Responsibilities:
  - Tool registry (register/unregister named tools)
  - call_tool() with configurable retry and exponential back-off
  - Session state: context key-value store + full call audit log
  - Turn counter tracking
"""

from __future__ import annotations

import copy
import time
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class AgentSession:
    """Holds all state for one agent conversation session."""
    session_id:      str
    context:         dict       = field(default_factory=dict)
    tool_calls_made: list[dict] = field(default_factory=list)
    turn:            int        = 0


class AgentRunner:
    """
    Minimal agent runner for testing tool dispatch, retry, and memory.

    Usage:
        runner = AgentRunner(max_retries=3, retry_delay_s=0.1)
        runner.start_session("session-1")
        runner.register_tool("calculator", calc_tool.run)

        result = runner.call_tool("calculator", {"operation": "add", "a": 1, "b": 2})
        # {"success": True, "result": {...}, "attempts": 1}
    """

    # Errors that trigger retry (transient / network failures)
    DEFAULT_RETRYABLE = (ConnectionError, TimeoutError)

    def __init__(self, max_retries: int = 3, retry_delay_s: float = 0.1):
        self.max_retries   = max_retries
        self.retry_delay_s = retry_delay_s
        self._tools:       dict[str, Callable] = {}
        self._session:     AgentSession | None = None

    # ── Tool Registry ─────────────────────────────────────────

    def register_tool(self, name: str, fn: Callable) -> None:
        self._tools[name] = fn

    def unregister_tool(self, name: str) -> None:
        self._tools.pop(name, None)

    @property
    def available_tools(self) -> list[str]:
        return sorted(self._tools.keys())

    # ── Session ───────────────────────────────────────────────

    def start_session(self, session_id: str = "default") -> AgentSession:
        self._session = AgentSession(session_id=session_id)
        return self._session

    @property
    def state(self) -> AgentSession | None:
        return self._session

    def set_context(self, key: str, value: Any) -> None:
        if self._session is None:
            raise RuntimeError("No active session. Call start_session() first.")
        self._session.context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        if self._session is None:
            return default
        return self._session.context.get(key, default)

    # ── Tool Call with Retry ──────────────────────────────────

    def call_tool(self, tool_name: str, params: dict,
                  retryable_errors: tuple = DEFAULT_RETRYABLE) -> dict:
        """
        Dispatch a tool call with retry logic.

        - Retries only on retryable_errors (default: ConnectionError, TimeoutError)
        - Non-retryable errors raise immediately after one attempt
        - Records every attempt in session.tool_calls_made

        Returns:
            {"success": True, "result": <tool output>, "attempts": <int>}
        """
        if tool_name not in self._tools:
            raise ValueError(
                f"Tool '{tool_name}' is not registered. "
                f"Available: {self.available_tools}"
            )

        tool_fn    = self._tools[tool_name]
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                result = tool_fn(**params)
                record = {
                    "tool":      tool_name,
                    "params":    copy.deepcopy(params),
                    "result":    result,
                    "attempt":   attempt,
                    "success":   True,
                    "timestamp": time.time(),
                }
                self._append_record(record)
                return {"success": True, "result": result, "attempts": attempt}

            except retryable_errors as exc:
                last_error = exc
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay_s * attempt)

            except Exception as exc:
                # Non-retryable — record and re-raise immediately
                record = {
                    "tool":      tool_name,
                    "params":    copy.deepcopy(params),
                    "result":    None,
                    "attempt":   attempt,
                    "success":   False,
                    "error":     str(exc),
                    "timestamp": time.time(),
                }
                self._append_record(record)
                raise

        # All retries exhausted
        record = {
            "tool":      tool_name,
            "params":    copy.deepcopy(params),
            "result":    None,
            "attempts":  self.max_retries,
            "success":   False,
            "error":     str(last_error),
            "timestamp": time.time(),
        }
        self._append_record(record)
        raise last_error

    def _append_record(self, record: dict) -> None:
        if self._session:
            self._session.tool_calls_made.append(record)
            self._session.turn += 1
