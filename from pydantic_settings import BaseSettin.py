from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()  # Optional, but you can keep it

class Settings(BaseSettings):
    # Database
    MYSQL_HOST: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str

    # OpenAI
    OPENAI_API_KEY: str

    # Pinecone
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str
    PINECONE_ENVIRONMENT: str

    # Vanna AI
    VANNA_API_KEY: str

    # Base URL
    BASE_URL: str

    # Cache settings
    CACHE_TTL: int = 3600  # Optional default

    class Config:
        env_file = ".env"

settings = Settings()
