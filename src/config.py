import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
MODEL_NAME = "gemini-3.5-flash"

DATASHEET_URL = os.environ.get("DATASHEET_URL")