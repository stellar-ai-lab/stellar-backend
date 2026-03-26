from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    WEB_APP_URL: str
    SUPABASE_URL: str
    SUPABASE_SECRET_KEY: str
    SUPABASE_BUCKET: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_SECRET_KEY: str
    GOOGLE_GEMINI_API_KEY: str
    OPENAI_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=True
    )


settings = Settings()
