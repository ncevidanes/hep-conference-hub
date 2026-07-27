import unittest

from app.core.config import normalize_database_url


class TestRenderDatabaseUrl(unittest.TestCase):
    def test_render_postgresql_url_uses_psycopg(self):
        self.assertEqual(
            normalize_database_url("postgresql://user:secret@host:5432/database"),
            "postgresql+psycopg://user:secret@host:5432/database",
        )

    def test_legacy_postgres_url_uses_psycopg(self):
        self.assertEqual(
            normalize_database_url("postgres://user:secret@host:5432/database"),
            "postgresql+psycopg://user:secret@host:5432/database",
        )

    def test_existing_driver_is_preserved(self):
        url = "postgresql+psycopg://user:secret@host:5432/database"
        self.assertEqual(normalize_database_url(url), url)

    def test_sqlite_url_is_preserved(self):
        url = "sqlite:///./conference_hub.db"
        self.assertEqual(normalize_database_url(url), url)


if __name__ == "__main__":
    unittest.main()
