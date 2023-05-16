from pydantic.env_settings import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    POSTGRESQL_USERNAME: str = "dbadmin"
    POSTGRESQL_PASSWORD: str = "dbadmin"
    SQLALCHEMY_DATABASE_URL: str = f"postgresql+psycopg2://{POSTGRESQL_PASSWORD}:{POSTGRESQL_USERNAME}@localhost:5435/rss_reader"  # noqa
    TEST_SQLALCHEMY_DATABASE_URL: str = f"postgresql+psycopg2://{POSTGRESQL_PASSWORD}:{POSTGRESQL_USERNAME}@localhost:5435/rss_reader_test"

    class Config:
        case_sensitive = True


settings = Settings()
