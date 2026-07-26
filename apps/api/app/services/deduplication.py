import re
import unicodedata
from difflib import SequenceMatcher


def normalize(value: str | None) -> str:
    value = value or ""
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def likely_duplicate(name_a: str, name_b: str, acronym_a: str | None, acronym_b: str | None, threshold: float = 0.88) -> bool:
    if acronym_a and acronym_b and normalize(acronym_a) == normalize(acronym_b):
        return True
    return similarity(name_a, name_b) >= threshold
