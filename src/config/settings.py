from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "lagrace-ngx-ai-insights"
    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/ngx"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    collector_source_url: str = "https://example.com/ngx-prices"
    scheduler_interval_minutes: int = 1440
    disclaimer: str = "Market information only. Not financial advice."

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
