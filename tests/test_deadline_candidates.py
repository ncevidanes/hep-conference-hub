import sys
import unittest

sys.path.insert(0, "apps/crawler")

from conference_crawler.extractors.deadline_candidates import extract_deadline_candidates


INDICO_ABSTRACTS = """
Opening day 1 Dec 2025, 08:00
Submission deadline 16 Feb 2026, 23:59
The abstract submission deadline is February 9th, 2026 for talks and
February 16th, 2026 for posters (both deadlines at 23:59 BRT).
The call for abstracts is closed.
"""

REGISTRATION_GUIDELINES = """
EARLY FEE (until May 15, 2026)
REGULAR FEE (from May 16 until July 23, 2026)
ONSITE FEE (after July 24, 2026)
"""

REGISTRATION_FORM = """
Registration is open
Deadline 30 Jul 2026
"""


class TestDeadlineCandidates(unittest.TestCase):
    def by_kind(self, candidates):
        return {item["kind"]: item for item in candidates}

    def test_extracts_split_abstract_deadlines(self):
        values = self.by_kind(
            extract_deadline_candidates(
                INDICO_ABSTRACTS,
                source_url="https://indico.cern.ch/event/1522800/abstracts/",
                page_role="call_for_abstracts",
                timezone="America/Sao_Paulo",
            )
        )
        self.assertEqual(values["submission_opening"]["date"], "2025-12-01")
        self.assertEqual(values["talk_abstract_deadline"]["date"], "2026-02-09")
        self.assertEqual(values["poster_abstract_deadline"]["date"], "2026-02-16")
        self.assertEqual(values["talk_abstract_deadline"]["time"], "23:59")
        self.assertEqual(values["talk_abstract_deadline"]["status"], "closed")

    def test_extracts_registration_phases(self):
        values = self.by_kind(
            extract_deadline_candidates(
                REGISTRATION_GUIDELINES,
                source_url="https://ichep2026.org/registration-guidelines.html",
                page_role="registration",
                timezone="America/Sao_Paulo",
            )
        )
        self.assertEqual(values["early_registration_deadline"]["date"], "2026-05-15")
        self.assertEqual(values["regular_registration_deadline"]["date"], "2026-07-23")
        self.assertEqual(values["onsite_registration_opening"]["date"], "2026-07-24")

    def test_extracts_registration_form_deadline(self):
        values = self.by_kind(
            extract_deadline_candidates(
                REGISTRATION_FORM,
                source_url="https://indico.cern.ch/event/1522800/registrations/121108/",
                page_role="registration",
                timezone="America/Sao_Paulo",
            )
        )
        self.assertEqual(values["registration_deadline"]["date"], "2026-07-30")
        self.assertEqual(values["registration_deadline"]["status"], "open")

    def test_ignores_unlabelled_dates(self):
        self.assertEqual(
            extract_deadline_candidates(
                "The conference is held from July 30 to August 5, 2026.",
                source_url="https://ichep2026.org/",
                page_role="homepage",
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
