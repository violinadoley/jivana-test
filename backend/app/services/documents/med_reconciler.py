from app.schemas.meddocs import (
    DiscrepancyType,
    DocumentType,
    EvidenceStatus,
    MedDiscrepancy,
    MedicationLine,
    ValidationFinding,
)
from app.services.documents.normalizers import (
    normalize_medication_name,
    normalize_mrn,
    normalize_patient_name,
)


class ReconcileInput:
    def __init__(self) -> None:
        self.medications_by_document: dict[str, list[MedicationLine]] = {}
        self.document_types: dict[str, DocumentType] = {}
        self.identifier_fields: dict[str, dict[str, str | None]] = {}
        self.discharge_has_documented_change_hint: bool = False


class ReconcileResult:
    def __init__(self) -> None:
        self.discrepancies: list[MedDiscrepancy] = []
        self.findings: list[ValidationFinding] = []
        self.weak_evidence_used: bool = False


def reconcile_medications(data: ReconcileInput) -> ReconcileResult:
    result = ReconcileResult()
    _validate_identifiers(data, result)

    prior = _meds_for_type(data, DocumentType.PRIOR_MEDICATION_RECORD)
    discharge = _meds_for_type(data, DocumentType.DISCHARGE_SUMMARY)
    rx = _meds_for_type(data, DocumentType.CURRENT_PRESCRIPTION)

    for med in prior + discharge + rx:
        if med.evidence_status != EvidenceStatus.VERIFIED:
            result.weak_evidence_used = True

    prior_map = {_key(m): m for m in prior}
    discharge_map = {_key(m): m for m in discharge}
    rx_map = {_key(m): m for m in rx}

    all_keys = set(prior_map) | set(discharge_map) | set(rx_map)

    for key in sorted(all_keys):
        p = prior_map.get(key)
        d = discharge_map.get(key)
        r = rx_map.get(key)

        if d and not r:
            result.discrepancies.append(
                MedDiscrepancy(
                    discrepancy_type=DiscrepancyType.OMITTED_MED,
                    summary=(
                        f"Medication {key} on discharge summary missing from current prescription."
                    ),
                    left_source=d.source_ref,
                    right_source=None,
                    requires_human_review=True,
                )
            )
        if r and not d and not p:
            result.discrepancies.append(
                MedDiscrepancy(
                    discrepancy_type=DiscrepancyType.ADDED_MED,
                    summary=f"Medication {key} on prescription not present on prior/discharge.",
                    left_source=r.source_ref,
                    requires_human_review=True,
                )
            )

        if d and r:
            _compare_pair(d, r, result, data.discharge_has_documented_change_hint)

        if p and r and not d:
            _compare_pair(p, r, result, False)

    return result


def _key(med: MedicationLine) -> str:
    return normalize_medication_name(med.medication_name)


def _compare_pair(
    left: MedicationLine,
    right: MedicationLine,
    result: ReconcileResult,
    documented_hint: bool,
) -> None:
    left_dose = (left.dose or left.strength or "").strip().lower()
    right_dose = (right.dose or right.strength or "").strip().lower()
    if left_dose == right_dose:
        return

    if left.strength and right.strength and left.strength != right.strength:
        dtype = DiscrepancyType.CONFLICTING_STRENGTH
    elif documented_hint:
        dtype = DiscrepancyType.DOCUMENTED_CHANGE
    else:
        dtype = DiscrepancyType.DOSE_MISMATCH

    result.discrepancies.append(
        MedDiscrepancy(
            discrepancy_type=dtype,
            summary=f"Dose/strength differs for {left.medication_name}.",
            left_source=left.source_ref,
            right_source=right.source_ref,
            requires_human_review=True,
        )
    )


def _meds_for_type(data: ReconcileInput, doc_type: DocumentType) -> list[MedicationLine]:
    out: list[MedicationLine] = []
    for doc_id, dtype in data.document_types.items():
        if dtype == doc_type:
            out.extend(data.medications_by_document.get(doc_id, []))
    return out


def _validate_identifiers(data: ReconcileInput, result: ReconcileResult) -> None:
    mrns = {did: normalize_mrn(fields.get("mrn")) for did, fields in data.identifier_fields.items()}
    names = {
        did: normalize_patient_name(fields.get("patient_name"))
        for did, fields in data.identifier_fields.items()
    }
    mrn_values = {v for v in mrns.values() if v}
    if len(mrn_values) > 1:
        result.findings.append(
            ValidationFinding(
                code="MRN_MISMATCH",
                message="Patient MRN differs across documents.",
                requires_review=True,
            )
        )
    name_values = {v for v in names.values() if v}
    if len(name_values) > 1:
        result.findings.append(
            ValidationFinding(
                code="PATIENT_NAME_MISMATCH",
                message="Patient name differs across documents.",
                requires_review=True,
            )
        )
    for did, fields in data.identifier_fields.items():
        if not fields.get("mrn"):
            result.findings.append(
                ValidationFinding(
                    code="MISSING_REQUIRED_FIELD",
                    message=f"Missing MRN on document {did}.",
                    related_fields=["mrn"],
                    requires_review=True,
                )
            )
