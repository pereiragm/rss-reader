from pydantic.env_settings import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str
    SQLALCHEMY_DATABASE_URL: str
    TEST_SQLALCHEMY_DATABASE_URL: str
    BROKER_URL: str

    JWT_SECRET_KEY = "aecd8f21d9b0dad4598efaf905b1eaa494bf259ef2e06bd15311080db11ee2eb"
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION = 30  # minutes


    class Config:
        case_sensitive = True
        env_file = "local.env"


settings = Settings()
