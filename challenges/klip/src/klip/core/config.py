from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    secretkey: str
    access_token_expires: int
    refresh_token_expires: int

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
