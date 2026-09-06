from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://samarth:samarth@localhost:5432/samarth"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    VAPID_PUBLIC_KEY: str = "BEl62iUYgUivxIkv69yViEuiBIa-Ib9-SkvMeAtA3LFgT8qBG89MCAh5B_k4S54yA2Gj4J0Bv9gV1s8uX5R_A1s="
    VAPID_PRIVATE_KEY: str = "c7E5N_N5Q1gR0xL7W8-X9Z8Y7X6W5V4U3T2S1R0Q9P8="
    VAPID_CLAIMS_EMAIL: str = "mailto:admin@samarth.coop"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
