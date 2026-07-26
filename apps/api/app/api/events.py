from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.domain import (
    CallForPapers,
    Event,
    EventRegion,
    EventStatus,
    RegistrationStatus,
    RegistrationWindow,
    SubmissionStatus,
)
from app.schemas.domain import EventList, EventOut
from app.services.registration_status import compute_registration_status
from app.services.region import LATIN_AMERICA_COUNTRY_CODES
from app.services.status import compute_status

router = APIRouter(prefix="/events", tags=["events"])


def _event_loading_options():
    return (
        selectinload(Event.calls),
        selectinload(Event.registrations),
        selectinload(Event.resources),
    )


@router.get("", response_model=EventList)
def list_events(
    q: str | None = None,
    area: str | None = None,
    country: str | None = None,
    region: EventRegion | None = None,
    submission_status: SubmissionStatus | None = None,
    registration_status: RegistrationStatus | None = None,
    event_status: EventStatus | None = None,
    include_finished: bool = Query(False),
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(Event).options(*_event_loading_options())
    count_stmt = select(func.count(Event.id))
    conditions = []

    if q:
        pattern = f"%{q}%"
        conditions.append(
            or_(
                Event.name.ilike(pattern),
                Event.acronym.ilike(pattern),
                Event.tags.ilike(pattern),
                Event.organizer.ilike(pattern),
            )
        )
    if area:
        conditions.append(Event.area == area)
    if country:
        conditions.append(Event.country_code == country.upper())
    if region == EventRegion.latin_america:
        conditions.append(Event.country_code.in_(tuple(LATIN_AMERICA_COUNTRY_CODES)))
    elif region == EventRegion.other:
        conditions.extend(
            [
                Event.country_code.is_not(None),
                Event.country_code.notin_(tuple(LATIN_AMERICA_COUNTRY_CODES)),
            ]
        )
    elif region == EventRegion.unknown:
        conditions.append(Event.country_code.is_(None))

    today = date.today()
    effective_end = func.coalesce(Event.end_date, Event.start_date)
    if event_status == EventStatus.upcoming:
        conditions.append(Event.start_date > today)
    elif event_status == EventStatus.ongoing:
        conditions.extend(
            [
                Event.start_date.is_not(None),
                Event.start_date <= today,
                effective_end >= today,
            ]
        )
    elif event_status == EventStatus.finished:
        conditions.extend(
            [
                Event.start_date.is_not(None),
                effective_end < today,
            ]
        )
    elif event_status == EventStatus.unknown:
        conditions.append(Event.start_date.is_(None))
    elif not include_finished:
        conditions.append(
            or_(
                Event.start_date.is_(None),
                effective_end >= today,
            )
        )

    if submission_status:
        if submission_status == SubmissionStatus.unknown:
            stmt = stmt.outerjoin(Event.calls)
            count_stmt = count_stmt.outerjoin(Event.calls)
            conditions.append(
                or_(
                    CallForPapers.id.is_(None),
                    CallForPapers.status == SubmissionStatus.unknown,
                )
            )
        else:
            stmt = stmt.join(Event.calls)
            count_stmt = count_stmt.join(Event.calls)
            conditions.append(CallForPapers.status == submission_status)

    if registration_status:
        if registration_status == RegistrationStatus.unknown:
            stmt = stmt.outerjoin(Event.registrations)
            count_stmt = count_stmt.outerjoin(Event.registrations)
            conditions.append(
                or_(
                    RegistrationWindow.id.is_(None),
                    RegistrationWindow.status == RegistrationStatus.unknown,
                )
            )
        else:
            stmt = stmt.join(Event.registrations)
            count_stmt = count_stmt.join(Event.registrations)
            conditions.append(RegistrationWindow.status == registration_status)

    if conditions:
        stmt = stmt.where(*conditions)
        count_stmt = count_stmt.where(*conditions)

    total = db.scalar(count_stmt.with_only_columns(func.count(func.distinct(Event.id)))) or 0
    events = (
        db.scalars(
            stmt.order_by(Event.start_date.asc().nullslast())
            .offset(offset)
            .limit(limit)
        )
        .unique()
        .all()
    )

    now = datetime.now(timezone.utc)
    today = now.date()
    changed = False
    for event in events:
        for call in event.calls:
            computed = compute_status(call, now)
            if call.status != computed and call.status != SubmissionStatus.conflicting:
                call.status = computed
                changed = True
        for registration in event.registrations:
            computed = compute_registration_status(registration, today)
            if registration.status != computed and registration.status != RegistrationStatus.conflicting:
                registration.status = computed
                changed = True
    if changed:
        db.commit()

    return EventList(items=events, total=total)


@router.get("/{slug}", response_model=EventOut)
def get_event(slug: str, db: Session = Depends(get_db)):
    event = db.scalar(
        select(Event)
        .where(Event.slug == slug)
        .options(*_event_loading_options())
    )
    if not event:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return event
