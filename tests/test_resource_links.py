import sys
import unittest

sys.path.insert(0, "apps/crawler")

from conference_crawler.extractors.resource_links import (
    build_event_resources,
    resource_role_for_page,
)


class TestResourceLinks(unittest.TestCase):
    def test_maps_page_roles_to_resource_roles(self):
        self.assertEqual(resource_role_for_page("call_for_abstracts"), "submission")
        self.assertEqual(resource_role_for_page("registration"), "registration")
        self.assertEqual(resource_role_for_page("timetable"), "timetable")
        self.assertEqual(resource_role_for_page("proceedings"), "proceedings")

    def test_ignores_non_actionable_pages(self):
        self.assertIsNone(resource_role_for_page("homepage"))
        self.assertIsNone(resource_role_for_page("newsletter"))

    def test_builds_ordered_resources(self):
        pages = [
            {
                "page_url": "https://example.org/proceedings",
                "page_role": "proceedings",
                "page_title": "Proceedings",
                "confidence_score": 0.9,
            },
            {
                "page_url": "https://example.org/abstracts",
                "page_role": "call_for_abstracts",
                "page_title": "Call for Abstracts",
                "confidence_score": 0.95,
            },
            {
                "page_url": "https://example.org/timetable",
                "page_role": "timetable",
                "page_title": "Timetable",
                "confidence_score": 0.9,
            },
        ]
        resources = build_event_resources(pages)
        self.assertEqual(
            [resource["role"] for resource in resources],
            ["submission", "timetable", "proceedings"],
        )

    def test_deduplicates_and_marks_primary(self):
        pages = [
            {
                "page_url": "https://example.org/program",
                "page_role": "programme",
                "page_title": "Scientific Programme",
                "confidence_score": 0.8,
            },
            {
                "page_url": "https://example.org/program",
                "page_role": "programme",
                "page_title": "Scientific Programme",
                "confidence_score": 0.99,
            },
            {
                "page_url": "https://example.org/program-alt",
                "page_role": "programme",
                "page_title": "Programme overview",
                "confidence_score": 0.7,
            },
        ]
        resources = build_event_resources(pages)
        self.assertEqual(len(resources), 2)
        self.assertTrue(resources[0]["is_primary"])
        self.assertFalse(resources[1]["is_primary"])
        self.assertEqual(resources[0]["confidence_score"], 0.99)

    def test_uses_default_label_for_empty_title(self):
        resources = build_event_resources(
            [
                {
                    "page_url": "https://example.org/registrations",
                    "page_role": "registration",
                    "page_title": "",
                    "confidence_score": 1.0,
                }
            ]
        )
        self.assertEqual(resources[0]["label"], "Inscrição")


if __name__ == "__main__":
    unittest.main()
