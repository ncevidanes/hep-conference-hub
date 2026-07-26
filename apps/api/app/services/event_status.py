from datetime import date

from app.models.domain import EventStatus


def compute_event_status(
    start_date: date | None,
    end_date: date | None,
    today: date | None = None,
) -> EventStatus:
    """Classifica temporalmente um evento usando apenas suas datas oficiais.

    - ``unknown``: data inicial ainda não confirmada;
    - ``upcoming``: começa depois de hoje;
    - ``ongoing``: hoje está entre o início e o fim, inclusive;
    - ``finished``: terminou antes de hoje.

    Quando ``end_date`` não foi informada, o evento é tratado como tendo um
    único dia, igual a ``start_date``.
    """
    today = today or date.today()

    if start_date is None:
        return EventStatus.unknown

    effective_end = end_date or start_date

    if today < start_date:
        return EventStatus.upcoming
    if today <= effective_end:
        return EventStatus.ongoing
    return EventStatus.finished
