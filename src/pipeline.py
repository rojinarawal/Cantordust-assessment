"""
pipeline.py — the only file that knows about every stage and the order
they run in. Kept separate from main.py so the pipeline itself is
importable/testable without going through the CLI.
"""

from src.agents.extraction_agent import run_extraction


def run() -> None:
    # Stage 2 only, for now — reconciliation and rendering are added
    # as milestones 3 and 4.
    result = run_extraction()
    print(result)