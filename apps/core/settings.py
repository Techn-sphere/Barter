from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from apps.core_dependency.dependencies import DBSettings


class Settings(BaseSettings):
    db_settings: DBSettings = DBSettings()
    secret_key: SecretStr

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf8",
        extra="ignore"
    )

settings = Settings()