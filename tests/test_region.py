import sys
import unittest

sys.path.insert(0, "apps/api")

from app.models.domain import EventRegion
from app.services.region import LATIN_AMERICA_COUNTRY_CODES, classify_event_region


class TestEventRegion(unittest.TestCase):
    def test_classifies_brazil_as_latin_america(self):
        self.assertEqual(classify_event_region("BR"), EventRegion.latin_america)

    def test_classifies_mexico_as_latin_america(self):
        self.assertEqual(classify_event_region("mx"), EventRegion.latin_america)

    def test_classifies_france_as_other(self):
        self.assertEqual(classify_event_region("FR"), EventRegion.other)

    def test_unknown_without_country(self):
        self.assertEqual(classify_event_region(None), EventRegion.unknown)

    def test_catalog_has_core_regional_countries(self):
        self.assertTrue({"AR", "BR", "CL", "CO", "MX"}.issubset(LATIN_AMERICA_COUNTRY_CODES))


if __name__ == "__main__":
    unittest.main()
