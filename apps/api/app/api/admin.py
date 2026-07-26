from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.domain import (
    CallForPapers,
    Event,
    RegistrationStatus,
    RegistrationWindow,
    SubmissionStatus,
    Subscriber,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    stale_before = datetime.now(timezone.utc) - timedelta(days=30)
    return {
        "events": db.scalar(select(func.count(Event.id))) or 0,
        "open_calls": db.scalar(
            select(func.count(CallForPapers.id)).where(CallForPapers.status.in_([SubmissionStatus.open, SubmissionStatus.extended]))
        )
        or 0,
        "open_registrations": db.scalar(
            select(func.count(RegistrationWindow.id)).where(RegistrationWindow.status == RegistrationStatus.open)
        )
        or 0,
        "subscribers": db.scalar(
            select(func.count(Subscriber.id)).where(Subscriber.active.is_(True))
        )
        or 0,
        "needs_review": db.scalar(
            select(func.count(Event.id)).where(Event.confidence_score < 0.8)
        )
        or 0,
        "stale_verifications": db.scalar(
            select(func.count(Event.id)).where(
                (Event.last_verified_at.is_(None)) | (Event.last_verified_at < stale_before)
            )
        )
        or 0,
        "verified_events": db.scalar(
            select(func.count(Event.id)).where(Event.verified.is_(True))
        )
        or 0,
    }
