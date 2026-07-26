from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import delete, select

from app.data.latin_america_2026 import LATIN_AMERICA_SEEDS
from app.db.session import SessionLocal
from app.models.domain import (
    CallForPapers,
    Event,
    EventResource,
    RegistrationStatus,
    RegistrationWindow,
    ResourceRole,
    SubmissionStatus,
)

# Registros reais de referência. O seed não inventa submissões abertas.
# Prazos só são criados quando há uma fonte explícita e verificável.
SEEDS = [
    {
        "name": "43rd International Conference on High Energy Physics",
        "acronym": "ICHEP 2026",
        "slug": "ichep-2026",
        "area": "high-energy-physics",
        "tags": "HEP,CERN,particle collisions,ATLAS,CMS,ALICE,LHCb",
        "organizer": "IUPAP C11",
        "official_url": "https://ichep2026.org/",
        "description": "Conferência internacional de referência em física de altas energias.",
        "start_date": date(2026, 7, 30),
        "end_date": date(2026, 8, 5),
        "city": "Natal",
        "country_code": "BR",
        "format": "in-person",
        "calls": [
            {
                "call_type": "talk_abstract",
                "title": "Resumo para apresentação oral",
                "submission_url": "https://indico.cern.ch/event/1522800/abstracts/",
                "opens_at": datetime(2025, 12, 1, 8, 0, tzinfo=ZoneInfo("America/Sao_Paulo")),
                "deadline_at": datetime(2026, 2, 9, 23, 59, tzinfo=ZoneInfo("America/Sao_Paulo")),
                "status": SubmissionStatus.closed,
                "timezone": "America/Sao_Paulo",
                "source_url": "https://indico.cern.ch/event/1522800/abstracts/",
                "source_excerpt": (
                    "The abstract submission deadline is February 9th, 2026 for talks "
                    "and February 16th, 2026 for posters (both deadlines at 23:59 BRT)."
                ),
                "confidence_score": 1.0,
            },
            {
                "call_type": "poster_abstract",
                "title": "Resumo para pôster",
                "submission_url": "https://indico.cern.ch/event/1522800/abstracts/",
                "opens_at": datetime(2025, 12, 1, 8, 0, tzinfo=ZoneInfo("America/Sao_Paulo")),
                "deadline_at": datetime(2026, 2, 16, 23, 59, tzinfo=ZoneInfo("America/Sao_Paulo")),
                "status": SubmissionStatus.closed,
                "timezone": "America/Sao_Paulo",
                "source_url": "https://indico.cern.ch/event/1522800/abstracts/",
                "source_excerpt": (
                    "The abstract submission deadline is February 9th, 2026 for talks "
                    "and February 16th, 2026 for posters (both deadlines at 23:59 BRT)."
                ),
                "confidence_score": 1.0,
            },
        ],
        "resources": [
            {
                "role": ResourceRole.submission,
                "label": "Chamada de resumos",
                "url": "https://indico.cern.ch/event/1522800/abstracts/",
                "is_primary": True,
                "source_url": "https://indico.cern.ch/event/1522800/abstracts/",
                "source_excerpt": "Call for Abstracts",
                "confidence_score": 1.0,
            },
            {
                "role": ResourceRole.registration,
                "label": "Inscrição no Indico",
                "url": "https://indico.cern.ch/event/1522800/registrations/121108/",
                "is_primary": True,
                "source_url": "https://indico.cern.ch/event/1522800/registrations/121108/",
                "source_excerpt": "Registration",
                "confidence_score": 1.0,
            },
            {
                "role": ResourceRole.programme,
                "label": "Programa científico",
                "url": "https://indico.cern.ch/event/1522800/program",
                "is_primary": True,
                "source_url": "https://indico.cern.ch/event/1522800/program",
                "source_excerpt": "Scientific Programme",
                "confidence_score": 1.0,
            },
            {
                "role": ResourceRole.timetable,
                "label": "Cronograma detalhado",
                "url": "https://indico.cern.ch/event/1522800/timetable/",
                "is_primary": True,
                "source_url": "https://indico.cern.ch/event/1522800/timetable/",
                "source_excerpt": "Timetable",
                "confidence_score": 1.0,
            },
        ],
        "registrations": [
            {
                "registration_type": "early",
                "title": "Inscrição antecipada",
                "registration_url": "https://indico.cern.ch/event/1522800/registrations/121108/",
                "opens_on": date(2026, 1, 10),
                "deadline_on": date(2026, 5, 15),
                "timezone": "America/Sao_Paulo",
                "status": RegistrationStatus.closed,
                "source_url": "https://ichep2026.org/registration-guidelines.html",
                "source_excerpt": "EARLY FEE (until May 15, 2026)",
                "confidence_score": 1.0,
            },
            {
                "registration_type": "regular",
                "title": "Inscrição regular",
                "registration_url": "https://indico.cern.ch/event/1522800/registrations/121108/",
                "opens_on": date(2026, 5, 16),
                "deadline_on": date(2026, 7, 23),
                "timezone": "America/Sao_Paulo",
                "status": RegistrationStatus.closed,
                "source_url": "https://ichep2026.org/registration-guidelines.html",
                "source_excerpt": "REGULAR FEE (from May 16 until July 23, 2026)",
                "confidence_score": 1.0,
            },
            {
                "registration_type": "onsite",
                "title": "Inscrição presencial",
                "registration_url": "https://indico.cern.ch/event/1522800/registrations/121108/",
                "opens_on": date(2026, 7, 24),
                "deadline_on": date(2026, 7, 30),
                "timezone": "America/Sao_Paulo",
                "status": RegistrationStatus.open,
                "source_url": "https://indico.cern.ch/event/1522800/registrations/121108/",
                "source_excerpt": "Registration is open. Deadline 30 Jul 2026.",
                "confidence_score": 1.0,
            },
        ],
    },
    {
        "name": "14th Large Hadron Collider Physics Conference",
        "acronym": "LHCP 2026",
        "slug": "lhcp-2026",
        "area": "high-energy-physics",
        "tags": "LHC,CERN,ATLAS,CMS,ALICE,LHCb,particle collisions",
        "organizer": "LHC experiments",
        "official_url": "https://indico.cern.ch/event/1537360/",
        "description": "Conferência dedicada à física do Large Hadron Collider.",
        "start_date": date(2026, 5, 18),
        "end_date": date(2026, 5, 22),
        "city": "Paris",
        "country_code": "FR",
        "format": "in-person",
        "resources": [
            {
                "role": ResourceRole.submission,
                "label": "Chamada de pôsteres",
                "url": "https://indico.cern.ch/event/1537360/abstracts/",
                "is_primary": True,
                "source_url": "https://indico.cern.ch/event/1537360/abstracts/",
                "source_excerpt": "Call for Poster Abstracts",
                "confidence_score": 1.0,
            },
            {
                "role": ResourceRole.registration,
                "label": "Inscrição",
                "url": "https://indico.cern.ch/event/1537360/registrations/",
                "is_primary": True,
                "source_url": "https://indico.cern.ch/event/1537360/registrations/",
                "source_excerpt": "Registration",
                "confidence_score": 1.0,
            },
            {
                "role": ResourceRole.programme,
                "label": "Programa científico",
                "url": "https://indico.cern.ch/event/1537360/page/38762-conference-program",
                "is_primary": True,
                "source_url": "https://indico.cern.ch/event/1537360/page/38762-conference-program",
                "source_excerpt": "Conference Program",
                "confidence_score": 1.0,
            },
            {
                "role": ResourceRole.timetable,
                "label": "Cronograma",
                "url": "https://indico.cern.ch/event/1537360/timetable/",
                "is_primary": True,
                "source_url": "https://indico.cern.ch/event/1537360/timetable/",
                "source_excerpt": "Timetable",
                "confidence_score": 1.0,
            },
            {
                "role": ResourceRole.contributions,
                "label": "Lista de contribuições",
                "url": "https://indico.cern.ch/event/1537360/contributions/",
                "is_primary": True,
                "source_url": "https://indico.cern.ch/event/1537360/contributions/",
                "source_excerpt": "Contribution List",
                "confidence_score": 1.0,
            },
        ],
        "calls": [],
        "registrations": [],
    },
    {
        "name": "28th Conference on Computing in High Energy and Nuclear Physics",
        "acronym": "CHEP 2026",
        "slug": "chep-2026",
        "area": "scientific-computing",
        "tags": "CERN,HEP computing,ROOT,Geant4,AI,HPC",
        "organizer": "HEP computing community",
        "official_url": "https://indico.cern.ch/event/1471803/",
        "description": "Computação, software e dados para física de altas energias e nuclear.",
        "start_date": date(2026, 5, 25),
        "end_date": date(2026, 5, 29),
        "city": "Bangkok",
        "country_code": "TH",
        "format": "in-person",
        "resources": [
            {
                "role": ResourceRole.submission,
                "label": "Chamada de resumos",
                "url": "https://indico.cern.ch/event/1471803/abstracts/",
                "is_primary": True,
                "source_url": "https://indico.cern.ch/event/1471803/abstracts/",
                "source_excerpt": "Call for Abstracts",
                "confidence_score": 1.0,
            },
            {
                "role": ResourceRole.registration,
                "label": "Inscrição",
                "url": "https://indico.cern.ch/event/1471803/registrations/",
                "is_primary": True,
                "source_url": "https://indico.cern.ch/event/1471803/registrations/",
                "source_excerpt": "Registration",
                "confidence_score": 1.0,
            },
            {
                "role": ResourceRole.programme,
                "label": "Programa científico",
                "url": "https://indico.cern.ch/event/1471803/page/39328-scientific-programme",
                "is_primary": True,
                "source_url": "https://indico.cern.ch/event/1471803/page/39328-scientific-programme",
                "source_excerpt": "Scientific Programme",
                "confidence_score": 1.0,
            },
            {
                "role": ResourceRole.timetable,
                "label": "Cronograma",
                "url": "https://indico.cern.ch/event/1471803/timetable/",
                "is_primary": True,
                "source_url": "https://indico.cern.ch/event/1471803/timetable/",
                "source_excerpt": "Timetable",
                "confidence_score": 1.0,
            },
            {
                "role": ResourceRole.contributions,
                "label": "Lista de contribuições",
                "url": "https://indico.cern.ch/event/1471803/contributions/",
                "is_primary": True,
                "source_url": "https://indico.cern.ch/event/1471803/contributions/",
                "source_excerpt": "Contribution List",
                "confidence_score": 1.0,
            },
            {
                "role": ResourceRole.proceedings,
                "label": "Proceedings",
                "url": "https://indico.cern.ch/event/1471803/page/40062-proceedings",
                "is_primary": True,
                "source_url": "https://indico.cern.ch/event/1471803/page/40062-proceedings",
                "source_excerpt": "Proceedings",
                "confidence_score": 1.0,
            },
        ],
        "calls": [],
        "registrations": [],
    },
    {
        "name": "21st International Conference on Calorimetry for High Energy Physics",
        "acronym": "CALOR 2026",
        "slug": "calor-2026",
        "area": "detectors",
        "tags": "calorimetry,detectors,CERN,ATLAS,CMS,energy reconstruction",
        "organizer": "International calorimetry community",
        "official_url": "https://calor2026.uta.edu/",
        "description": "Instrumentação e calorimetria para física de altas energias.",
        "start_date": date(2026, 5, 31),
        "end_date": date(2026, 6, 5),
        "city": "Santa Fe",
        "country_code": "US",
        "format": "in-person",
        "resources": [
            {
                "role": ResourceRole.submission,
                "label": "Chamada de resumos",
                "url": "https://indico.cern.ch/event/1572594/abstracts/",
                "is_primary": True,
                "source_url": "https://indico.cern.ch/event/1572594/abstracts/",
                "source_excerpt": "Call for Abstracts",
                "confidence_score": 1.0,
            },
            {
                "role": ResourceRole.registration,
                "label": "Inscrição e informações",
                "url": "https://web.cvent.com/event/45985898-e3a4-451b-a9f4-cd103944fc32/summary",
                "is_primary": True,
                "source_url": "https://calor2026.uta.edu/",
                "source_excerpt": "CALOR 2026 conference registration landing page",
                "confidence_score": 0.95,
            },
            {
                "role": ResourceRole.timetable,
                "label": "Cronograma",
                "url": "https://indico.cern.ch/event/1572594/timetable/",
                "is_primary": True,
                "source_url": "https://indico.cern.ch/event/1572594/timetable/",
                "source_excerpt": "Timetable",
                "confidence_score": 1.0,
            },
            {
                "role": ResourceRole.contributions,
                "label": "Lista de contribuições",
                "url": "https://indico.cern.ch/event/1572594/contributions/",
                "is_primary": True,
                "source_url": "https://indico.cern.ch/event/1572594/contributions/",
                "source_excerpt": "Contribution List",
                "confidence_score": 1.0,
            },
        ],
        "calls": [
            {
                "call_type": "abstract",
                "title": "Call for abstracts",
                "submission_url": "https://indico.cern.ch/event/1572594/abstracts/",
                "deadline_at": datetime(2026, 5, 1, 23, 59, tzinfo=timezone.utc),
                "status": SubmissionStatus.closed,
                "source_url": "https://alice-conferences.web.cern.ch/node/70267",
                "source_excerpt": "Prazo de resumos prorrogado até 1º de maio de 2026.",
                "confidence_score": 0.95,
            }
        ],
        "registrations": [],
    },
]

SEEDS.extend(LATIN_AMERICA_SEEDS)


def seed() -> None:
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        for data in SEEDS:
            call_data = data["calls"]
            registration_data = data["registrations"]
            resource_data = data.get("resources", [])
            event_data = {
                key: value
                for key, value in data.items()
                if key not in {"calls", "registrations", "resources"}
            }
            event = db.scalar(select(Event).where(Event.slug == data["slug"]))

            if event is None:
                event = Event(**event_data)
                db.add(event)
                db.flush()
            else:
                for key, value in event_data.items():
                    setattr(event, key, value)

            event.source_type = "verified-seed"
            event.verified = True
            event.confidence_score = 0.95
            event.last_verified_at = now

            db.execute(delete(CallForPapers).where(CallForPapers.event_id == event.id))
            db.execute(delete(RegistrationWindow).where(RegistrationWindow.event_id == event.id))
            db.execute(delete(EventResource).where(EventResource.event_id == event.id))

            for call in call_data:
                event.calls.append(CallForPapers(**call, last_verified_at=now))
            for registration in registration_data:
                event.registrations.append(
                    RegistrationWindow(**registration, last_verified_at=now)
                )
            for resource in resource_data:
                event.resources.append(EventResource(**resource, last_verified_at=now))

        db.commit()


if __name__ == "__main__":
    seed()
