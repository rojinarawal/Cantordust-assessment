# SunBridge Trading — Bangladesh Import Compliance Draft

Submission for the Cantordust Analytics AI Engineer Assessment — Task 2
(China → Bangladesh, "Almost nothing in hand").

## What this does

SunBridge Trading is importing a Deye SUN-5K-G06P3-EU-AM2-P1 grid-tied solar
inverter from China into Bangladesh. The factory hasn't sent proper
paperwork yet — all that exists is one manufacturer datasheet (a public PDF
link), a buyer form, and a set of call notes from a phone conversation.

This pipeline runs an autonomous LangGraph agent that:

1. Fetches and parses the real manufacturer datasheet PDF itself (not
   pre-read by a human and pasted in).
2. Combines it with the buyer form and call notes.
3. Extracts every fact relevant to an import compliance review, sorted
   into the five categories a real import agent checks: product identity,
   manufacturer identity, test evidence, labeling, and importer paperwork.
4. Judges each fact honestly — is it written or only verbal, do sources
   agree, does it exist at all yet.
5. Runs deterministic reconciliation logic over that structured output to
   surface what's pending, what's unverified, where sources conflict, and
   what to ask the factory.
6. Renders a clean Markdown draft — the actual document SunBridge would
   circulate internally while waiting on the real certificates.

Nothing in this pipeline was hand-typed from the source documents. If the
factory sends a revised datasheet tomorrow, re-running `python main.py` is
the only step needed to regenerate everything.

## How to run it

```bash
git clone <this-repo-url>
cd cantordust-task2
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
cp .env.example .env           # then paste your GOOGLE_API_KEY in
python main.py
```

Outputs land in `outputs/`:

- `structured_data.json` — machine-readable extraction + reconciliation, with source and confidence per field
- `draft.md` — the human-readable draft for SunBridge's import agent

## Architecture

This is a small pipeline architecture: data flows through distinct stages,
and each stage only knows its own job.

```
cantordust-task2/
├── main.py                        CLI entry point, ~5 lines, calls pipeline.run()
├── src/
│   ├── config.py                  env loading, model name, constants — one place to change
│   ├── ingestion/
│   │   ├── pdf_fetcher.py          the ONLY tool given to the agent: fetch + parse a PDF
│   │   └── static_sources.py       buyer form + call notes as static text (not links, nothing to fetch)
│   ├── agents/
│   │   ├── prompts.py               prompt text, kept out of code so wording can be tuned
│   │   └── extraction_agent.py      builds the LangGraph ReAct agent, runs extraction
│   ├── domain/
│   │   └── schemas.py               ExtractedField / ProductRecord — the shared data shape
│   │                                 every other stage imports rather than redefining
│   ├── reconciliation/
│   │   └── reconciler.py            pure logic, no LLM calls: derives pending / unverified /
│   │                                 conflicting fields and a factory question list
│   ├── rendering/
│   │   └── draft_writer.py          turns structured data into the Markdown draft — template
│   │                                 based, not another LLM call (see "why" below)
│   └── pipeline.py                  the only file that knows about every stage and calls
│                                     them in order
└── outputs/
    ├── structured_data.json
    └── draft.md
```

## Extraction approach and why

**Agent framework: LangGraph**, specifically `langgraph.prebuilt.create_react_agent`.
This builds a ReAct loop — the model reads the goal, decides whether it
needs to call a tool, reads the tool's result, and repeats until it has
enough to answer. The agent decides on its own to fetch the PDF; the code
never fetches it and hands the content over pre-read. That autonomy is
what the assessment brief specifically asks for.

**Model: Gemini 2.5 Flash / 3 Flash** (see `src/config.py` for the exact
string in use) via `langchain-google-genai`, chosen because it was
available on Google's free tier and supports tool calling, which the
ReAct loop depends on. Swapping providers only requires changing
`build_agent()` in `extraction_agent.py` — nothing else in the codebase
references a specific model or provider.

**PDF parsing: `pdfplumber`**, chosen over OCR because the source PDF has
selectable text and real tables, not scanned images — `pdfplumber` extracts
both text and table structure directly, which is more reliable than
running OCR on a document that doesn't need it.

**Structured output via `response_format`**, not manual JSON parsing.
`create_react_agent` accepts a Pydantic schema (`ProductRecord`) and
makes one additional constrained call after the tool-calling loop
finishes, guaranteeing the final answer matches the schema exactly —
no regex-ing JSON out of markdown fences, no risk of the model wrapping
the answer in prose.

**Reconciliation is deterministic Python, not a second LLM call.** By the
time extraction finishes, the agent has already judged confidence,
`is_pending`, and `sources_disagree` per field. Reconciliation only
filters and groups that data — it makes no new factual judgments, so
there's no risk of a second LLM call quietly changing a value on the way
out. This also makes reconciliation the easiest part of the codebase to
unit test, since it has no network calls and no randomness.

**Draft rendering is template-based, not an LLM call**, for the same
reason: formatting is not a judgment call, so it shouldn't touch the LLM
at all. This also makes the final draft byte-for-byte reproducible from a
given `structured_data.json`.

## Assumptions

- The 5kW model within the datasheet's product family (which spans 4–15kW)
  is the one relevant to SunBridge's order, per the brief.
- Where the buyer form and call notes give a rounded or shorthand figure
  (e.g. "5000 W" vs the datasheet's "5 kW", or "Deye" vs the full legal
  name), these are treated as the same fact stated differently, not a
  conflict — reserving `sources_disagree: true` for cases where the
  actual values differ (e.g. weight: 11kg vs "maybe 18kg").
- The manufacturer's datasheet server rejected plain `requests` calls
  (returned an error suggesting bot-blocking); the fetch tool sends
  browser-like headers (`User-Agent`, `Referer`) to get past this. This
  is a reasonable real-world workaround, not a way of bypassing anything
  the site owner intends to keep public — the PDF is a public marketing
  document.
- "Confidence" reflects certainty in the _value_, not urgency or
  importance — a field can be `is_pending: true` (nothing exists yet)
  independent of confidence, which only applies to values that do exist.

## Known limitations / what I'd do with more time

- **No automated tests.** `reconciler.py` is pure, deterministic logic
  with zero I/O — with more time this is the first place I'd add unit
  tests, since it's the cheapest part of the codebase to verify and the
  part most likely to silently regress if the schema changes again.
- **Single extraction pass, no retry/validation loop.** If the model
  mis-files a fact into the wrong category, nothing currently catches
  it. A second pass that checks the structured output against the
  original checklist (rather than trusting the first response) would
  catch that class of error.
- **No caching of the fetched PDF.** Every run re-downloads and
  re-parses the datasheet. For a 48-hour assessment this doesn't matter,
  but a production version would cache the raw text keyed by URL, and
  only re-fetch if the ETag/Last-Modified header changes — useful if
  the factory revises the datasheet mid-negotiation.
- **The question-generation templates in `reconciler.py` are generic per
  category**, not tuned per individual field. With more time I'd let the
  extraction agent draft the actual question text itself (still
  constrained by schema) rather than filling a fixed template, since a
  factory-facing question benefits from context a template can't supply.
- **No handling for a datasheet that fails to parse at all** (e.g. if
  Deye changes their PDF format or blocks the fetch entirely) — right
  now this would just crash. A production version should catch that and
  surface "datasheet could not be retrieved" as an explicit pending item
  rather than failing the whole run.
