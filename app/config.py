from pydantic_settings import BaseSettings, SettingsConfigDict
from app.utils.utils import singleton

@singleton
class Config(BaseSettings):
    # NUMERIC
    USER_MIN_PASSWORD_LENGTH: int
    USER_MAX_PASSWORD_LENGTH: int
    OAUTH2_ACCESS_TOKEN_LIFE_MINUTES: int

    # CHARSTRING
    DATABASE_HOSTNAME: str
    DATABASE_PORT: str
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DT_DATETIME_FORMAT: str
    DT_TIME_FORMAT: str
    SERVICE_DEFAULT_OPEN_TIME: str
    SERVICE_DEFAULT_CLOSE_TIME: str
    SERVICE_MIN_TIME: str
    SERVICE_MAX_TIME: str

    # CONFIG OF CLASS
    model_config = SettingsConfigDict(env_file=".env")

# SINGLETON OBJECT FOR USE THROUGHOUT PROJECT
CONFIG = Config()