"""
prompts.py — prompt text lives here, not inline in agent code, so wording
can be tuned without touching logic.
"""

EXTRACTION_PROMPT_TEMPLATE = """
Fetch and read the manufacturer datasheet at this URL: {datasheet_url}

You also have these two additional sources, given as text (do not try to
fetch them - they are not links):

--- Buyer form ---
{buyer_form}

--- Call notes ---
{call_notes}

Sort what you find into these five categories, matching an import
compliance checklist:
1. product_identity - model number, variant, rated power, key electrical specs
2. manufacturer_identity - legal company name, factory address, country
3. test_evidence - which standards are claimed, and whether anything is in writing
4. labeling - what the product label should carry (model, ratings, manufacturer, origin, protection rating)
5. importer_paperwork - what SunBridge itself still needs to chase from the factory (e.g. certificates, label photos)

For every field:
- Set source to whichever of 'datasheet', 'buyer_form', 'call_notes' it
  came from (combine with commas if more than one agrees).
- Set confidence honestly: 'high' only if it's written and multiple
  sources agree. 'medium' if written but only in one source. 'low' if
  it's only stated verbally (e.g. in the call notes) or was a guess.
  'pending' if it doesn't exist anywhere yet - that is a valid, expected
  answer for several fields, not a failure to find something.
- If sources disagree, still report the field, set confidence
  accordingly, and explain the disagreement in the note.
- For importer_paperwork specifically, list what's still needed even
  though this isn't literally "extracted" from a source - reason about
  what the import checklist requires versus what you found.
- Set sources_disagree to true ONLY if sources give genuinely different
  values (e.g. weight: 11kg vs 18kg). If sources agree, or only one
  source mentions the field, set sources_disagree to false, even if you
  add an explanatory note.
- Set is_pending to true whenever an item is not available in any source
  yet (missing certificates, no label photo, etc) - this is common for
  importer_paperwork fields. Use confidence only for how sure you are
  about a value that DOES exist; when is_pending is true, set confidence
  to 'low'.
"""