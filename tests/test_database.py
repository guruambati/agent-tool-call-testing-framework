"""
test_database.py
================
12 tests covering: all tables, filter logic, limit bounds,
error paths, data isolation between calls.
"""

import pytest
from src.tools.database import DatabaseLookupTool


class TestDatabaseHappyPath:

    def test_list_all_users(self, db):
        r = db.run("users")
        assert r["count"] == 4
        assert r["table"] == "users"

    def test_filter_by_plan(self, db):
        r = db.run("users", filters={"plan": "pro"})
        assert r["count"] == 2
        assert all(row["plan"] == "pro" for row in r["rows"])

    def test_filter_by_active_false(self, db):
        r = db.run("users", filters={"active": False})
        assert r["count"] == 1
        assert r["rows"][0]["name"] == "Carol Singh"

    def test_orders_for_user_1(self, db):
        r = db.run("orders", filters={"user_id": 1})
        assert r["count"] == 2

    def test_out_of_stock_products(self, db):
        r = db.run("products", filters={"stock": 0})
        assert r["count"] == 1
        assert r["rows"][0]["sku"] == "GADGET-B"

    def test_limit_respected(self, db):
        r = db.run("users", limit=2)
        assert len(r["rows"]) == 2

    def test_empty_filter_returns_all_rows(self, db):
        r = db.run("products", filters={})
        assert r["count"] == 4

    def test_filter_by_category(self, db):
        r = db.run("products", filters={"category": "electronics"})
        assert r["count"] == 2


class TestDatabaseErrors:

    def test_unknown_table_raises(self, db):
        with pytest.raises(ValueError, match="Unknown table"):
            db.run("invoices")

    def test_negative_limit_raises(self, db):
        with pytest.raises(ValueError, match="positive"):
            db.run("users", limit=-1)

    def test_zero_limit_raises(self, db):
        with pytest.raises(ValueError, match="positive"):
            db.run("users", limit=0)

    def test_limit_over_max_raises(self, db):
        with pytest.raises(ValueError, match="1000"):
            db.run("users", limit=9999)


class TestDatabaseIsolation:

    def test_rows_are_copies_not_references(self, db):
        """Mutating returned rows must not affect future queries."""
        r1 = db.run("users")
        r1["rows"][0]["name"] = "MUTATED"
        r2 = db.run("users")
        assert r2["rows"][0]["name"] != "MUTATED"
