"""
base.py
=======
BaseTool and ToolCall dataclass.

Every tool inherits from BaseTool which provides:
  - call_history : full audit log of every invocation
  - call_count   : total number of calls (successful + failed)
  - reset()      : clear history between test cases
  - _record()    : internal method to persist each call result
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    """
    Immutable record of one tool invocation.
    Stored in BaseTool.call_history for audit and side-effect testing.
    """
    tool_name:  str
    params:     dict
    result:     Any
    timestamp:  float = field(default_factory=time.time)
    call_id:    str   = field(default_factory=lambda: uuid.uuid4().hex[:8])
    success:    bool  = True
    error:      str   = ""


class BaseTool:
    """
    Base class for all mock tools.

    Subclasses implement a run(**kwargs) method that:
      1. Validates inputs
      2. Performs the operation
      3. Calls self._record() to log the result
      4. Returns a plain dict result
    """

    def __init__(self, name: str):
        self.name        = name
        self._history:   list[ToolCall] = []
        self._call_count = 0

    @property
    def call_history(self) -> list[ToolCall]:
        """Read-only copy of the full call log."""
        return list(self._history)

    @property
    def call_count(self) -> int:
        return self._call_count

    @property
    def last_call(self) -> ToolCall | None:
        return self._history[-1] if self._history else None

    def reset(self) -> None:
        """Clear history between test cases — prevents test pollution."""
        self._history.clear()
        self._call_count = 0

    def _record(self, params: dict, result: Any,
                success: bool = True, error: str = "") -> ToolCall:
        record = ToolCall(
            tool_name=self.name,
            params=params,
            result=result,
            success=success,
            error=error,
        )
        self._history.append(record)
        self._call_count += 1
        return record
