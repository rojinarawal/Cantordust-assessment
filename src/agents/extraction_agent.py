from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from src.config import MODEL_NAME, DATASHEET_URL
from src.ingestion.pdf_fetcher import fetch_pdf_text
from src.ingestion.static_sources import BUYER_FORM_TEXT, CALL_NOTES_TEXT
from src.agents.prompts import EXTRACTION_PROMPT_TEMPLATE
from src.domain.schemas import ProductRecord

def build_agent():
    model = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0)
    return create_react_agent(model, tools=[fetch_pdf_text], response_format=ProductRecord,)

def run_extraction() -> str:
    agent = build_agent()
    prompt = EXTRACTION_PROMPT_TEMPLATE.format(
        datasheet_url=DATASHEET_URL,
        buyer_form=BUYER_FORM_TEXT,
        call_notes=CALL_NOTES_TEXT,
    )
    result = agent.invoke({"messages": [{"role": "user", "content": prompt}]})
    return result['structured_response']
