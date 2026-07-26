import sys
import unittest

sys.path.insert(0, "apps/crawler")

from conference_crawler.extractors.regional_discovery import (
    is_claf_event_detail,
    is_external_http_url,
    is_hecap_relevant,
    normalize_text,
)


class TestRegionalDiscovery(unittest.TestCase):
    def test_detects_hecap_topics_in_multiple_languages(self):
        self.assertTrue(is_hecap_relevant("Latin American Symposium on High Energy Physics"))
        self.assertTrue(is_hecap_relevant("Física de partículas e detectores"))
        self.assertTrue(is_hecap_relevant("Astroparticle physics and gamma rays"))

    def test_rejects_unrelated_topic(self):
        self.assertFalse(is_hecap_relevant("Conference on soft matter and polymers"))

    def test_identifies_claf_detail_pages(self):
        self.assertTrue(
            is_claf_event_detail(
                "https://claffisica.org.br/event/advances-in-quantum-gravity-strings"
            )
        )
        self.assertFalse(is_claf_event_detail("https://claffisica.org.br/events/list"))

    def test_external_url_detection(self):
        source = "https://www.laa-hecap.org/"
        self.assertTrue(is_external_http_url("https://fisindico.uniandes.edu.co/event/18/", source))
        self.assertFalse(is_external_http_url("https://www.laa-hecap.org/about", source))

    def test_normalizes_whitespace(self):
        self.assertEqual(normalize_text("  High\n Energy   Physics "), "High Energy Physics")


if __name__ == "__main__":
    unittest.main()
