"""
email_sender.py
===============
Mock email sender tool.

Key testing properties:
  - Does NOT send real email — records sends in memory
  - Can simulate SMTP failure for specific addresses
  - Each send generates a unique message ID (non-idempotent by design)
  - Validates: address format, non-empty subject/body, valid priority
"""

from __future__ import annotations

import re
import uuid
from src.tools.base import BaseTool

EMAIL_REGEX    = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
VALID_PRIORITY = frozenset({"low", "normal", "high", "urgent"})


class EmailSenderTool(BaseTool):

    def __init__(self, simulate_failure_for: list[str] | None = None):
        super().__init__("email_sender")
        self._sent:         list[dict] = []
        self._fail_addrs:   set[str]   = set(simulate_failure_for or [])

    @property
    def sent_emails(self) -> list[dict]:
        """All successfully sent emails this session."""
        return list(self._sent)

    @property
    def sent_count(self) -> int:
        return len(self._sent)

    def run(self, to: str, subject: str, body: str,
            cc: str = "", priority: str = "normal") -> dict:
        """
        Send a mock email.

        Args:
            to       : recipient email address
            subject  : email subject line (non-empty)
            body     : email body (non-empty)
            cc       : optional CC address
            priority : low | normal | high | urgent

        Returns:
            dict with keys: message_id, to, subject, cc, priority, status
        """
        params = {"to": to, "subject": subject,
                  "body_length": len(body), "cc": cc, "priority": priority}

        try:
            # Validate recipient
            if not to or not EMAIL_REGEX.match(to.strip()):
                raise ValueError(f"Invalid 'to' email address: '{to}'")

            # Validate subject
            if not subject or not subject.strip():
                raise ValueError("'subject' cannot be empty.")

            # Validate body
            if not body or not body.strip():
                raise ValueError("'body' cannot be empty.")

            # Validate priority
            if priority.lower() not in VALID_PRIORITY:
                raise ValueError(
                    f"Invalid priority '{priority}'. "
                    f"Must be one of: {sorted(VALID_PRIORITY)}"
                )

            # Simulate SMTP failure
            if to.strip() in self._fail_addrs:
                raise ConnectionError(
                    f"SMTP delivery failed for '{to}'. "
                    "Simulated transient network error."
                )

            message_id = f"MSG-{uuid.uuid4().hex[:8].upper()}"
            output = {
                "message_id": message_id,
                "to":         to.strip(),
                "subject":    subject.strip(),
                "cc":         cc.strip(),
                "priority":   priority.lower(),
                "status":     "sent",
            }
            self._sent.append(output)
            self._record(params, output, success=True)
            return output

        except Exception as exc:
            self._record(params, None, success=False, error=str(exc))
            raise
