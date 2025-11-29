from pydantic_settings import BaseSettings

from apps.core_dependency.dependencies import DBSettings


class Settings(BaseSettings):
    db_settings: DBSettings = DBSettings()  # Экземпляр класса DBSettings

# Инициализация переменной settings
settings = Settings()