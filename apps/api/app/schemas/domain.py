from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.domain import (
    ConfidenceLevel,
    EventRegion,
    EventStatus,
    RegistrationStatus,
    ResourceRole,
    SubmissionStatus,
    VerificationFreshness,
)


class CallOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    call_type: str
    title: str | None
    submission_url: str | None
    opens_at: datetime | None
    deadline_at: datetime | None
    extended_deadline_at: datetime | None
    timezone: str | None
    status: SubmissionStatus
    source_url: str
    source_excerpt: str | None
    confidence_score: float
    confidence_level: ConfidenceLevel
    last_verified_at: datetime | None
    verification_freshness: VerificationFreshness


class RegistrationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    registration_type: str
    title: str | None
    registration_url: str | None
    opens_on: date | None
    deadline_on: date | None
    timezone: str | None
    status: RegistrationStatus
    source_url: str
    source_excerpt: str | None
    confidence_score: float
    confidence_level: ConfidenceLevel
    last_verified_at: datetime | None
    verification_freshness: VerificationFreshness


class ResourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: ResourceRole
    label: str
    url: str
    is_primary: bool
    source_url: str
    source_excerpt: str | None
    confidence_score: float
    confidence_level: ConfidenceLevel
    last_verified_at: datetime | None
    verification_freshness: VerificationFreshness


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    acronym: str | None
    slug: str
    description: str | None
    area: str
    tags: str
    organizer: str | None
    institution: str | None
    country_code: str | None
    city: str | None
    format: str | None
    start_date: date | None
    end_date: date | None
    official_url: str
    source_type: str
    confidence_score: float
    confidence_level: ConfidenceLevel
    verified: bool
    last_verified_at: datetime | None
    verification_freshness: VerificationFreshness
    region: EventRegion
    event_status: EventStatus
    calls: list[CallOut] = Field(default_factory=list)
    registrations: list[RegistrationOut] = Field(default_factory=list)
    resources: list[ResourceOut] = Field(default_factory=list)


class EventList(BaseModel):
    items: list[EventOut]
    total: int


class SubscriberCreate(BaseModel):
    email: EmailStr
    areas: list[str] = Field(default_factory=lambda: ["high-energy-physics", "CERN", "particle-collisions"])
    frequency: str = "weekly"


class SubscriberOut(BaseModel):
    id: UUID
    email: EmailStr
    confirmed: bool
    message: str
