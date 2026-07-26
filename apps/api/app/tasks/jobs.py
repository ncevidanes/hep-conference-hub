from datetime import date, datetime, timezone

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.domain import CallForPapers, RegistrationWindow
from app.services.registration_status import compute_registration_status
from app.services.status import compute_status
from app.tasks.celery_app import celery_app


@celery_app.task
def refresh_opportunity_statuses():
    with SessionLocal() as db:
        calls = db.scalars(select(CallForPapers)).all()
        registrations = db.scalars(select(RegistrationWindow)).all()
        changed_submissions = 0
        changed_registrations = 0
        now = datetime.now(timezone.utc)
        today = date.today()

        for call in calls:
            new_status = compute_status(call, now)
            if call.status != new_status:
                call.status = new_status
                changed_submissions += 1

        for registration in registrations:
            new_status = compute_registration_status(registration, today)
            if registration.status != new_status:
                registration.status = new_status
                changed_registrations += 1

        db.commit()
        return {
            "changed_submissions": changed_submissions,
            "changed_registrations": changed_registrations,
        }


# Mantém compatibilidade com o nome da tarefa usado na Prioridade 1.
@celery_app.task
def refresh_submission_statuses():
    return refresh_opportunity_statuses.run()


@celery_app.task
def collect_seed_sources():
    # Ponto de integração dos crawlers. Em produção, dispare Scrapy/Playwright
    # por fonte cadastrada e grave evidências antes de publicar.
    return {"queued_sources": ["CERN Indico", "CERN events", "INSPIRE HEP", "conference series"]}
