from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Voz da Lei API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://vozdalei:vozdalei123@localhost:5432/vozdalei"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # AI APIs
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    # External APIs
    CAMARA_API_URL: str = "https://dadosabertos.camara.leg.br/api/v2"
    SENADO_API_URL: str = "https://legis.senado.leg.br/dadosabertos"
    QUERIDO_DIARIO_API_URL: str = "https://queridodiario.ok.org.br/api"
    LEXML_API_URL: str = "https://www.lexml.gov.br/busca/SRU"
    BASE_DOS_DADOS_PROJECT: str = "basedosdados"

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001"]

    # Audio
    MAX_AUDIO_SIZE_MB: int = 25
    SUPPORTED_AUDIO_FORMATS: list = ["mp3", "wav", "ogg", "m4a"]

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
