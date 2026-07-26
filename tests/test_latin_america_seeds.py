import sys
import unittest

sys.path.insert(0, "apps/api")

from app.data.latin_america_2026 import LATIN_AMERICA_SEEDS


class TestLatinAmericaSeeds(unittest.TestCase):
    def test_has_seven_events(self):
        self.assertEqual(len(LATIN_AMERICA_SEEDS), 7)

    def test_slugs_are_unique(self):
        slugs = [event["slug"] for event in LATIN_AMERICA_SEEDS]
        self.assertEqual(len(slugs), len(set(slugs)))

    def test_all_events_are_tagged_as_latin_america(self):
        for event in LATIN_AMERICA_SEEDS:
            self.assertIn("Latin America", event["tags"])

    def test_all_events_have_auditable_collections(self):
        for event in LATIN_AMERICA_SEEDS:
            self.assertIn("calls", event)
            self.assertIn("registrations", event)
            self.assertIn("resources", event)
            self.assertTrue(event["official_url"].startswith("https://"))
            for resource in event["resources"]:
                self.assertTrue(resource["source_url"].startswith("https://"))
                self.assertGreaterEqual(resource["confidence_score"], 0.9)

    def test_expected_countries_are_covered(self):
        countries = {event["country_code"] for event in LATIN_AMERICA_SEEDS}
        self.assertEqual(countries, {"AR", "BR", "CL", "CO", "MX"})


if __name__ == "__main__":
    unittest.main()
