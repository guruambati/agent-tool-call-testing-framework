"""
test_email.py
=============
13 tests covering: valid sends, message ID uniqueness,
validation errors, SMTP failure simulation,
side-effect isolation, and priority handling.
"""

import pytest
from src.tools.email_sender import EmailSenderTool


class TestEmailHappyPath:

    def test_valid_email_returns_sent(self, email):
        r = email.run("alice@example.com", "Hello", "Body text here")
        assert r["status"] == "sent"

    def test_message_id_prefixed_msg(self, email):
        r = email.run("bob@example.com", "Subject", "Body")
        assert r["message_id"].startswith("MSG-")

    def test_sent_emails_recorded(self, email):
        email.run("a@b.com", "S1", "B1")
        email.run("c@d.com", "S2", "B2")
        assert email.sent_count == 2

    def test_cc_field_preserved(self, email):
        r = email.run("a@b.com", "Sub", "Body", cc="manager@b.com")
        assert r["cc"] == "manager@b.com"

    def test_high_priority_accepted(self, email):
        r = email.run("a@b.com", "Urgent", "Body", priority="high")
        assert r["priority"] == "high"
        assert r["status"] == "sent"


class TestEmailValidationErrors:

    def test_invalid_email_address_raises(self, email):
        with pytest.raises(ValueError, match="email"):
            email.run("not-an-email", "Subject", "Body")

    def test_empty_subject_raises(self, email):
        with pytest.raises(ValueError, match="subject"):
            email.run("a@b.com", "", "Body")

    def test_whitespace_subject_raises(self, email):
        with pytest.raises(ValueError, match="subject"):
            email.run("a@b.com", "   ", "Body")

    def test_empty_body_raises(self, email):
        with pytest.raises(ValueError, match="body"):
            email.run("a@b.com", "Subject", "")

    def test_invalid_priority_raises(self, email):
        with pytest.raises(ValueError, match="priority"):
            email.run("a@b.com", "Sub", "Body", priority="critical")


class TestEmailSideEffects:

    def test_smtp_failure_simulated(self):
        broken = EmailSenderTool(simulate_failure_for=["fail@example.com"])
        with pytest.raises(ConnectionError, match="SMTP"):
            broken.run("fail@example.com", "Subject", "Body")

    def test_failed_send_not_in_sent_list(self):
        broken = EmailSenderTool(simulate_failure_for=["fail@example.com"])
        with pytest.raises(ConnectionError):
            broken.run("fail@example.com", "Subject", "Body")
        assert broken.sent_count == 0

    def test_side_effect_isolation_between_instances(self):
        """Two EmailSenderTool instances must not share sent state."""
        e1 = EmailSenderTool()
        e2 = EmailSenderTool()
        e1.run("a@b.com", "Sub", "Body")
        assert e1.sent_count == 1
        assert e2.sent_count == 0

    def test_each_send_unique_message_id(self, email):
        """Email is intentionally non-idempotent — each call must produce a new ID."""
        r1 = email.run("a@b.com", "Same Subject", "Same Body")
        r2 = email.run("a@b.com", "Same Subject", "Same Body")
        assert r1["message_id"] != r2["message_id"]
