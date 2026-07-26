from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "conference_hub",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.jobs"],
)
celery_app.conf.beat_schedule = {
    "refresh-opportunity-statuses-every-hour": {
        "task": "app.tasks.jobs.refresh_opportunity_statuses",
        "schedule": 3600.0,
    },
    "collect-indico-every-six-hours": {
        "task": "app.tasks.jobs.collect_seed_sources",
        "schedule": 21600.0,
    },
}
celery_app.conf.timezone = "UTC"
