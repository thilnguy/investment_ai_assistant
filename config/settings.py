from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings
from pydantic import SecretStr

class Settings(BaseSettings):
    CHAT_MODEL: str
    TRANSLATE_MODEL: str
    STT_MODEL: str
    DEFAULT_TARGET_LANGUAGE: str="Vietnamese"
    DEFAULT_INVESTMENT_TYPE: str="Gold"
    METAL_PRICE_API_KEY: SecretStr
    OPENAI_API_KEY: SecretStr
    OLLAMA_BASE_URL: str

    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()