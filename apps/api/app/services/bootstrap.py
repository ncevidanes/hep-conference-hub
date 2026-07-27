from sqlalchemy import func, select

from app.db.session import Base, SessionLocal, engine
from app.models.domain import Event


def initialize_database(seed_if_empty: bool = False) -> None:
    """Create the schema and optionally load the verified catalog once."""
    Base.metadata.create_all(bind=engine)

    if not seed_if_empty:
        return

    with SessionLocal() as db:
        event_count = db.scalar(select(func.count(Event.id))) or 0

    if event_count == 0:
        from app.seed import seed

        seed()
