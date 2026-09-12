import os

os.environ.setdefault(
    "API_DB_URL", "postgresql+psycopg://test:test@localhost:5433/canumpe_academic_api_test"
)
os.environ.setdefault(
    "ATTENDANCE_DB_URL", "postgresql+psycopg://test:test@localhost:5434/asistencia_test"
)
os.environ.setdefault(
    "MOODLE_DB_URL", "postgresql+psycopg://test:test@localhost:5435/moodle_test"
)
os.environ.setdefault("MOODLE_COURSE_ID", "10")  # matches tests/fixtures/moodle_seed.sql
os.environ.setdefault("API_KEY_HASH_PEPPER", "test-pepper")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("LOG_LEVEL", "WARNING")


def db_reachable(url: str) -> bool:
    from sqlalchemy import create_engine, text

    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return True
    except Exception:
        return False
