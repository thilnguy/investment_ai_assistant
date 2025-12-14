from openai import OpenAI
from config.settings import settings

# Create a single shared LLM client for the whole app
client = OpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())

        