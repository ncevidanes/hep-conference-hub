import sys
import unittest
from datetime import date
from types import SimpleNamespace

sys.path.insert(0, "apps/api")

from app.models.domain import RegistrationStatus
from app.services.registration_status import compute_registration_status


class TestRegistrationStatus(unittest.TestCase):
    def make_registration(self, *, status, opens_on=None, deadline_on=None):
        return SimpleNamespace(
            status=status,
            opens_on=opens_on,
            deadline_on=deadline_on,
        )

    def test_upcoming_before_opening(self):
        registration = self.make_registration(
            status=RegistrationStatus.unknown,
            opens_on=date(2026, 8, 1),
            deadline_on=date(2026, 8, 20),
        )
        self.assertEqual(
            compute_registration_status(registration, date(2026, 7, 26)),
            RegistrationStatus.upcoming,
        )

    def test_open_inside_window(self):
        registration = self.make_registration(
            status=RegistrationStatus.unknown,
            opens_on=date(2026, 7, 1),
            deadline_on=date(2026, 7, 30),
        )
        self.assertEqual(
            compute_registration_status(registration, date(2026, 7, 26)),
            RegistrationStatus.open,
        )

    def test_closed_after_deadline(self):
        registration = self.make_registration(
            status=RegistrationStatus.open,
            opens_on=date(2026, 1, 10),
            deadline_on=date(2026, 7, 23),
        )
        self.assertEqual(
            compute_registration_status(registration, date(2026, 7, 26)),
            RegistrationStatus.closed,
        )

    def test_preserves_explicit_status_without_dates(self):
        registration = self.make_registration(
            status=RegistrationStatus.closed,
        )
        self.assertEqual(
            compute_registration_status(registration, date(2026, 7, 26)),
            RegistrationStatus.closed,
        )

    def test_preserves_closed_when_capacity_is_reached_without_deadline(self):
        item = SimpleNamespace(
            opens_on=date(2026, 6, 4),
            deadline_on=None,
            status=RegistrationStatus.closed,
        )
        self.assertEqual(
            compute_registration_status(item, date(2026, 7, 26)),
            RegistrationStatus.closed,
        )


if __name__ == "__main__":
    unittest.main()
