from __future__ import annotations

from urllib.parse import urlparse

HECAP_KEYWORDS = (
    "high energy",
    "particle",
    "partículas",
    "particle physics",
    "hep",
    "hecap",
    "lhc",
    "cern",
    "neutrino",
    "dark matter",
    "astroparticle",
    "astropartícula",
    "gamma ray",
    "raios gama",
    "cosmology",
    "cosmologia",
    "quantum gravity",
    "string",
    "detector",
    "calorim",
    "collider",
    "colis",
)


def normalize_text(value: str) -> str:
    return " ".join((value or "").split()).strip()


def is_hecap_relevant(text: str) -> bool:
    lowered = normalize_text(text).casefold()
    return any(keyword.casefold() in lowered for keyword in HECAP_KEYWORDS)


def is_external_http_url(url: str, source_url: str) -> bool:
    target = urlparse(url)
    source = urlparse(source_url)
    return (
        target.scheme in {"http", "https"}
        and bool(target.netloc)
        and target.netloc != source.netloc
    )


def is_claf_event_detail(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.netloc.endswith("claffisica.org.br") and (
        "/event/" in parsed.path or "/events/event/" in parsed.path
    )
