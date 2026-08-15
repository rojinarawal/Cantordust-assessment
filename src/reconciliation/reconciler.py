"""
reconciler.py — given a ProductRecord already produced by extraction, derive the reconciliation
views the brief asks for explicitly:
  - what is pending from the factory
  - what is only backed by verbal/guessed sources (low confidence)
  - a concrete list of questions to send the factory
"""

from src.domain.schemas import ProductRecord, ExtractedField

CATEGORY_LABELS = {
    "product_identity": "Product identity",
    "manufacturer_identity": "Manufacturer identity",
    "test_evidence": "Test evidence",
    "labeling": "Labeling",
    "importer_paperwork": "Importer paperwork",
}


def _all_fields(record: ProductRecord) -> list[tuple[str, ExtractedField]]:
    """Flatten the record into (category, field) pairs for iteration."""
    result = []
    for category in CATEGORY_LABELS:
        for field in getattr(record, category):
            result.append((category, field))
    return result


def pending_fields(record: ProductRecord) -> list[tuple[str, ExtractedField]]:
    """Fields not available in any source - need to be chased from the factory."""
    return [(c, f) for c, f in _all_fields(record) if f.is_pending]


def low_confidence_fields(record: ProductRecord) -> list[tuple[str, ExtractedField]]:
    """Fields only backed by verbal claims or guesses, but NOT already
    pending (avoids double-listing the same field in two sections)."""
    return [(c, f) for c, f in _all_fields(record) if f.confidence == "low" and not f.is_pending]


def conflicting_fields(record: ProductRecord) -> list[tuple[str, ExtractedField]]:
    return [(c, f) for c, f in _all_fields(record) if f.sources_disagree]


_QUESTION_TEMPLATES = {
    "product_identity": "Please confirm the exact {field} for the SUN-5K-G06P3-EU-AM2-P1 in writing.",
    "manufacturer_identity": "Please confirm {field} in writing on company letterhead.",
    "test_evidence": "Please provide written certification/test reports for {field} - a verbal mention is not sufficient for import paperwork.",
    "labeling": "Please provide a photo or proof sheet of the product label showing {field}.",
    "importer_paperwork": "Please supply: {field}.",
}


def generate_factory_questions(record: ProductRecord) -> list[str]:
    questions = []
    for category, field in pending_fields(record) + low_confidence_fields(record):
        template = _QUESTION_TEMPLATES.get(category, "Please confirm {field} in writing.")
        questions.append(template.format(field=field.field_name.replace("_", " ")))
    seen = set()
    unique = []
    for q in questions:
        if q not in seen:
            seen.add(q)
            unique.append(q)
    return unique


def build_reconciliation_summary(record: ProductRecord) -> dict:
    return {
        "pending_from_factory": [
            {"category": CATEGORY_LABELS[c], "field": f.field_name}
            for c, f in pending_fields(record)
        ],
        "verbal_or_unverified": [
            {"category": CATEGORY_LABELS[c], "field": f.field_name, "value": f.value, "note": f.note}
            for c, f in low_confidence_fields(record)
        ],
        "conflicts_between_sources": [
            {"category": CATEGORY_LABELS[c], "field": f.field_name, "note": f.note}
            for c, f in conflicting_fields(record)
        ],
        "questions_for_factory": generate_factory_questions(record),
    }