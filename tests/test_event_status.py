import sys
import unittest
from datetime import date

sys.path.insert(0, "apps/api")

from app.models.domain import EventStatus
from app.services.event_status import compute_event_status


class TestEventStatus(unittest.TestCase):
    def test_unknown_without_start_date(self):
        self.assertEqual(compute_event_status(None, None, date(2026, 7, 26)), EventStatus.unknown)

    def test_upcoming(self):
        self.assertEqual(
            compute_event_status(date(2026, 7, 30), date(2026, 8, 5), date(2026, 7, 26)),
            EventStatus.upcoming,
        )

    def test_ongoing_inclusive(self):
        self.assertEqual(
            compute_event_status(date(2026, 7, 26), date(2026, 7, 30), date(2026, 7, 26)),
            EventStatus.ongoing,
        )
        self.assertEqual(
            compute_event_status(date(2026, 7, 20), date(2026, 7, 26), date(2026, 7, 26)),
            EventStatus.ongoing,
        )

    def test_finished(self):
        self.assertEqual(
            compute_event_status(date(2026, 5, 18), date(2026, 5, 22), date(2026, 7, 26)),
            EventStatus.finished,
        )

    def test_one_day_event(self):
        self.assertEqual(
            compute_event_status(date(2026, 7, 26), None, date(2026, 7, 26)),
            EventStatus.ongoing,
        )


if __name__ == "__main__":
    unittest.main()
