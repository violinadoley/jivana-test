import re


def normalize_medication_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())


def normalize_mrn(value: str | None) -> str | None:
    if not value:
        return None
    return re.sub(r"[^a-zA-Z0-9]", "", value).upper()


def normalize_patient_name(value: str | None) -> str | None:
    if not value:
        return None
    return re.sub(r"\s+", " ", value.strip().lower())
