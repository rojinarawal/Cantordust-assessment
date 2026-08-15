EXTRACTION_PROMPT_TEMPLATE = """
Fetch and read the manufacturer datasheet at this URL: {datasheet_url}

You also have these two additional sources, given as text (do not try to
fetch them - they are not links):

--- Buyer form ---
{buyer_form}

--- Call notes ---
{call_notes}

From all three sources, extract these fields for the 5kW model: model
number, rated power, manufacturer legal name, factory address/country,
IP rating, weight, efficiency, and any compliance standards mentioned.

Return your findings as a plain list of "field: value" pairs, noting
which source(s) each value came from and whether sources agree.
"""