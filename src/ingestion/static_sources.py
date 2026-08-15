"""
static_sources.py — the two Task 2 sources that are NOT links (buyer
form, call notes). Given verbatim in the brief, so nothing to fetch —
treated as trusted static input rather than a tool the agent calls.
"""

BUYER_FORM_TEXT = """
Ref: INT-2024-8841
Buyer: SunBridge Trading Pvt. Ltd.
Destination: Bangladesh
Item: SUN-5K-G06P3-EU-AM2-P1 — buyer wrote "5000 W", rooftop
Maker: Ningbo Deye Inverter Technology Co., Ltd., China
Attached docs: none
Need by: 2024-11-30
""".strip()

CALL_NOTES_TEXT = """
2024-10-03, call notes from Ramesh:
Model SUN-5K-G06P3, 5 kW, Deye (China). Said IP65. Weight maybe 18 kg?
Installer guessed. Mentioned SGS and "high 90s efficiency" on the phone —
nothing in writing. No label photo yet. They want something to circulate
internally before the real certificates arrive. OK to mark parts as
"pending from factory" where unsure.
""".strip()