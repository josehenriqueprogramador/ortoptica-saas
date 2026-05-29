from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    """
    Núcleo central de configuração da Engine Biomédica.
    Todas as variáveis críticas do sistema são carregadas
    de forma tipada e segura via .env ou ambiente do SO.
    """

    # AMBIENTE
    APP_ENV: str = Field(default="development")
    ENGINE_VERSION: str = Field(default="1.0.0")
    LOG_LEVEL: str = Field(default="INFO")

    # INFRAESTRUTURA
    REDIS_URL: str = Field(default="redis://redis:6379/0")
    QDRANT_URL: str = Field(default="http://qdrant:6333")

    # LIMITES BIOMÉDICOS
    MAX_FRAME_SIZE_BYTES: int = Field(default=5242880)
    STABILITY_THRESHOLD_CONFIDENCE: float = Field(default=0.85)
    MAX_LATENCY_SECONDS: float = Field(default=0.150)
    MAX_HEAD_ROTATION_DEGREES: float = Field(default=25.0)

    # PIPELINE DE TRACKING
    TARGET_FPS: int = Field(default=30)
    ENABLE_KALMAN_FILTER: bool = Field(default=True)
    ENABLE_TEMPORAL_SMOOTHING: bool = Field(default=True)
    ENABLE_DYNAMIC_DOWNSCALE: bool = Field(default=True)

    # SEGURANÇA CLÍNICA
    SESSION_TIMEOUT_SECONDS: int = Field(default=600)
    WEBSOCKET_HEARTBEAT_INTERVAL: int = Field(default=10)
    ALLOW_MOCK_TRACKING: bool = Field(default=True)

    # MEDIA PIPE / COMPUTER VISION
    FACEMESH_MAX_FACES: int = Field(default=1)
    FACEMESH_DETECTION_CONFIDENCE: float = Field(default=0.7)
    FACEMESH_TRACKING_CONFIDENCE: float = Field(default=0.7)

    # Configurações do Pydantic Settings
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

@lru_cache
def get_settings() -> Settings:
    """
    Singleton cacheado para evitar recarregar o arquivo .env
    múltiplas vezes durante o ciclo de vida do runtime.
    """
    return Settings()

# Instância global unificada
settings = get_settings()
