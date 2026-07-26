from __future__ import annotations

from urllib.parse import urlparse

import scrapy

from conference_crawler.extractors.regional_discovery import (
    is_claf_event_detail,
    is_external_http_url,
    is_hecap_relevant,
    normalize_text,
)
from conference_crawler.items.event import EventCandidate
from conference_crawler.sources.latin_america import LATIN_AMERICA_DISCOVERY_SOURCES


class LatinAmericaDiscoverySpider(scrapy.Spider):
    """Descobre candidatos regionais em LAA-HECAP e na agenda do CLAF.

    Os itens são candidatos de staging: ainda precisam passar pela validação da
    página oficial antes de serem publicados no catálogo.
    """

    name = "latin_america_discovery"
    custom_settings = {
        "ITEM_PIPELINES": {
            "conference_crawler.pipelines.validation.ValidationPipeline": 100,
        },
        "FEEDS": {
            "output/latin_america_candidates.jsonl": {
                "format": "jsonlines",
                "encoding": "utf8",
                "overwrite": True,
            }
        },
    }

    async def start(self):
        for source in LATIN_AMERICA_DISCOVERY_SOURCES:
            yield scrapy.Request(
                source["url"],
                callback=self.parse_source,
                meta={"source_name": source["name"]},
            )

    def parse_source(self, response):
        if "claffisica.org.br" in urlparse(response.url).netloc:
            for href in response.css("a::attr(href)").getall():
                url = response.urljoin(href)
                if is_claf_event_detail(url):
                    yield scrapy.Request(
                        url,
                        callback=self.parse_claf_event,
                        meta={"source_name": response.meta.get("source_name")},
                    )
            return

        # LAA-HECAP publica anúncios com links diretos para páginas oficiais.
        for anchor in response.css("a"):
            href = anchor.attrib.get("href", "")
            url = response.urljoin(href)
            context = normalize_text(
                " ".join(
                    anchor.xpath("ancestor::*[self::li or self::p][1]//text()").getall()
                    or anchor.css("::text").getall()
                )
            )
            if not is_external_http_url(url, response.url) or not is_hecap_relevant(context):
                continue
            name = normalize_text(" ".join(anchor.css("::text").getall())) or context[:180]
            yield EventCandidate(
                name=name,
                official_url=url,
                source_url=response.url,
                tags=["Latin America", "HECAP", "discovered"],
                confidence_score=0.65,
            )

    def parse_claf_event(self, response):
        title = normalize_text(
            response.css("h1::text, h2::text, title::text").get(default="")
        )
        body = normalize_text(" ".join(response.css("body ::text").getall()))
        if not title or not is_hecap_relevant(f"{title} {body}"):
            return

        official_url = response.url
        for href in response.css("a::attr(href)").getall():
            candidate = response.urljoin(href)
            if is_external_http_url(candidate, response.url):
                official_url = candidate
                break

        yield EventCandidate(
            name=title,
            official_url=official_url,
            source_url=response.url,
            tags=["Latin America", "HECAP", "CLAF", "discovered"],
            confidence_score=0.7 if official_url != response.url else 0.55,
        )
