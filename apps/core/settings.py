from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_echo: bool = True
    redis_url: str = "redis://localhost:6379/0"
    resend_api_key: str
    frontend_url: str
    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf8",
        extra="ignore"
    )

    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

settings = Settings()