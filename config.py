from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    supabase_url: str
    supabase_publishable_key: str

    class Config():
        env_file = ".env"

settings = Settings()