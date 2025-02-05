from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    huggingface_api_token: str
    model_repo_id: str = "google/flan-t5-xl"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_length: int = 512
    temperature: float = 0.5
    persist_directory: str = "db"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
