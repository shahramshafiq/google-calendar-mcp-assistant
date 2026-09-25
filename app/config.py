from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str

    openai_model: str = "gpt-4.1-mini"

    google_credentials_path: str = "credentials/credentials.json"
    google_token_path: str = "credentials/token.json"

    task_store_path: str = "data/tasks.json"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
