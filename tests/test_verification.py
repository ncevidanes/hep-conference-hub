import sys
import unittest
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "apps/api")

from app.models.domain import ConfidenceLevel, VerificationFreshness
from app.services.verification import classify_confidence, classify_verification_freshness


class TestConfidenceClassification(unittest.TestCase):
    def test_unknown_without_score(self):
        self.assertEqual(classify_confidence(None), ConfidenceLevel.unknown)

    def test_high_confidence_threshold(self):
        self.assertEqual(classify_confidence(0.90), ConfidenceLevel.high)
        self.assertEqual(classify_confidence(1.0), ConfidenceLevel.high)

    def test_medium_confidence_threshold(self):
        self.assertEqual(classify_confidence(0.70), ConfidenceLevel.medium)
        self.assertEqual(classify_confidence(0.89), ConfidenceLevel.medium)

    def test_low_confidence(self):
        self.assertEqual(classify_confidence(0.69), ConfidenceLevel.low)
        self.assertEqual(classify_confidence(0.0), ConfidenceLevel.low)


class TestVerificationFreshness(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc)

    def test_unknown_without_date(self):
        self.assertEqual(
            classify_verification_freshness(None, self.now),
            VerificationFreshness.unknown,
        )

    def test_current_until_seven_days(self):
        self.assertEqual(
            classify_verification_freshness(self.now - timedelta(days=7), self.now),
            VerificationFreshness.current,
        )

    def test_aging_from_eight_to_thirty_days(self):
        self.assertEqual(
            classify_verification_freshness(self.now - timedelta(days=8), self.now),
            VerificationFreshness.aging,
        )
        self.assertEqual(
            classify_verification_freshness(self.now - timedelta(days=30), self.now),
            VerificationFreshness.aging,
        )

    def test_stale_after_thirty_days(self):
        self.assertEqual(
            classify_verification_freshness(self.now - timedelta(days=31), self.now),
            VerificationFreshness.stale,
        )


if __name__ == "__main__":
    unittest.main()
