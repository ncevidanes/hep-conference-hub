import re
from datetime import datetime
from typing import Any

from dateutil import parser as date_parser


_MONTH_PATTERN = (
    r"January|February|March|April|May|June|July|August|"
    r"September|October|November|December"
)
_DATE_PATTERN = rf"(?:{_MONTH_PATTERN})\s+\d{{1,2}},\s+\d{{4}}"


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _parse_date(value: str | None) -> str | None:
    if not value:
        return None
    parsed = date_parser.parse(value, fuzzy=True, default=datetime(2000, 1, 1)).date()
    return parsed.isoformat()


def _closed_after(text: str, end: int, distance: int = 35) -> bool:
    return bool(re.search(r"\bclosed\b", text[end : end + distance], re.IGNORECASE))


def extract_opportunity_statuses(raw_text: str) -> dict[str, Any]:
    """Extrai estados de submissão e fases de inscrição de texto visível.

    A função é deliberadamente conservadora: ela só informa ``closed`` quando
    a própria fonte usa a palavra "Closed". Datas ausentes não são inferidas.
    """

    text = normalize_text(raw_text)
    result: dict[str, Any] = {
        "submission_status": "unknown",
        "submission_source_excerpt": None,
        "registrations": [],
    }

    submission_match = re.search(
        r"Abstract\s+Submission\s+is\s+(Closed|Open)",
        text,
        re.IGNORECASE,
    )
    if submission_match:
        result["submission_status"] = submission_match.group(1).lower()
        result["submission_source_excerpt"] = submission_match.group(0)

    opening_match = re.search(
        rf"Registration\s+Opening\s+({_DATE_PATTERN})",
        text,
        re.IGNORECASE,
    )
    registration_opening = _parse_date(opening_match.group(1)) if opening_match else None

    for registration_type, label in (("early", "Early"), ("regular", "Regular")):
        match = re.search(
            rf"{label}\s+Registration\s+Deadline\s+({_DATE_PATTERN})",
            text,
            re.IGNORECASE,
        )
        if not match:
            continue

        closed = _closed_after(text, match.end())
        item = {
            "registration_type": registration_type,
            "title": f"Inscrição {('antecipada' if registration_type == 'early' else 'regular')}",
            "opens_on": registration_opening if registration_type == "early" else None,
            "deadline_on": _parse_date(match.group(1)),
            "status": "closed" if closed else "unknown",
            "source_excerpt": normalize_text(
                text[(opening_match.start() if registration_type == "early" and opening_match else match.start()) : match.end() + (7 if closed else 0)]
            ),
        }
        result["registrations"].append(item)

    return result
