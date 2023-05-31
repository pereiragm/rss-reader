from pydantic.env_settings import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str
    SQLALCHEMY_DATABASE_URL: str
    TEST_SQLALCHEMY_DATABASE_URL: str
    BROKER_URL: str

    class Config:
        case_sensitive = True
        # env_file = ".env"  # Configs are read from file


settings = Settings()
