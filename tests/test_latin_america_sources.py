import sys
import unittest
from urllib.parse import urlparse

sys.path.insert(0, "apps/crawler")

from conference_crawler.sources.latin_america import (
    LATIN_AMERICA_DISCOVERY_SOURCES,
    LATIN_AMERICA_EVENT_SOURCES,
)


class TestLatinAmericaSources(unittest.TestCase):
    def test_has_seven_verified_event_sources(self):
        self.assertEqual(len(LATIN_AMERICA_EVENT_SOURCES), 7)

    def test_event_keys_are_unique(self):
        keys = [source["event_key"] for source in LATIN_AMERICA_EVENT_SOURCES]
        self.assertEqual(len(keys), len(set(keys)))

    def test_official_host_is_trusted(self):
        for source in LATIN_AMERICA_EVENT_SOURCES:
            host = urlparse(source["official_url"]).netloc
            self.assertIn(host, source["trusted_domains"])

    def test_all_sources_use_https(self):
        for source in LATIN_AMERICA_EVENT_SOURCES:
            self.assertEqual(urlparse(source["official_url"]).scheme, "https")

    def test_discovery_sources_include_laa_hecap_and_claf(self):
        names = {source["name"] for source in LATIN_AMERICA_DISCOVERY_SOURCES}
        self.assertEqual(names, {"LAA-HECAP", "CLAF Agenda"})


if __name__ == "__main__":
    unittest.main()
