from __future__ import annotations

import scrapy

from conference_crawler.extractors.deadline_candidates import extract_deadline_candidates
from conference_crawler.extractors.opportunity_status import extract_opportunity_statuses
from conference_crawler.extractors.page_discovery import (
    classify_event_link,
    is_allowed_event_page,
    rank_and_deduplicate,
)
from conference_crawler.items.event import EventPageObservation


class Ichep2026Spider(scrapy.Spider):
    name = "ichep_2026"
    allowed_domains = ["ichep2026.org", "indico.cern.ch"]

    official_url = "https://ichep2026.org/"
    indico_root = "https://indico.cern.ch/event/1522800"
    timezone = "America/Sao_Paulo"
    max_pages = 20

    def start_requests(self):
        seeds = (
            (self.official_url, "homepage"),
            (f"{self.indico_root}/overview", "overview"),
            (f"{self.indico_root}/abstracts", "call_for_abstracts"),
            (f"{self.indico_root}/registrations/121108", "registration"),
            (f"{self.indico_root}/program", "programme"),
            (f"{self.indico_root}/timetable", "timetable"),
        )
        self.visited_urls: set[str] = set()
        for url, role in seeds:
            self.visited_urls.add(url.rstrip("/"))
            yield scrapy.Request(url, callback=self.parse_page, meta={"page_role": role, "discovered_from": None})

    def parse_page(self, response):
        role = response.meta.get("page_role", "unknown")
        visible_text = " ".join(response.css("body ::text").getall())
        title = " ".join(response.css("title ::text").getall()).strip()
        candidates = extract_deadline_candidates(
            visible_text,
            source_url=response.url,
            page_role=role,
            timezone=self.timezone,
        )
        opportunities = extract_opportunity_statuses(visible_text)

        discovered = []
        for anchor in response.css("a"):
            href = anchor.attrib.get("href", "")
            anchor_text = " ".join(anchor.css("::text").getall())
            page = classify_event_link(anchor_text, href, response.url)
            if not page:
                continue
            if not is_allowed_event_page(
                page.url,
                root_domains={"ichep2026.org"},
                trusted_domains={"indico.cern.ch"},
                trusted_path_prefixes=("/event/1522800",),
            ):
                continue
            discovered.append(page)

        ranked = rank_and_deduplicate(discovered, self.max_pages)
        outgoing_links = [page.as_dict() for page in ranked]

        yield EventPageObservation(
            event_key="ichep-2026",
            name="43rd International Conference on High Energy Physics",
            acronym="ICHEP 2026",
            official_url=self.official_url,
            page_url=response.url,
            page_role=role,
            page_title=title,
            discovered_from=response.meta.get("discovered_from"),
            timezone=self.timezone,
            deadline_candidates=candidates,
            opportunity_statuses=opportunities,
            outgoing_links=outgoing_links,
            confidence_score=1.0 if candidates else 0.85,
        )

        for page in ranked:
            normalized = page.url.rstrip("/")
            if normalized in self.visited_urls or len(self.visited_urls) >= self.max_pages:
                continue
            self.visited_urls.add(normalized)
            yield scrapy.Request(
                page.url,
                callback=self.parse_page,
                meta={"page_role": page.role, "discovered_from": response.url},
            )
