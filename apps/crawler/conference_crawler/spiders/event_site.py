from __future__ import annotations

from urllib.parse import urlparse

import scrapy

from conference_crawler.extractors.page_observation import observe_event_page


class EventSiteSpider(scrapy.Spider):
    """Coletor genérico para páginas internas de um único domínio oficial.

    Exemplo:
      scrapy crawl event_site -a url=https://evento.org -a event_key=evento-2027 -a name="Evento 2027"
    """

    name = "event_site"

    def __init__(
        self,
        url: str,
        event_key: str,
        name: str,
        acronym: str = "",
        timezone: str = "UTC",
        max_pages: int = 12,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.start_urls = [url]
        self.official_url = url
        self.event_key = event_key
        self.event_name = name
        self.acronym = acronym
        self.timezone = timezone
        self.max_pages = int(max_pages)
        self.allowed_domains = [urlparse(url).netloc]
        self.visited_urls: set[str] = set()

    def parse(self, response):
        self.visited_urls.add(response.url.rstrip("/"))
        observation, ranked = observe_event_page(
            response,
            event_key=self.event_key,
            name=self.event_name,
            acronym=self.acronym,
            official_url=self.official_url,
            timezone=self.timezone,
            trusted_domains=set(self.allowed_domains),
            max_pages=self.max_pages,
        )
        yield observation

        for page in ranked:
            normalized = page.url.rstrip("/")
            if normalized in self.visited_urls or len(self.visited_urls) >= self.max_pages:
                continue
            self.visited_urls.add(normalized)
            yield scrapy.Request(
                page.url,
                callback=self.parse,
                meta={"page_role": page.role, "discovered_from": response.url},
            )
