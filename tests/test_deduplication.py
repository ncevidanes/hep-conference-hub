import sys, unittest
sys.path.insert(0, "apps/api")
from app.services.deduplication import likely_duplicate

class TestDeduplication(unittest.TestCase):
    def test_acronym(self):
        self.assertTrue(likely_duplicate("International Conference on High Energy Physics", "ICHEP Conference", "ICHEP", "ICHEP"))
    def test_distinct(self):
        self.assertFalse(likely_duplicate("CALOR", "Quark Matter", None, None))

if __name__ == "__main__": unittest.main()
