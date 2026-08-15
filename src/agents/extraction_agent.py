from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from src.config import MODEL_NAME, DATASHEET_URL
from src.ingestion.pdf_fetcher import fetch_pdf_text
from src.ingestion.static_sources import BUYER_FORM_TEXT, CALL_NOTES_TEXT
from src.agents.prompts import EXTRACTION_PROMPT_TEMPLATE

def build_agent():
    model = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0)
    return create_react_agent(model, tools=[fetch_pdf_text])

def _extract_text(content) -> str:
    """Gemini returns message content as a list of blocks (text, plus an
    internal 'signature' block we don't need) rather than a plain string.
    Pull out just the text parts and join them."""
    if isinstance(content, str):
        return content
    return "\n".join(
        block.get("text", "")
        for block in content
        if isinstance(block, dict) and block.get("type") == "text"
    )

def run_extraction() -> str:
    agent = build_agent()
    prompt = EXTRACTION_PROMPT_TEMPLATE.format(
        datasheet_url=DATASHEET_URL,
        buyer_form=BUYER_FORM_TEXT,
        call_notes=CALL_NOTES_TEXT,
    )
    result = agent.invoke({"messages": [{"role": "user", "content": prompt}]})
    return result["messages"][-1].content
