from __future__ import annotations

from collections import defaultdict

import scrapy

from conference_crawler.extractors.page_observation import observe_event_page
from conference_crawler.sources.latin_america import LATIN_AMERICA_EVENT_SOURCES


class LatinAmericaEventsSpider(scrapy.Spider):
    """Coleta em lote eventos HEP/HECAP latino-americanos verificados."""

    name = "latin_america_events"
    custom_settings = {
        "FEEDS": {
            "output/latin_america_pages.jsonl": {
                "format": "jsonlines",
                "encoding": "utf8",
                "overwrite": True,
            }
        },
        "EVENT_AGGREGATE_OUTPUT": "output/latin_america",
    }

    def __init__(self, max_pages: int = 12, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.visited_urls: dict[str, set[str]] = defaultdict(set)

    async def start(self):
        for source in LATIN_AMERICA_EVENT_SOURCES:
            yield scrapy.Request(
                source["official_url"],
                callback=self.parse_event_page,
                meta={"event_source": source, "page_role": "homepage"},
            )

    def parse_event_page(self, response):
        source = response.meta["event_source"]
        event_key = source["event_key"]
        visited = self.visited_urls[event_key]
        visited.add(response.url.rstrip("/"))

        observation, ranked = observe_event_page(
            response,
            event_key=event_key,
            name=source["name"],
            acronym=source["acronym"],
            official_url=source["official_url"],
            timezone=source["timezone"],
            trusted_domains=set(source["trusted_domains"]),
            max_pages=self.max_pages,
        )
        yield observation

        for page in ranked:
            normalized = page.url.rstrip("/")
            if normalized in visited or len(visited) >= self.max_pages:
                continue
            visited.add(normalized)
            yield scrapy.Request(
                page.url,
                callback=self.parse_event_page,
                meta={
                    "event_source": source,
                    "page_role": page.role,
                    "discovered_from": response.url,
                },
            )
