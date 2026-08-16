"""
prompts.py — prompt text lives here, not inline in agent code, so wording
can be tuned without touching logic.
"""

EXTRACTION_PROMPT_TEMPLATE = """
Fetch and read the manufacturer datasheet at this URL: {datasheet_url}

We have these two additional sources, given as text:

--- Buyer form ---
{buyer_form}

--- Call notes ---
{call_notes}

Sort what you find into these five categories, matching an import
compliance checklist:
1. product_identity - model number, variant, rated power, key electrical specs
2. manufacturer_identity - legal company name, factory address, country
3. test_evidence - which standards are claimed, and whether anything is in writing
4. labeling - what the product label SHOULD carry (model, ratings, manufacturer, origin, protection rating), based on the specs you already have
5. importer_paperwork - what SunBridge itself still needs to chase from the factory (e.g. certificates, label photos)

For the labeling category specifically: report what the label should say
based on known specs - this is usually knowable with high or medium
confidence even though the physical label hasn't been seen yet. Do NOT
mark a labeling field as pending just because there's no photo of the
actual physical label - that verification gap belongs under
importer_paperwork (e.g. "product_label_photo") instead, and should only
be listed there, not duplicated in labeling. Only mark a labeling field
as pending if you genuinely don't know what the value should be at all.

For every field:
- Set source to whichever of 'datasheet', 'buyer_form', 'call_notes' it
  came from (combine with commas if more than one agrees).
- Set confidence to 'high', 'medium', or 'low', reflecting how sure you
  are about the VALUE ITSELF: 'high' if it's written and multiple
  sources agree. 'medium' if written but only in one source. 'low' if
  it's only stated verbally (e.g. in the call notes) or was a guess.
  Confidence only applies to values that exist somewhere - see
  is_pending below for values that don't exist anywhere yet.
- If sources disagree, still report the field, set confidence
  accordingly, and explain the disagreement in the note.
- For importer_paperwork specifically, list what's still needed even
  though this isn't literally "extracted" from a source - reason about
  what the import checklist requires versus what you found.
- Set sources_disagree to true ONLY if sources give genuinely different
  values (e.g. weight: 11kg vs 18kg). If sources agree, or only one
  source mentions the field, set sources_disagree to false, even if you
  add an explanatory note.
- Set is_pending to true whenever an item is not available in ANY source
  yet (missing certificates, no physical label photo, etc) - this is
  common for importer_paperwork fields, and should be rare or absent in
  product_identity, manufacturer_identity, and labeling, since those are
  mostly answerable from the datasheet already. When is_pending is true,
  set confidence to 'low'.
"""