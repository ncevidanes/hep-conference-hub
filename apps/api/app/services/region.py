from __future__ import annotations

from app.models.domain import EventRegion

# Países e territórios normalmente incluídos no recorte latino-americano do portal.
# A classificação é geográfica/editorial e não altera os dados persistidos.
LATIN_AMERICA_COUNTRY_CODES = frozenset(
    {
        "AR",
        "BO",
        "BR",
        "BZ",
        "CL",
        "CO",
        "CR",
        "CU",
        "DO",
        "EC",
        "GT",
        "GY",
        "HN",
        "HT",
        "MX",
        "NI",
        "PA",
        "PE",
        "PR",
        "PY",
        "SV",
        "SR",
        "UY",
        "VE",
    }
)


def classify_event_region(country_code: str | None) -> EventRegion:
    if not country_code:
        return EventRegion.unknown
    if country_code.upper() in LATIN_AMERICA_COUNTRY_CODES:
        return EventRegion.latin_america
    return EventRegion.other
