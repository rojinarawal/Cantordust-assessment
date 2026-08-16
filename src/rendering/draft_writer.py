"""
draft_writer.py — turns the final ProductRecord + reconciliation summary
into the human-readable Markdown draft SunBridge hands to their agent.
"""

from datetime import date
from src.domain.schemas import ProductRecord, ExtractedField

CATEGORY_TITLES = {
    "product_identity": "1. Product Identity",
    "manufacturer_identity": "2. Manufacturer Identity",
    "test_evidence": "3. Test Evidence",
    "labeling": "4. Labeling",
    "importer_paperwork": "5. Importer Paperwork",
}

def _confidence_tag(field: ExtractedField) -> str:
    """Pick a display tag based on actual source count + confidence,
    rather than assuming what 'medium' means - medium confidence can come
    from a single source OR from multiple sources that disagree, and
    those need different labels."""
    source_count = len([s for s in field.source.split(",") if s.strip() and s.strip() != "none"])

    if field.sources_disagree:
        return "🟡 Written, sources disagree"
    if field.confidence == "high":
        return "✅ Confirmed"
    if field.confidence == "low":
        return "⚠️ Verbal / unverified"
    # medium confidence
    if source_count > 1:
        return "🟡 Written, multiple sources (partial match)"
    return "🟡 Written, single source"


def _format_field(field: ExtractedField) -> str:
    if field.is_pending:
        line = f"- **{field.field_name.replace('_', ' ').title()}**: _Pending from manufacturer_"
    else:
        tag = _confidence_tag(field)
        line = f"- **{field.field_name.replace('_', ' ').title()}**: {field.value} ({tag})"
    if field.sources_disagree:
        line += "  \n  ⚠️ **Sources disagree** — " + field.note
    elif field.note:
        line += f"  \n  _{field.note}_"
    return line

def _format_category(category_key: str, fields: list[ExtractedField]) -> str:
    title = CATEGORY_TITLES[category_key]
    if not fields:
        return f"## {title}\n\n_No data available for this section._\n"
    body = "\n".join(_format_field(f) for f in fields)
    return f"## {title}\n\n{body}\n"


def generate_markdown_draft(record: ProductRecord, reconciliation: dict) -> str:
    parts = [
        "# SunBridge Trading — Bangladesh Import Compliance Draft",
        f"*Generated {date.today().isoformat()} — SUN-5K-G06P3-EU-AM2-P1, 5kW grid-tied inverter, Deye (China)*",
        "",
        "> This draft is an early working document, not a final compliance "
        "file. Several items are marked **pending from manufacturer** — "
        "that is expected at this stage, not a gap in this report. See "
        "the questions list at the end for what to chase next.",
        "",
    ]

    for category_key in CATEGORY_TITLES:
        fields = getattr(record, category_key)
        parts.append(_format_category(category_key, fields))

    parts.append("## Summary: What's Still Pending From The Factory\n")
    pending = reconciliation.get("pending_from_factory", [])
    if pending:
        for item in pending:
            parts.append(f"- {item['field'].replace('_', ' ').title()} ({item['category']})")
    else:
        parts.append("_Nothing currently marked pending._")
    parts.append("")

    parts.append("## Summary: Verbal / Unverified Claims (Not Yet In Writing)\n")
    verbal = reconciliation.get("verbal_or_unverified", [])
    if verbal:
        for item in verbal:
            parts.append(f"- **{item['field'].replace('_', ' ').title()}**: {item['value']} — _{item['note']}_")
    else:
        parts.append("_None — everything currently recorded is backed by a written source._")
    parts.append("")

    parts.append("## Summary: Conflicts Between Sources\n")
    conflicts = reconciliation.get("conflicts_between_sources", [])
    if conflicts:
        for item in conflicts:
            parts.append(f"- **{item['field'].replace('_', ' ').title()}** ({item['category']}): {item['note']}")
    else:
        parts.append("_None identified._")
    parts.append("")

    parts.append("## Questions To Send The Factory\n")
    questions = reconciliation.get("questions_for_factory", [])
    if questions:
        for i, q in enumerate(questions, start=1):
            parts.append(f"{i}. {q}")
    else:
        parts.append("_No outstanding questions._")
    parts.append("")

    return "\n".join(parts)