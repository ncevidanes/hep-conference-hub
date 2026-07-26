.PHONY: up down logs seed crawl crawl-latam crawl-latam-discovery test
up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

seed:
	docker compose exec api python -m app.seed

crawl:
	cd apps/crawler && scrapy crawl cern_indico

crawl-latam:
	cd apps/crawler && scrapy crawl latin_america_events

crawl-latam-discovery:
	cd apps/crawler && scrapy crawl latin_america_discovery

test:
	python -m unittest discover -s tests
