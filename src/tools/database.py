"""
database.py
===========
Mock database lookup tool with an in-memory dataset.

Tables: users, orders, products
Supports: table selection, key=value filters, row limit
Raises: ValueError for unknown tables, invalid limits
"""

from __future__ import annotations

import copy
from src.tools.base import BaseTool


# In-memory mock dataset
MOCK_TABLES: dict[str, list[dict]] = {
    "users": [
        {"id": 1, "name": "Alice Chen",   "email": "alice@example.com", "plan": "pro",        "active": True},
        {"id": 2, "name": "Bob Martinez", "email": "bob@example.com",   "plan": "free",       "active": True},
        {"id": 3, "name": "Carol Singh",  "email": "carol@example.com", "plan": "enterprise", "active": False},
        {"id": 4, "name": "David Kim",    "email": "david@example.com", "plan": "pro",        "active": True},
    ],
    "orders": [
        {"order_id": "ORD-001", "user_id": 1, "amount": 99.99,  "status": "shipped"},
        {"order_id": "ORD-002", "user_id": 2, "amount": 19.99,  "status": "pending"},
        {"order_id": "ORD-003", "user_id": 1, "amount": 149.00, "status": "delivered"},
        {"order_id": "ORD-004", "user_id": 4, "amount": 49.99,  "status": "cancelled"},
    ],
    "products": [
        {"sku": "WIDGET-A", "name": "Widget A", "price": 9.99,  "stock": 250, "category": "tools"},
        {"sku": "GADGET-B", "name": "Gadget B", "price": 49.99, "stock": 0,   "category": "electronics"},
        {"sku": "DEVICE-C", "name": "Device C", "price": 199.0, "stock": 15,  "category": "electronics"},
        {"sku": "THING-D",  "name": "Thing D",  "price": 4.99,  "stock": 500, "category": "tools"},
    ],
}

VALID_TABLES = frozenset(MOCK_TABLES.keys())
MAX_LIMIT    = 1000


class DatabaseLookupTool(BaseTool):

    def __init__(self):
        super().__init__("database_lookup")

    def run(self, table: str,
            filters: dict | None = None,
            limit: int = 10) -> dict:
        """
        Query a mock database table.

        Args:
            table   : one of users | orders | products
            filters : optional dict of {column: value} equality filters
            limit   : maximum rows to return (1–1000)

        Returns:
            dict with keys: table, rows, count
        """
        params = {"table": table, "filters": filters, "limit": limit}

        try:
            if table not in VALID_TABLES:
                raise ValueError(
                    f"Unknown table '{table}'. "
                    f"Valid tables: {sorted(VALID_TABLES)}"
                )

            if not isinstance(limit, int) or limit <= 0:
                raise ValueError("'limit' must be a positive integer.")

            if limit > MAX_LIMIT:
                raise ValueError(
                    f"'limit' cannot exceed {MAX_LIMIT}. Got {limit}."
                )

            # Deep copy so tests cannot mutate the source data
            rows = copy.deepcopy(MOCK_TABLES[table])

            if filters:
                for key, value in filters.items():
                    rows = [r for r in rows if r.get(key) == value]

            rows = rows[:limit]
            output = {"table": table, "rows": rows, "count": len(rows)}
            self._record(params, output, success=True)
            return output

        except Exception as exc:
            self._record(params, None, success=False, error=str(exc))
            raise
