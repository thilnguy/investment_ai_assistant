from dotenv import load_dotenv
import os

load_dotenv()
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")
TRANSLATE_MODEL = os.getenv("TRANSLATE_MODEL", "gpt-4o-mini")
DEFAULT_TARGET_LANGUAGE = "Vietnamese"
DEFAULT_INVESTMENT_TYPE = "Gold"
METAL_PRICE_API_KEY = os.getenv("METAL_PRICE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STT_MODEL = os.getenv("STT_MODEL", "whisper-1")
