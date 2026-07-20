from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    secret_key: str = "dev-secret-key-change-me"
    database_url: str = "sqlite:///./data/fit_raport.db"
    session_cookie_name: str = "fit_raport_session"
    session_max_age_seconds: int = 60 * 60 * 24 * 30  # 30 dni


settings = Settings()
