from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class ValidationPipeline:
    def process_item(self, item, spider):
        data = ItemAdapter(item)
        if data.get("event_key"):
            if not data.get("page_url"):
                raise DropItem("Observação sem URL de página")
            data["confidence_score"] = float(data.get("confidence_score", 0.5))
            data["deadline_candidates"] = list(data.get("deadline_candidates") or [])
            data["outgoing_links"] = list(data.get("outgoing_links") or [])
            return item

        if not data.get("name") or not data.get("source_url"):
            raise DropItem("Evento sem nome ou fonte")

        data["confidence_score"] = float(data.get("confidence_score", 0.5))
        data["registrations"] = list(data.get("registrations") or [])
        data["deadline_candidates"] = list(data.get("deadline_candidates") or [])
        data["source_pages"] = list(data.get("source_pages") or [])
        data["conflicts"] = dict(data.get("conflicts") or {})
        return item
