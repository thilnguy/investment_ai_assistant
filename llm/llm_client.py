from openai import OpenAI
import config.settings as settings

# Create a single shared LLM client for the whole app
client = OpenAI(api_key=settings.OPENAI_API_KEY)

        