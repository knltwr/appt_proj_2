from pydantic_settings import BaseSettings, SettingsConfigDict
from app.utils.util_funcs import singleton

@singleton
class Config(BaseSettings):

    PASSWORD_MIN_LENGTH: int
    PASSWORD_MAX_LENGTH: int
    PASSWORD_SALT_ROUNDS: int

    OAUTH2_SECRET_KEY: str
    OAUTH2_ALGORITHM: str
    OAUTH2_ACCESS_TOKEN_LIFE_MINUTES: int

    DATABASE_HOSTNAME: str
    DATABASE_PORT: int
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str

    DATABASE_MAINT_DB_HOSTNAME: str
    DATABASE_MAINT_DB_PORT: int
    DATABASE_MAINT_DB_USERNAME: str
    DATABASE_MAINT_DB_PASSWORD: str
    DATABASE_MAINT_DB_NAME: str

    DATABASE_MIGRATIONS_RELATIVE_PATH: str

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