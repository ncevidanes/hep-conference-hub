from __future__ import annotations

from datetime import datetime, timezone

from app.models.domain import ConfidenceLevel, VerificationFreshness


def classify_confidence(score: float | None) -> ConfidenceLevel:
    """Converte uma pontuação numérica em uma faixa legível e estável.

    Os limites foram escolhidos para diferenciar evidência oficial/estruturada
    (alta), evidência consistente mas ainda sujeita a revisão (média) e dados
    provisórios ou inferidos (baixa).
    """

    if score is None:
        return ConfidenceLevel.unknown
    if score >= 0.90:
        return ConfidenceLevel.high
    if score >= 0.70:
        return ConfidenceLevel.medium
    return ConfidenceLevel.low


def classify_verification_freshness(
    last_verified_at: datetime | None,
    now: datetime | None = None,
) -> VerificationFreshness:
    """Classifica a idade da última verificação.

    - até 7 dias: atual;
    - de 8 a 30 dias: envelhecendo;
    - mais de 30 dias: desatualizada;
    - sem data: desconhecida.
    """

    if last_verified_at is None:
        return VerificationFreshness.unknown

    reference = now or datetime.now(timezone.utc)
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)
    if last_verified_at.tzinfo is None:
        last_verified_at = last_verified_at.replace(tzinfo=timezone.utc)

    age_days = max(0, (reference - last_verified_at).days)
    if age_days <= 7:
        return VerificationFreshness.current
    if age_days <= 30:
        return VerificationFreshness.aging
    return VerificationFreshness.stale
