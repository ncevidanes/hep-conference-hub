import re

import scrapy

from conference_crawler.extractors.opportunity_status import extract_opportunity_statuses
from conference_crawler.items.event import EventCandidate


class CernIndicoSpider(scrapy.Spider):
    name = "cern_indico"
    allowed_domains = ["indico.cern.ch"]
    start_urls = ["https://indico.cern.ch/category/1/"]

    def parse(self, response):
        for link in response.css('a[href*="/event/"]::attr(href)').getall():
            yield response.follow(link, callback=self.parse_event)

    def parse_event(self, response):
        title = response.css("h1::text, .conference-title::text, .event-title::text").get()
        if not title:
            return

        text = " ".join(response.css("body ::text").getall())
        keywords = [
            "high energy",
            "particle",
            "collision",
            "atlas",
            "cms",
            "alice",
            "lhcb",
            "calorimeter",
            "cern",
        ]
        if not any(keyword in text.lower() for keyword in keywords):
            return

        deadline_match = re.search(
            r"(?:abstract|paper|submission).{0,80}(?:deadline|closes?).{0,80}",
            text,
            re.I,
        )
        opportunities = extract_opportunity_statuses(text)
        registration_link = response.css('a[href*="/registrations/"]::attr(href)').get()
        submission_link = response.css('a[href*="/abstracts/"]::attr(href)').get()

        yield EventCandidate(
            name=" ".join(title.split()),
            official_url=response.url,
            source_url=response.url,
            deadline_text=deadline_match.group(0) if deadline_match else None,
            call_type="abstract" if "abstract" in text.lower() else "unknown",
            submission_url=response.urljoin(submission_link) if submission_link else None,
            submission_status=opportunities["submission_status"],
            submission_source_excerpt=opportunities["submission_source_excerpt"],
            registration_url=response.urljoin(registration_link) if registration_link else None,
            registrations=opportunities["registrations"],
            tags=[keyword for keyword in keywords if keyword in text.lower()],
            confidence_score=0.85 if opportunities["registrations"] else (0.75 if deadline_match else 0.55),
        )
