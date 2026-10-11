from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = "service"
    host: str = "127.0.0.1"
    port: int = 8000
    database_url: str = ""


settings = Settings()
