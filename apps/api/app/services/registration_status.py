from datetime import date

from app.models.domain import RegistrationStatus, RegistrationWindow


def compute_registration_status(
    registration: RegistrationWindow,
    today: date | None = None,
) -> RegistrationStatus:
    """Calcula o estado de uma fase específica de inscrição."""

    today = today or date.today()

    if registration.status == RegistrationStatus.conflicting:
        return registration.status
    if (
        registration.status == RegistrationStatus.closed
        and registration.deadline_on is None
    ):
        # Algumas inscrições encerram por lotação, sem publicar data final.
        return RegistrationStatus.closed

    has_temporal_evidence = any((registration.opens_on, registration.deadline_on))
    if not has_temporal_evidence and registration.status not in {
        RegistrationStatus.unknown,
        RegistrationStatus.not_announced,
    }:
        return registration.status

    if registration.opens_on and today < registration.opens_on:
        return RegistrationStatus.upcoming
    if registration.deadline_on and today > registration.deadline_on:
        return RegistrationStatus.closed
    if registration.opens_on and today >= registration.opens_on:
        return RegistrationStatus.open
    if registration.deadline_on and today <= registration.deadline_on:
        return RegistrationStatus.open
    return registration.status
