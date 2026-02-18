from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Job Apply Assistant"
    db_url: str = "sqlite:///./data/db.sqlite3"
    packets_dir: str = "./data/packets"
    templates_dir: str = "./data/templates"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"

settings = Settings()
