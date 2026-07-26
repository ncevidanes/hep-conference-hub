from __future__ import annotations

import json
from pathlib import Path

from itemadapter import ItemAdapter

from conference_crawler.extractors.deadline_candidates import merge_deadline_candidates
from conference_crawler.extractors.resource_links import build_event_resources


class EventPageAggregationPipeline:
    """Consolida observações de páginas em um arquivo auditável por evento."""

    def open_spider(self, spider):
        self.events: dict[str, dict] = {}

    def process_item(self, item, spider):
        data = ItemAdapter(item).asdict()
        event_key = data.get("event_key")
        page_url = data.get("page_url")
        if not event_key or not page_url:
            return item

        aggregate = self.events.setdefault(
            event_key,
            {
                "event_key": event_key,
                "name": data.get("name"),
                "acronym": data.get("acronym"),
                "official_url": data.get("official_url"),
                "pages": [],
                "deadline_candidates": [],
            },
        )
        if not any(page["page_url"] == page_url for page in aggregate["pages"]):
            aggregate["pages"].append(
                {
                    "page_url": page_url,
                    "page_role": data.get("page_role"),
                    "page_title": data.get("page_title"),
                    "discovered_from": data.get("discovered_from"),
                    "confidence_score": data.get("confidence_score"),
                }
            )
        aggregate["deadline_candidates"].extend(data.get("deadline_candidates") or [])
        return item

    def close_spider(self, spider):
        output_dir = Path(spider.settings.get("EVENT_AGGREGATE_OUTPUT", "output"))
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "events_aggregated.json"

        payload = []
        for aggregate in self.events.values():
            merge = merge_deadline_candidates(aggregate.pop("deadline_candidates"))
            aggregate.update(merge)
            aggregate["resources"] = build_event_resources(aggregate["pages"])
            aggregate["pages"].sort(key=lambda page: (page.get("page_role") or "", page["page_url"]))
            payload.append(aggregate)

        payload.sort(key=lambda event: event["event_key"])
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
