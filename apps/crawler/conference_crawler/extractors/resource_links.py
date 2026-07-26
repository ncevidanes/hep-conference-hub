from __future__ import annotations

from urllib.parse import urlparse

_RESOURCE_ROLE_MAP = {
    "call_for_abstracts": "submission",
    "registration": "registration",
    "programme": "programme",
    "timetable": "timetable",
    "contributions": "contributions",
    "proceedings": "proceedings",
    "important_dates": "important_dates",
    "authors": "authors",
}

_DEFAULT_LABELS = {
    "submission": "Chamada de trabalhos",
    "registration": "Inscrição",
    "programme": "Programa científico",
    "timetable": "Cronograma",
    "contributions": "Lista de contribuições",
    "proceedings": "Proceedings",
    "important_dates": "Datas importantes",
    "authors": "Informações para autores",
}

_RESOURCE_ORDER = {
    "submission": 10,
    "registration": 20,
    "programme": 30,
    "timetable": 40,
    "contributions": 50,
    "proceedings": 60,
    "important_dates": 70,
    "authors": 80,
}


def resource_role_for_page(page_role: str | None) -> str | None:
    return _RESOURCE_ROLE_MAP.get(page_role or "")


def _clean_title(title: str | None, role: str) -> str:
    value = " ".join((title or "").split()).strip()
    if not value or len(value) > 100:
        return _DEFAULT_LABELS[role]
    lower = value.lower()
    if lower in {"home", "overview", "event", "indico"}:
        return _DEFAULT_LABELS[role]
    return value


def build_event_resources(pages: list[dict]) -> list[dict]:
    """Transforma páginas descobertas em links funcionais auditáveis.

    A primeira URL de cada função, depois da ordenação por confiança, é marcada
    como primária. Outras URLs da mesma função continuam disponíveis para
    auditoria e para eventos que mantêm páginas distintas por público.
    """

    candidates: dict[tuple[str, str], dict] = {}
    for page in pages:
        role = resource_role_for_page(page.get("page_role"))
        url = page.get("page_url")
        if not role or not url:
            continue
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            continue
        confidence = float(page.get("confidence_score") or 0.5)
        item = {
            "role": role,
            "label": _clean_title(page.get("page_title"), role),
            "url": url,
            "source_url": page.get("discovered_from") or url,
            "confidence_score": confidence,
            "is_primary": False,
        }
        key = (role, url)
        current = candidates.get(key)
        if current is None or confidence > current["confidence_score"]:
            candidates[key] = item

    resources = sorted(
        candidates.values(),
        key=lambda item: (
            _RESOURCE_ORDER.get(item["role"], 999),
            -item["confidence_score"],
            item["url"],
        ),
    )
    primary_roles: set[str] = set()
    for resource in resources:
        if resource["role"] not in primary_roles:
            resource["is_primary"] = True
            primary_roles.add(resource["role"])
    return resources
