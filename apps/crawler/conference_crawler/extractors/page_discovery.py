from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse


@dataclass(frozen=True)
class DiscoveredPage:
    url: str
    role: str
    score: int
    anchor_text: str

    def as_dict(self) -> dict[str, str | int]:
        return asdict(self)


_ROLE_RULES: tuple[tuple[str, int, tuple[str, ...]], ...] = (
    (
        "call_for_abstracts",
        100,
        (
            "call for abstracts",
            "call for papers",
            "submit abstract",
            "abstract submission",
            "submissão de resumos",
            "chamada de trabalhos",
            "/abstracts",
        ),
    ),
    (
        "important_dates",
        95,
        (
            "important dates",
            "important days",
            "key dates",
            "deadlines",
            "datas importantes",
            "prazos",
            "important-dates",
            "important-days",
        ),
    ),
    (
        "registration",
        90,
        (
            "registration guidelines",
            "registration fee",
            "registration",
            "register now",
            "inscrição",
            "inscrições",
            "/registrations",
        ),
    ),
    (
        "authors",
        78,
        (
            "for authors",
            "authors",
            "contributors",
            "prepare your contribution",
            "para autores",
        ),
    ),
    (
        "newsletter",
        72,
        (
            "newsletter",
            "bulletin",
            "boletim",
        ),
    ),
    (
        "timetable",
        66,
        (
            "timetable",
            "schedule",
            "agenda",
            "cronograma",
            "/timetable",
        ),
    ),
    (
        "contributions",
        62,
        (
            "contribution list",
            "list of contributions",
            "lista de contribuições",
            "/contributions",
        ),
    ),
    (
        "programme",
        58,
        (
            "scientific programme",
            "scientific program",
            "conference program",
            "conference programme",
            "program",
            "programme",
        ),
    ),
    (
        "proceedings",
        42,
        (
            "proceedings",
            "anais",
        ),
    ),
)

_IGNORED_SCHEMES = {"mailto", "tel", "javascript", "data"}
_TRACKING_QUERY_KEYS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "fbclid",
    "gclid",
}


def normalize_link(url: str) -> str:
    parsed = urlparse(url)
    query = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in _TRACKING_QUERY_KEYS
    ]
    path = re.sub(r"/{2,}", "/", parsed.path or "/")
    if path != "/":
        path = path.rstrip("/")
    return urlunparse(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            parsed.params,
            urlencode(query),
            "",
        )
    )


def classify_event_link(anchor_text: str, href: str, base_url: str) -> DiscoveredPage | None:
    absolute = urljoin(base_url, href or "")
    parsed = urlparse(absolute)
    if parsed.scheme.lower() in _IGNORED_SCHEMES or parsed.scheme.lower() not in {"http", "https"}:
        return None

    normalized_anchor = re.sub(r"\s+", " ", anchor_text or "").strip()
    haystack = f"{normalized_anchor} {parsed.path} {parsed.query}".lower()

    best: tuple[str, int] | None = None
    for role, score, keywords in _ROLE_RULES:
        matches = sum(1 for keyword in keywords if keyword in haystack)
        if not matches:
            continue
        candidate_score = score + min(matches - 1, 3) * 3
        if best is None or candidate_score > best[1]:
            best = (role, candidate_score)

    if best is None:
        return None

    return DiscoveredPage(
        url=normalize_link(absolute),
        role=best[0],
        score=best[1],
        anchor_text=normalized_anchor,
    )


def is_allowed_event_page(
    url: str,
    *,
    root_domains: set[str],
    trusted_domains: set[str] | None = None,
    trusted_path_prefixes: tuple[str, ...] = (),
) -> bool:
    parsed = urlparse(url)
    domain = parsed.netloc.lower().split(":", 1)[0]
    trusted_domains = {item.lower() for item in (trusted_domains or set())}
    root_domains = {item.lower() for item in root_domains}

    if domain in root_domains:
        return True
    if domain not in trusted_domains:
        return False
    if not trusted_path_prefixes:
        return True
    return any(parsed.path.startswith(prefix) for prefix in trusted_path_prefixes)


def rank_and_deduplicate(pages: list[DiscoveredPage], max_pages: int = 20) -> list[DiscoveredPage]:
    by_url: dict[str, DiscoveredPage] = {}
    for page in pages:
        current = by_url.get(page.url)
        if current is None or page.score > current.score:
            by_url[page.url] = page
    return sorted(by_url.values(), key=lambda page: (-page.score, page.url))[:max_pages]
