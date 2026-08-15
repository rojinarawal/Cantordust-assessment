"""
pipeline.py — the only file that knows about every stage and the order
they run in. Kept separate from main.py so the pipeline itself is
importable/testable without going through the CLI.
"""
import json
from pathlib import Path
from src.agents.extraction_agent import run_extraction
from src.reconciliation.reconciler import build_reconciliation_summary

OUTPUT_PATH = Path("outputs/structured_data.json")

def run() -> None:
    record = run_extraction()
    reconciliation = build_reconciliation_summary(record)

    combined_output = {
        "extracted_data": record.model_dump(),
        "reconciliation": reconciliation,
    }

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(record.model_dump(), indent=2))

    print(f"Structured data written to {OUTPUT_PATH}")
    print(json.dumps(combined_output, indent=2))
    print(f"Wrote to: {OUTPUT_PATH.resolve()}")