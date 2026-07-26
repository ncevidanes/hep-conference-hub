import re

import scrapy

from conference_crawler.extractors.opportunity_status import extract_opportunity_statuses
from conference_crawler.items.event import EventCandidate


class GenericEventSpider(scrapy.Spider):
    name = "generic_event"

    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not url:
            raise ValueError("Use -a url=https://site-do-event.example")
        self.start_urls = [url]

    def parse(self, response):
        title = response.css("h1::text, title::text").get(default="Evento científico")
        body = " ".join(response.css("body ::text").getall())
        pattern = r"(?:call for (?:papers|abstracts)|submission|important dates).{0,300}"
        match = re.search(pattern, body, re.I)
        opportunities = extract_opportunity_statuses(body)

        yield EventCandidate(
            name=" ".join(title.split()),
            official_url=response.url,
            source_url=response.url,
            deadline_text=match.group(0) if match else None,
            call_type="abstract" if opportunities["submission_status"] != "unknown" else "unknown",
            submission_status=opportunities["submission_status"],
            submission_source_excerpt=opportunities["submission_source_excerpt"],
            registrations=opportunities["registrations"],
            tags=[],
            confidence_score=0.85 if opportunities["registrations"] else (0.6 if match else 0.35),
        )
