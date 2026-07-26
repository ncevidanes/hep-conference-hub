import sys
import unittest

sys.path.insert(0, "apps/crawler")

from conference_crawler.extractors.page_discovery import (
    classify_event_link,
    is_allowed_event_page,
    rank_and_deduplicate,
)


class TestPageDiscovery(unittest.TestCase):
    def test_classifies_internal_deadline_pages(self):
        page = classify_event_link(
            "Important Dates",
            "/important-days.html",
            "https://ichep2026.org/",
        )
        self.assertIsNotNone(page)
        self.assertEqual(page.role, "important_dates")
        self.assertEqual(page.url, "https://ichep2026.org/important-days.html")

    def test_classifies_indico_abstract_page(self):
        page = classify_event_link(
            "Call for Abstracts",
            "https://indico.cern.ch/event/1522800/abstracts/",
            "https://ichep2026.org/",
        )
        self.assertEqual(page.role, "call_for_abstracts")

    def test_distinguishes_timetable_from_programme(self):
        timetable = classify_event_link(
            "Timetable",
            "/event/1522800/timetable/",
            "https://indico.cern.ch/",
        )
        programme = classify_event_link(
            "Scientific Programme",
            "/event/1522800/program",
            "https://indico.cern.ch/",
        )
        self.assertEqual(timetable.role, "timetable")
        self.assertEqual(programme.role, "programme")

    def test_classifies_contribution_list(self):
        page = classify_event_link(
            "Contribution List",
            "/event/1522800/contributions/",
            "https://indico.cern.ch/",
        )
        self.assertEqual(page.role, "contributions")

    def test_rejects_irrelevant_link(self):
        self.assertIsNone(
            classify_event_link("Contact", "/contacts.html", "https://ichep2026.org/")
        )

    def test_restricts_trusted_indico_to_event_prefix(self):
        self.assertTrue(
            is_allowed_event_page(
                "https://indico.cern.ch/event/1522800/abstracts",
                root_domains={"ichep2026.org"},
                trusted_domains={"indico.cern.ch"},
                trusted_path_prefixes=("/event/1522800",),
            )
        )
        self.assertFalse(
            is_allowed_event_page(
                "https://indico.cern.ch/event/999999/abstracts",
                root_domains={"ichep2026.org"},
                trusted_domains={"indico.cern.ch"},
                trusted_path_prefixes=("/event/1522800",),
            )
        )

    def test_keeps_highest_scoring_duplicate(self):
        weak = classify_event_link("Registration", "/registration-guidelines.html", "https://ichep2026.org/")
        strong = classify_event_link("Registration Guidelines", "/registration-guidelines.html", "https://ichep2026.org/")
        result = rank_and_deduplicate([weak, strong])
        self.assertEqual(len(result), 1)
        self.assertGreaterEqual(result[0].score, weak.score)


if __name__ == "__main__":
    unittest.main()
