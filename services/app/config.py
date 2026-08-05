from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Student Success Copilot API"
    debug: bool = True
    database_url: str = "sqlite:///./edupilot.db"
    chroma_path: str = "./chroma_data"
    # Permit the standard Next.js development addresses. Next uses port 3001
    # automatically when another process already occupies port 3000.
    cors_origins: str = (
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:3001,http://127.0.0.1:3001"
    )
    supabase_url: str = ""
    supabase_jwt_secret: str = ""
    dev_mode: bool = True
    redis_url: str = "redis://localhost:6379/0"
    
    # PostgreSQL Configuration
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "edupilot"
    postgres_user: str = "postgres"
    postgres_password: str = ""
    db_pool_size: int = 5  # Minimum pool size
    db_max_overflow: int = 15  # Maximum overflow (total max = pool_size + max_overflow = 20)
    db_pool_timeout: int = 30  # Connection timeout in seconds
    db_pool_recycle: int = 3600  # Recycle connections after 1 hour
    
    # TEE Configuration
    tee_mode: str = "mock"  # mock | aws_nitro | azure_confidential
    
    # Notification Services
    sendgrid_api_key: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_phone: str = ""
    firebase_credentials_path: str = ""
    notification_from_email: str = "noreply@edupilot.local"
    
    # Data Connectors
    unstop_api_key: str = ""
    enabled_connectors: str = "unstop,internshala"
    
    # Document Verification
    tesseract_cmd: str = ""  # Path to tesseract executable
    uidai_api_key: str = ""
    uidai_api_url: str = ""
    
    # Encryption & Security
    encryption_key_master: str = ""  # Base64 encoded key for document encryption
    audit_log_retention_days: int = 1095  # 3 years per DPDP Act

    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_temperature: float = 0.7

    # Auto-verification thresholds
    auto_approval_threshold: float = 0.85
    review_threshold: float = 0.60

    class Config:
        # Resolve relative to the backend directory so settings load whether
        # Uvicorn is started from the repository root or services/.
        env_file = Path(__file__).resolve().parents[1] / ".env"
        extra = "ignore"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]
    
    @property
    def enabled_connectors_list(self) -> list[str]:
        return [c.strip() for c in self.enabled_connectors.split(",") if c.strip()]
    
    @property
    def postgres_url(self) -> str:
        """Build PostgreSQL connection URL from individual components"""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def postgres_async_url(self) -> str:
        """Build PostgreSQL async connection URL (asyncpg dialect)"""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    def get_database_url(self) -> str:
        """
        Get the appropriate database URL based on configuration.
        Returns postgres_url if postgres_password is set, otherwise database_url (SQLite fallback).
        """
        if self.postgres_password:
            return self.postgres_url
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
