"""
calculator.py
=============
Mock calculator tool supporting arithmetic operations.

Supported operations: add, subtract, multiply, divide, sqrt, power, mod
Raises ValueError for unknown operations or invalid inputs.
Raises ZeroDivisionError for divide/mod by zero.
"""

from __future__ import annotations

import math
from src.tools.base import BaseTool


class CalculatorTool(BaseTool):

    SUPPORTED_OPS = frozenset(
        {"add", "subtract", "multiply", "divide", "sqrt", "power", "mod"}
    )

    def __init__(self):
        super().__init__("calculator")

    def run(self, operation: str, a: float, b: float | None = None) -> dict:
        """
        Execute an arithmetic operation.

        Args:
            operation : one of SUPPORTED_OPS
            a         : first operand
            b         : second operand (not required for sqrt)

        Returns:
            dict with keys: result, operation, a, b
        """
        params = {"operation": operation, "a": a, "b": b}

        try:
            op = operation.lower().strip()

            if op not in self.SUPPORTED_OPS:
                raise ValueError(
                    f"Unknown operation '{operation}'. "
                    f"Supported: {sorted(self.SUPPORTED_OPS)}"
                )

            # Unary operations
            if op == "sqrt":
                if a < 0:
                    raise ValueError("Cannot take sqrt of a negative number.")
                result = math.sqrt(a)

            else:
                # All other ops require b
                if b is None:
                    raise ValueError(
                        f"Operation '{operation}' requires parameter 'b'."
                    )
                if op == "add":
                    result = a + b
                elif op == "subtract":
                    result = a - b
                elif op == "multiply":
                    result = a * b
                elif op == "divide":
                    if b == 0:
                        raise ZeroDivisionError("Division by zero is undefined.")
                    result = a / b
                elif op == "power":
                    result = a ** b
                elif op == "mod":
                    if b == 0:
                        raise ZeroDivisionError("Modulo by zero is undefined.")
                    result = a % b

            output = {"result": result, "operation": op, "a": a, "b": b}
            self._record(params, output, success=True)
            return output

        except Exception as exc:
            self._record(params, None, success=False, error=str(exc))
            raise
