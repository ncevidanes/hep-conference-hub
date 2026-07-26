from __future__ import annotations

from urllib.parse import urlparse

from conference_crawler.extractors.deadline_candidates import extract_deadline_candidates
from conference_crawler.extractors.page_discovery import classify_event_link, rank_and_deduplicate
from conference_crawler.items.event import EventPageObservation


def observe_event_page(
    response,
    *,
    event_key: str,
    name: str,
    acronym: str,
    official_url: str,
    timezone: str,
    trusted_domains: set[str],
    max_pages: int,
):
    """Extrai uma observação e os links internos relevantes de uma página."""

    visible_text = " ".join(response.css("body ::text").getall())
    role = response.meta.get("page_role", "homepage")
    candidates = extract_deadline_candidates(
        visible_text,
        source_url=response.url,
        page_role=role,
        timezone=timezone,
    )

    discovered = []
    for anchor in response.css("a"):
        page = classify_event_link(
            " ".join(anchor.css("::text").getall()),
            anchor.attrib.get("href", ""),
            response.url,
        )
        if page and urlparse(page.url).netloc in trusted_domains:
            discovered.append(page)
    ranked = rank_and_deduplicate(discovered, max_pages)

    observation = EventPageObservation(
        event_key=event_key,
        name=name,
        acronym=acronym,
        official_url=official_url,
        page_url=response.url,
        page_role=role,
        page_title=" ".join(response.css("title ::text").getall()).strip(),
        discovered_from=response.meta.get("discovered_from"),
        timezone=timezone,
        deadline_candidates=candidates,
        opportunity_statuses={},
        outgoing_links=[page.as_dict() for page in ranked],
        confidence_score=0.9 if candidates else 0.7,
    )
    return observation, ranked
