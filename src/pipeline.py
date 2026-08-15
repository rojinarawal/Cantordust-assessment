"""
pipeline.py — the only file that knows about every stage and the order
they run in. Kept separate from main.py so the pipeline itself is
importable/testable without going through the CLI.
"""
import json
from pathlib import Path
from src.agents.extraction_agent import run_extraction
from src.reconciliation.reconciler import build_reconciliation_summary
from src.rendering.draft_writer import generate_markdown_draft

JSON_OUTPUT_PATH = Path("outputs/structured_data.json")
DRAFT_OUTPUT_PATH = Path("outputs/draft.md")

def run() -> None:
    record = run_extraction()
    reconciliation = build_reconciliation_summary(record)

    combined_output = {
        "extracted_data": record.model_dump(),
        "reconciliation": reconciliation,
    }

    JSON_OUTPUT_PATH.parent.mkdir(exist_ok=True)
    JSON_OUTPUT_PATH.write_text(json.dumps(combined_output, indent=2), encoding='utf-8')
    print(f"Structured data written to: {JSON_OUTPUT_PATH.resolve()}")

    draft = generate_markdown_draft(record, reconciliation)
    DRAFT_OUTPUT_PATH.write_text(draft, encoding='utf-8')
    print(f"Human-readable draft written to: {DRAFT_OUTPUT_PATH.resolve()}")