from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Iterable

from dateutil import parser as date_parser


_MONTHS = (
    "January|February|March|April|May|June|July|August|September|October|November|December|"
    "Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
)
_DATE = rf"(?:{_MONTHS})\s+\d{{1,2}}(?:st|nd|rd|th)?(?:,)?\s+\d{{4}}|\d{{1,2}}\s+(?:{_MONTHS})\s+\d{{4}}"
_TIME = r"\d{1,2}:\d{2}"


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _clean_ordinal(value: str) -> str:
    return re.sub(r"(?<=\d)(st|nd|rd|th)\b", "", value, flags=re.IGNORECASE)


def _parse_date(value: str) -> str:
    parsed = date_parser.parse(_clean_ordinal(value), fuzzy=True, default=datetime(2000, 1, 1))
    return parsed.date().isoformat()


def _candidate(
    *,
    kind: str,
    label: str,
    date_text: str,
    source_url: str,
    source_excerpt: str,
    page_role: str,
    timezone: str | None,
    time_text: str | None = None,
    status: str = "unknown",
    confidence: float = 0.9,
) -> dict[str, Any]:
    return {
        "kind": kind,
        "label": label,
        "date": _parse_date(date_text),
        "time": time_text,
        "timezone": timezone,
        "status": status,
        "source_url": source_url,
        "source_excerpt": normalize_text(source_excerpt),
        "page_role": page_role,
        "confidence": confidence,
    }


def _append_match(
    candidates: list[dict[str, Any]],
    text: str,
    match: re.Match[str] | None,
    *,
    kind: str,
    label: str,
    source_url: str,
    page_role: str,
    timezone: str | None,
    date_group: str = "date",
    time_group: str | None = "time",
    status: str = "unknown",
    confidence: float = 0.9,
) -> None:
    if not match:
        return
    time_text = match.groupdict().get(time_group) if time_group else None
    candidates.append(
        _candidate(
            kind=kind,
            label=label,
            date_text=match.group(date_group),
            time_text=time_text,
            source_url=source_url,
            source_excerpt=match.group(0),
            page_role=page_role,
            timezone=timezone,
            status=status,
            confidence=confidence,
        )
    )


def extract_deadline_candidates(
    raw_text: str,
    *,
    source_url: str,
    page_role: str = "unknown",
    timezone: str | None = None,
) -> list[dict[str, Any]]:
    """Extrai datas explicitamente associadas a submissão ou inscrição.

    A rotina não interpreta datas soltas. Cada candidato precisa estar ligado a
    um rótulo semântico, e sempre mantém URL e trecho de evidência.
    """

    text = normalize_text(raw_text)
    candidates: list[dict[str, Any]] = []

    _append_match(
        candidates,
        text,
        re.search(rf"Opening\s+day\s+(?P<date>{_DATE})(?:,?\s+(?P<time>{_TIME}))?", text, re.I),
        kind="submission_opening",
        label="Abertura da submissão",
        source_url=source_url,
        page_role=page_role,
        timezone=timezone,
        confidence=0.98 if page_role == "call_for_abstracts" else 0.9,
    )
    _append_match(
        candidates,
        text,
        re.search(rf"Submission\s+deadline\s+(?P<date>{_DATE})(?:,?\s+(?P<time>{_TIME}))?", text, re.I),
        kind="abstract_deadline",
        label="Prazo geral de resumos",
        source_url=source_url,
        page_role=page_role,
        timezone=timezone,
        status="closed" if re.search(r"call for abstracts is closed|submission is closed", text, re.I) else "unknown",
        confidence=0.98 if page_role == "call_for_abstracts" else 0.9,
    )

    split_deadline = re.search(
        rf"abstract\s+submission\s+deadline\s+is\s+(?P<talk>{_DATE})\s+for\s+talks?\s+and\s+(?P<poster>{_DATE})\s+for\s+posters?",
        text,
        re.I,
    )
    if split_deadline:
        shared_time = "23:59" if re.search(r"both\s+deadlines?\s+at\s+23:59", text[split_deadline.start(): split_deadline.end() + 120], re.I) else None
        candidates.extend(
            [
                _candidate(
                    kind="talk_abstract_deadline",
                    label="Prazo de resumo para apresentação oral",
                    date_text=split_deadline.group("talk"),
                    time_text=shared_time,
                    source_url=source_url,
                    source_excerpt=split_deadline.group(0),
                    page_role=page_role,
                    timezone=timezone,
                    status="closed",
                    confidence=0.99,
                ),
                _candidate(
                    kind="poster_abstract_deadline",
                    label="Prazo de resumo para pôster",
                    date_text=split_deadline.group("poster"),
                    time_text=shared_time,
                    source_url=source_url,
                    source_excerpt=split_deadline.group(0),
                    page_role=page_role,
                    timezone=timezone,
                    status="closed",
                    confidence=0.99,
                ),
            ]
        )

    for kind, label, prefix in (
        ("talk_abstract_deadline", "Prazo de resumo para apresentação oral", r"Parallel\s+talks?"),
        ("poster_abstract_deadline", "Prazo de resumo para pôster", r"Posters?"),
    ):
        _append_match(
            candidates,
            text,
            re.search(rf"{prefix}\s*:\s*(?P<date>{_DATE})", text, re.I),
            kind=kind,
            label=label,
            source_url=source_url,
            page_role=page_role,
            timezone=timezone,
            status="closed" if re.search(r"abstract submission is closed|call for abstracts is closed", text, re.I) else "unknown",
            confidence=0.93 if page_role == "important_dates" else 0.86,
        )

    _append_match(
        candidates,
        text,
        re.search(rf"Registration\s+Opening\s+(?P<date>{_DATE})", text, re.I),
        kind="registration_opening",
        label="Abertura das inscrições",
        source_url=source_url,
        page_role=page_role,
        timezone=timezone,
        confidence=0.96,
    )

    for kind, label, expression in (
        (
            "early_registration_deadline",
            "Prazo de inscrição antecipada",
            rf"Early\s+(?:Registration\s+Deadline|Fee\s*\(?\s*until)\s+(?P<date>{_DATE})",
        ),
        (
            "regular_registration_deadline",
            "Prazo de inscrição regular",
            rf"Regular\s+(?:Registration\s+Deadline|Fee.*?until)\s+(?P<date>{_DATE})",
        ),
        (
            "onsite_registration_opening",
            "Início da inscrição presencial",
            rf"Onsite\s+Fee\s*\(?\s*after\s+(?P<date>{_DATE})",
        ),
    ):
        match = re.search(expression, text, re.I)
        _append_match(
            candidates,
            text,
            match,
            kind=kind,
            label=label,
            source_url=source_url,
            page_role=page_role,
            timezone=timezone,
            status="closed" if kind.endswith("deadline") and match and re.search(r"closed", text[match.end(): match.end() + 30], re.I) else "unknown",
            confidence=0.96 if page_role == "registration" else 0.9,
        )

    registration_form = re.search(
        rf"Registration\s+is\s+(?P<state>open|closed).*?Deadline\s+(?P<date>{_DATE})",
        text,
        re.I,
    )
    if registration_form:
        candidates.append(
            _candidate(
                kind="registration_deadline",
                label="Prazo do formulário de inscrição",
                date_text=registration_form.group("date"),
                source_url=source_url,
                source_excerpt=registration_form.group(0),
                page_role=page_role,
                timezone=timezone,
                status=registration_form.group("state").lower(),
                confidence=0.99,
            )
        )

    unique: dict[tuple[str, str, str | None, str], dict[str, Any]] = {}
    for candidate in candidates:
        key = (
            candidate["kind"],
            candidate["date"],
            candidate.get("time"),
            candidate["source_url"],
        )
        previous = unique.get(key)
        if previous is None or candidate["confidence"] > previous["confidence"]:
            unique[key] = candidate
    return list(unique.values())


def merge_deadline_candidates(candidates: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Agrupa candidatos sem esconder divergências entre páginas oficiais."""

    grouped: dict[str, list[dict[str, Any]]] = {}
    for candidate in candidates:
        grouped.setdefault(candidate["kind"], []).append(dict(candidate))

    resolved: dict[str, dict[str, Any]] = {}
    conflicts: dict[str, list[dict[str, Any]]] = {}
    for kind, values in grouped.items():
        by_value: dict[tuple[str, str | None], list[dict[str, Any]]] = {}
        for value in values:
            by_value.setdefault((value["date"], value.get("time")), []).append(value)

        ranked = sorted(
            values,
            key=lambda item: (
                float(item.get("confidence", 0.0)),
                1 if "indico.cern.ch" in item.get("source_url", "") else 0,
            ),
            reverse=True,
        )
        winner = dict(ranked[0])
        winner["conflicting"] = len(by_value) > 1
        resolved[kind] = winner
        if len(by_value) > 1:
            conflicts[kind] = sorted(values, key=lambda item: (item["date"], item.get("source_url", "")))

    return {
        "resolved": resolved,
        "conflicts": conflicts,
        "candidates": [dict(item) for item in candidates],
    }
