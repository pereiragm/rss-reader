from pydantic.env_settings import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str

    # Postgres
    # POSTGRES_USER: str
    # POSTGRES_PASSWORD: str
    # POSTGRES_HOST: str
    # POSTGRES_PORT: str
    # SQLALCHEMY_DATABASE_URL: str = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/rss_reader"  # noqa
    SQLALCHEMY_DATABASE_URL: str
    # TEST_SQLALCHEMY_DATABASE_URL: str = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/rss_reader_test"
    TEST_SQLALCHEMY_DATABASE_URL: str

    class Config:
        case_sensitive = True
        # env_file = ".env"  # Configs are read from file


settings = Settings()
