from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str
    gemini_api_key: str
    usda_api_key: str = "DEMO_KEY"
    database_url: str = "./munchmeter.db"

    class Config:
        env_file = ".env"


settings = Settings()
