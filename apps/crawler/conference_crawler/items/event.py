import scrapy


class EventCandidate(scrapy.Item):
    name = scrapy.Field()
    acronym = scrapy.Field()
    slug = scrapy.Field()
    official_url = scrapy.Field()
    source_url = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()

    submission_url = scrapy.Field()
    submission_status = scrapy.Field()
    submission_source_excerpt = scrapy.Field()
    deadline_text = scrapy.Field()
    call_type = scrapy.Field()

    registration_url = scrapy.Field()
    registrations = scrapy.Field()

    deadline_candidates = scrapy.Field()
    source_pages = scrapy.Field()
    conflicts = scrapy.Field()
    tags = scrapy.Field()
    confidence_score = scrapy.Field()


class EventPageObservation(scrapy.Item):
    """Observação de uma página interna pertencente ao mesmo evento."""

    event_key = scrapy.Field()
    name = scrapy.Field()
    acronym = scrapy.Field()
    official_url = scrapy.Field()
    page_url = scrapy.Field()
    page_role = scrapy.Field()
    page_title = scrapy.Field()
    discovered_from = scrapy.Field()
    timezone = scrapy.Field()
    deadline_candidates = scrapy.Field()
    opportunity_statuses = scrapy.Field()
    outgoing_links = scrapy.Field()
    confidence_score = scrapy.Field()
