"""
schemas.py — the shared data shapes for the whole pipeline. Every other
stage (extraction, reconciliation, rendering) imports ProductRecord from
here rather than redefining its own shape."""

from typing import Literal
from pydantic import BaseModel, Field

class ExtractedField(BaseModel):
    field_name: str = Field(description="e.g. 'rated_power', 'ip_rating'")
    value: str = Field(description="The extracted value, or 'unknown/Pending' if not found anywhere")
    source: str = Field(
        description=(
            "Which source(s) this came from: 'datasheet', 'buyer_form', "
            "'call_notes', any comma-separated combination, or 'none' if "
            "the value is not available in any source"
        )
    )
    confidence: Literal["high", "medium", "low"] = Field(
        description="Confidence in the value itself. If is_pending is True, set this to 'low'."
    )
    is_pending: bool = Field(
        default=False,
        description=(
            "True if this item does not exist in ANY source yet and needs "
            "to be chased from the factory - regardless of how certain you "
            "are that it's needed. Do not use 'confidence' for this."
        ),
    )
    sources_disagree: bool = Field(
        default=False,
        description="True ONLY if two or more sources give genuinely different values for this field (e.g. 11kg vs 18kg). False if sources agree, or if only one source mentions it at all.",
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