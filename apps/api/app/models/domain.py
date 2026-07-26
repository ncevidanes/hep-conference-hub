import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ConfidenceLevel(str, enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"
    unknown = "unknown"


class VerificationFreshness(str, enum.Enum):
    current = "current"
    aging = "aging"
    stale = "stale"
    unknown = "unknown"


class VerificationMixin:
    confidence_score: float
    last_verified_at: datetime | None

    @property
    def confidence_level(self) -> ConfidenceLevel:
        from app.services.verification import classify_confidence

        return classify_confidence(self.confidence_score)

    @property
    def verification_freshness(self) -> VerificationFreshness:
        from app.services.verification import classify_verification_freshness

        return classify_verification_freshness(self.last_verified_at)


class EventRegion(str, enum.Enum):
    latin_america = "latin-america"
    other = "other"
    unknown = "unknown"


class EventStatus(str, enum.Enum):
    upcoming = "upcoming"
    ongoing = "ongoing"
    finished = "finished"
    unknown = "unknown"


class SubmissionStatus(str, enum.Enum):
    upcoming = "upcoming"
    open = "open"
    extended = "extended"
    closed = "closed"
    rolling = "rolling"
    unknown = "unknown"
    conflicting = "conflicting"


class ResourceRole(str, enum.Enum):
    submission = "submission"
    registration = "registration"
    programme = "programme"
    timetable = "timetable"
    contributions = "contributions"
    proceedings = "proceedings"
    important_dates = "important_dates"
    authors = "authors"
    payment = "payment"
    other = "other"


class RegistrationStatus(str, enum.Enum):
    not_announced = "not_announced"
    upcoming = "upcoming"
    open = "open"
    closed = "closed"
    unknown = "unknown"
    conflicting = "conflicting"


class Event(VerificationMixin, Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(500), index=True)
    acronym: Mapped[str | None] = mapped_column(String(80), index=True)
    slug: Mapped[str] = mapped_column(String(600), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    area: Mapped[str] = mapped_column(String(120), default="high-energy-physics", index=True)
    tags: Mapped[str] = mapped_column(Text, default="")
    organizer: Mapped[str | None] = mapped_column(String(300), index=True)
    institution: Mapped[str | None] = mapped_column(String(300))
    country_code: Mapped[str | None] = mapped_column(String(2), index=True)
    city: Mapped[str | None] = mapped_column(String(150))
    format: Mapped[str | None] = mapped_column(String(30), index=True)
    start_date: Mapped[date | None] = mapped_column(Date, index=True)
    end_date: Mapped[date | None] = mapped_column(Date)
    official_url: Mapped[str] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(String(50), default="manual")
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    calls: Mapped[list["CallForPapers"]] = relationship(
        back_populates="event",
        cascade="all, delete-orphan",
    )
    registrations: Mapped[list["RegistrationWindow"]] = relationship(
        back_populates="event",
        cascade="all, delete-orphan",
    )
    resources: Mapped[list["EventResource"]] = relationship(
        back_populates="event",
        cascade="all, delete-orphan",
    )

    @property
    def region(self) -> EventRegion:
        from app.services.region import classify_event_region

        return classify_event_region(self.country_code)

    @property
    def event_status(self) -> EventStatus:
        # Importação local evita dependência circular entre modelo e serviço.
        from app.services.event_status import compute_event_status

        return compute_event_status(self.start_date, self.end_date)


class CallForPapers(VerificationMixin, Base):
    __tablename__ = "calls_for_papers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), index=True)
    call_type: Mapped[str] = mapped_column(String(80), index=True)
    title: Mapped[str | None] = mapped_column(String(400))
    submission_url: Mapped[str | None] = mapped_column(Text)
    opens_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deadline_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    extended_deadline_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    timezone: Mapped[str | None] = mapped_column(String(80))
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus),
        default=SubmissionStatus.unknown,
        index=True,
    )
    source_url: Mapped[str] = mapped_column(Text)
    source_excerpt: Mapped[str | None] = mapped_column(Text)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    event: Mapped[Event] = relationship(back_populates="calls")


class RegistrationWindow(VerificationMixin, Base):
    """Uma fase de inscrição independente, como antecipada ou regular.

    Uma linha representa uma única janela. Isso evita confundir o encerramento
    da inscrição antecipada com o encerramento de todas as inscrições.
    """

    __tablename__ = "registration_windows"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), index=True)
    registration_type: Mapped[str] = mapped_column(String(80), index=True)
    title: Mapped[str | None] = mapped_column(String(400))
    registration_url: Mapped[str | None] = mapped_column(Text)
    opens_on: Mapped[date | None] = mapped_column(Date, index=True)
    deadline_on: Mapped[date | None] = mapped_column(Date, index=True)
    timezone: Mapped[str | None] = mapped_column(String(80))
    status: Mapped[RegistrationStatus] = mapped_column(
        Enum(RegistrationStatus),
        default=RegistrationStatus.unknown,
        index=True,
    )
    source_url: Mapped[str] = mapped_column(Text)
    source_excerpt: Mapped[str | None] = mapped_column(Text)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    event: Mapped[Event] = relationship(back_populates="registrations")


class EventResource(VerificationMixin, Base):
    """Link específico e auditável para uma função dentro do evento."""

    __tablename__ = "event_resources"
    __table_args__ = (
        UniqueConstraint("event_id", "role", "url", name="uq_event_resource_role_url"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), index=True)
    role: Mapped[ResourceRole] = mapped_column(Enum(ResourceRole), index=True)
    label: Mapped[str] = mapped_column(String(160))
    url: Mapped[str] = mapped_column(Text)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    source_url: Mapped[str] = mapped_column(Text)
    source_excerpt: Mapped[str | None] = mapped_column(Text)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    event: Mapped[Event] = relationship(back_populates="resources")


class Subscriber(Base):
    __tablename__ = "subscribers"
    __table_args__ = (UniqueConstraint("email", name="uq_subscriber_email"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    areas: Mapped[str] = mapped_column(Text, default="high-energy-physics,CERN,particle-collisions")
    frequency: Mapped[str] = mapped_column(String(30), default="weekly")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
