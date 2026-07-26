import sys
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

sys.path.insert(0, "apps/api")

from app.models.domain import SubmissionStatus
from app.services.status import compute_status


class TestSubmissionStatus(unittest.TestCase):
    def test_preserves_explicit_closed_without_deadline(self):
        call = SimpleNamespace(
            status=SubmissionStatus.closed,
            opens_at=None,
            deadline_at=None,
            extended_deadline_at=None,
        )
        self.assertEqual(
            compute_status(call, datetime(2026, 7, 26, tzinfo=timezone.utc)),
            SubmissionStatus.closed,
        )


if __name__ == "__main__":
    unittest.main()
