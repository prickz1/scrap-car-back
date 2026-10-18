from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    APP_NAME: str = "Scrap Carros API"
    DEBUG: bool = True
    ML_MODELS_DIR: str = "/app/modelos_ml"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
