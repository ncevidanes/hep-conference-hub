BOT_NAME = "hep_conference_hub"
SPIDER_MODULES = ["conference_crawler.spiders"]
NEWSPIDER_MODULE = "conference_crawler.spiders"
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS_PER_DOMAIN = 2
DOWNLOAD_DELAY = 1.5
AUTOTHROTTLE_ENABLED = True
HTTPCACHE_ENABLED = True
DEPTH_LIMIT = 2
USER_AGENT = "HEPConferenceHubBot/0.1 (+contact@example.org)"
ITEM_PIPELINES = {
    "conference_crawler.pipelines.validation.ValidationPipeline": 100,
    "conference_crawler.pipelines.aggregation.EventPageAggregationPipeline": 200,
}
FEEDS = {"output/pages.jsonl": {"format": "jsonlines", "encoding": "utf8", "overwrite": True}}
EVENT_AGGREGATE_OUTPUT = "output"
