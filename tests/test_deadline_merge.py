import sys
import unittest

sys.path.insert(0, "apps/crawler")

from conference_crawler.extractors.deadline_candidates import merge_deadline_candidates


class TestDeadlineMerge(unittest.TestCase):
    def test_preserves_conflicting_official_dates(self):
        candidates = [
            {
                "kind": "talk_abstract_deadline",
                "date": "2026-02-02",
                "time": None,
                "source_url": "https://ichep2026.org/important-days.html",
                "confidence": 0.93,
            },
            {
                "kind": "talk_abstract_deadline",
                "date": "2026-02-09",
                "time": "23:59",
                "source_url": "https://indico.cern.ch/event/1522800/abstracts/",
                "confidence": 0.99,
            },
        ]
        result = merge_deadline_candidates(candidates)
        self.assertIn("talk_abstract_deadline", result["conflicts"])
        self.assertTrue(result["resolved"]["talk_abstract_deadline"]["conflicting"])
        self.assertEqual(
            result["resolved"]["talk_abstract_deadline"]["source_url"],
            "https://indico.cern.ch/event/1522800/abstracts/",
        )

    def test_merges_same_date_from_multiple_pages_without_conflict(self):
        candidates = [
            {
                "kind": "poster_abstract_deadline",
                "date": "2026-02-16",
                "time": None,
                "source_url": "https://ichep2026.org/important-days.html",
                "confidence": 0.93,
            },
            {
                "kind": "poster_abstract_deadline",
                "date": "2026-02-16",
                "time": None,
                "source_url": "https://indico.cern.ch/event/1522800/abstracts/",
                "confidence": 0.99,
            },
        ]
        result = merge_deadline_candidates(candidates)
        self.assertNotIn("poster_abstract_deadline", result["conflicts"])
        self.assertFalse(result["resolved"]["poster_abstract_deadline"]["conflicting"])


if __name__ == "__main__":
    unittest.main()
