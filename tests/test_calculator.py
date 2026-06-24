"""
test_calculator.py
==================
14 tests covering: all operations, edge cases, error paths,
call history recording, and idempotency.
"""

import math
import pytest
from src.tools.calculator import CalculatorTool


class TestCalculatorOperations:

    def test_addition(self, calc):
        assert calc.run("add", 3, 4)["result"] == 7

    def test_subtraction(self, calc):
        assert calc.run("subtract", 10, 3)["result"] == 7

    def test_multiplication(self, calc):
        assert calc.run("multiply", 6, 7)["result"] == 42

    def test_division(self, calc):
        assert calc.run("divide", 15, 3)["result"] == 5.0

    def test_power(self, calc):
        assert calc.run("power", 2, 8)["result"] == 256

    def test_modulo(self, calc):
        assert calc.run("mod", 17, 5)["result"] == 2

    def test_sqrt(self, calc):
        assert calc.run("sqrt", 16)["result"] == 4.0

    def test_float_inputs(self, calc):
        assert abs(calc.run("add", 1.5, 2.5)["result"] - 4.0) < 1e-9

    def test_result_includes_operation_and_operands(self, calc):
        r = calc.run("multiply", 3, 5)
        assert r["operation"] == "multiply"
        assert r["a"] == 3
        assert r["b"] == 5


class TestCalculatorErrors:

    def test_division_by_zero_raises(self, calc):
        with pytest.raises(ZeroDivisionError):
            calc.run("divide", 10, 0)

    def test_modulo_by_zero_raises(self, calc):
        with pytest.raises(ZeroDivisionError):
            calc.run("mod", 10, 0)

    def test_sqrt_negative_raises(self, calc):
        with pytest.raises(ValueError, match="negative"):
            calc.run("sqrt", -9)

    def test_unknown_operation_raises(self, calc):
        with pytest.raises(ValueError, match="Unknown operation"):
            calc.run("logarithm", 100)

    def test_missing_b_for_binary_op_raises(self, calc):
        with pytest.raises(ValueError, match="requires parameter"):
            calc.run("add", 5)


class TestCalculatorHistory:

    def test_successful_call_recorded(self, calc):
        calc.run("add", 1, 2)
        assert calc.call_count == 1
        assert calc.last_call.success is True

    def test_failed_call_recorded(self, calc):
        with pytest.raises(ZeroDivisionError):
            calc.run("divide", 5, 0)
        assert calc.call_count == 1
        assert calc.last_call.success is False
        assert "zero" in calc.last_call.error.lower()

    def test_multiple_calls_tracked(self, calc):
        calc.run("add", 1, 2)
        calc.run("multiply", 3, 4)
        assert calc.call_count == 2

    def test_reset_clears_history(self, calc):
        calc.run("add", 1, 2)
        calc.reset()
        assert calc.call_count == 0
        assert calc.call_history == []


class TestCalculatorIdempotency:

    def test_same_inputs_same_result(self, calc):
        r1 = calc.run("multiply", 7, 8)
        r2 = calc.run("multiply", 7, 8)
        assert r1["result"] == r2["result"]

    def test_repeated_calls_accumulate_history(self, calc):
        for _ in range(5):
            calc.run("add", 1, 1)
        assert calc.call_count == 5
