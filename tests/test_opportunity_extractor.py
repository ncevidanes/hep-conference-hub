import sys
import unittest

sys.path.insert(0, "apps/crawler")

from conference_crawler.extractors.opportunity_status import extract_opportunity_statuses


ICHEP_TEXT = """
Abstract Submission is Closed
Registration Opening January 10, 2026
Early Registration Deadline May 15, 2026 Closed
Regular Registration Deadline July 23, 2026 Closed
"""


class TestOpportunityExtractor(unittest.TestCase):
    def test_extracts_submission_and_registration_independently(self):
        result = extract_opportunity_statuses(ICHEP_TEXT)

        self.assertEqual(result["submission_status"], "closed")
        self.assertEqual(result["submission_source_excerpt"], "Abstract Submission is Closed")
        self.assertEqual(len(result["registrations"]), 2)

        early = result["registrations"][0]
        regular = result["registrations"][1]

        self.assertEqual(early["registration_type"], "early")
        self.assertEqual(early["opens_on"], "2026-01-10")
        self.assertEqual(early["deadline_on"], "2026-05-15")
        self.assertEqual(early["status"], "closed")

        self.assertEqual(regular["registration_type"], "regular")
        self.assertIsNone(regular["opens_on"])
        self.assertEqual(regular["deadline_on"], "2026-07-23")
        self.assertEqual(regular["status"], "closed")

    def test_does_not_invent_missing_deadlines(self):
        result = extract_opportunity_statuses("Abstract Submission is Closed")
        self.assertEqual(result["submission_status"], "closed")
        self.assertEqual(result["registrations"], [])


if __name__ == "__main__":
    unittest.main()
