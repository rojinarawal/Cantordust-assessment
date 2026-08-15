"""
schemas.py — the shared data shapes for the whole pipeline. Every other
stage (extraction, reconciliation, rendering) imports ProductRecord from
here rather than redefining its own shape."""

from typing import Literal
from pydantic import BaseModel, Field

class ExtractedField(BaseModel):
    field_name: str = Field(description="e.g. 'rated_power', 'ip_rating'")
    value: str = Field(description="The extracted value, or 'unknown' if not found anywhere")
    source: str = Field(
        description=(
            "Which source(s) this came from: 'datasheet', 'buyer_form', "
            "'call_notes', any comma-separated combination, or 'none' if "
            "the value is not available in any source"
        )
    )
    confidence: Literal["high", "medium", "low", "pending"] = Field(
        description=(
            "high = written and consistent across sources; "
            "medium = written but only in one source; "
            "low = only stated verbally / guessed (e.g. call notes); "
            "pending = not available anywhere, needs to be chased from the factory"
        )
    )
    note: str = Field(
        default="",
        description="Optional: explain a discrepancy, e.g. 'datasheet says 11kg, call notes guess 18kg'",
    )

class ProductRecord(BaseModel):
    product_identity: list[ExtractedField] = Field(
        description="Model number, variant, rated power, key electrical specs"
    )
    manufacturer_identity: list[ExtractedField] = Field(
        description="Legal company name, factory address, country of manufacture"
    )
    test_evidence: list[ExtractedField] = Field(
        description="Standards claimed, whether anything is in writing vs verbal"
    )
    labeling: list[ExtractedField] = Field(
        description="What the product label should carry: model, ratings, manufacturer, origin, protection rating"
    )
    importer_paperwork: list[ExtractedField] = Field(
        description="What SunBridge itself still has to supply or chase from the factory"
    )