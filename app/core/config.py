from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    api_db_url: str
    attendance_db_url: str
    moodle_db_url: str
    moodle_course_id: int
    """The single Moodle course CANUMPE currently serves (e.g. APS). Only
    enrolments in this course are ever returned from /me/courses."""

    api_key_hash_pepper: str = ""

    log_level: str = "INFO"
    environment: str = "production"
    rate_limit_per_minute: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
