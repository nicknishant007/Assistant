from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    SESSION_SECRET_KEY: str
    GOOGLE_API_KEY: str
    MISTRAL_API_KEY: str
    MISTRAL_MODEL: str="mistral-small-latest"
    FRONTEND_URL:str ="http://localhost:3000"
    REDIS_URL:str="redis://localhost:6379:6379/0"
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()