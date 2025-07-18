"""
Settings module for backend configuration.
Uses pydantic-settings for type-safe environment variable management.
"""
import os
import warnings
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

class BackendSettings(BaseSettings):
    """
    Backend configuration settings loaded from environment variables.
    """
    
    # API Keys (Required)
    GROQ_API_KEY: str = Field(..., description="Groq API key for LLM access")
    TAVILY_API_KEY: str = Field(..., description="Tavily API key for web search")
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Server host address")
    PORT: int = Field(default=8000, description="Server port")
    RELOAD: bool = Field(default=False, description="Enable auto-reload in development")
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )
    
    # Agent Configuration
    MAX_ITERATIONS: int = Field(default=10, description="Maximum workflow iterations")
    MODEL_NAME: str = Field(default="llama-3.1-8b-instant", description="Default LLM model")
    TEMPERATURE: float = Field(default=0.7, description="LLM temperature", ge=0.0, le=2.0)
    MAX_TOKENS: int = Field(default=2000, description="Maximum tokens per response", gt=0)
    
    # Database Configuration (for future use)
    DATABASE_URL: Optional[str] = Field(default=None, description="Database connection URL")
    
    # CORS Configuration
    CORS_ORIGINS: str = Field(
        default="http://localhost:8501,http://127.0.0.1:8501",
        description="Comma-separated list of allowed CORS origins"
    )
    
    # WebSocket Configuration
    WS_HEARTBEAT_INTERVAL: int = Field(default=30, description="WebSocket heartbeat interval in seconds")
    
    # Task Configuration
    TASK_TIMEOUT: int = Field(default=300, description="Task timeout in seconds")
    MAX_CONCURRENT_TASKS: int = Field(default=10, description="Maximum concurrent tasks")
    
    # Agent Configuration Constants
    MAX_AGENTS: int = Field(default=4, description="Maximum number of agents in the system")
    DEFAULT_AGENT_COUNT: int = Field(default=4, description="Default agent count for progress calculations")
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()
    
    @field_validator("MODEL_NAME")
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        # Add known Groq models for validation
        valid_models = [
            "llama-3.1-8b-instant",
            "llama-3.1-70b-versatile", 
            "mixtral-8x7b-32768",
            "gemma-7b-it"
        ]
        if v not in valid_models:
            # Warning but don't fail - allows for new models
            warnings.warn(f"Model {v} not in known models: {valid_models}")
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        """Convert comma-separated CORS origins string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"  # Ignore extra environment variables
    }

# Global settings instance
settings = BackendSettings()

def get_settings() -> BackendSettings:
    """
    Get the global settings instance.
    Useful for dependency injection in FastAPI.
    """
    return settings
