"""Application settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # base kwargs
    DEBUG: bool = False

    # database
    SQL_DEBUG: bool = False
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "social_network"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    POSTGRES_POOl_SIZE: int = 20
    POSTGRES_MAX_OVERFLOW: int = 30
    POSTGRES_POOL_TIMEOUT: int = 60
    POSTGRES_POOL_RECYCLE: int = 3600

    # JWT
    JWT_SECRET_KEY: str
    JWT_EXPIRATION_TIME: int = 3600
    JWT_ALGORITHM: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Read replicas configuration
    POSTGRES_READ_HOSTS: str = "localhost:5433,localhost:5434"
    
    @property
    def get_read_replica_urls(self) -> list[str]:
        """Parse read replica URLs from environment variable."""
        urls = []
        for host_port in self.POSTGRES_READ_HOSTS.split(","):
            host_port = host_port.strip()
            if ":" in host_port:
                host, port = host_port.split(":")
            else:
                host, port = host_port, "5432"
            
            url = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{host}:{port}/{self.POSTGRES_DB}"
            urls.append(url)
        return urls

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None
    FEED_CACHE_SIZE: int = 1000
    FEED_CACHE_TTL: int = 3600

    WEB_PORT: int = 8000


settings = AppSettings()
