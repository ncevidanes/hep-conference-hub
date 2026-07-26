from datetime import datetime, timezone

from app.models.domain import CallForPapers, SubmissionStatus


def compute_status(call: CallForPapers, now: datetime | None = None) -> SubmissionStatus:
    """Calcula o estado temporal sem apagar um estado explícito da fonte.

    Algumas páginas publicam apenas "Abstract Submission is Closed", sem a
    data do encerramento. Nesses casos, o estado explícito deve ser preservado.
    """

    now = now or datetime.now(timezone.utc)
    deadline = call.extended_deadline_at or call.deadline_at

    if call.status in {SubmissionStatus.rolling, SubmissionStatus.conflicting}:
        return call.status

    has_temporal_evidence = any((call.opens_at, call.deadline_at, call.extended_deadline_at))
    if not has_temporal_evidence and call.status != SubmissionStatus.unknown:
        return call.status

    if call.opens_at and now < call.opens_at:
        return SubmissionStatus.upcoming
    if deadline and now > deadline:
        return SubmissionStatus.closed
    if call.extended_deadline_at and now <= call.extended_deadline_at:
        return SubmissionStatus.extended
    if deadline and now <= deadline:
        return SubmissionStatus.open
    return SubmissionStatus.unknown
