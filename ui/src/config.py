"""
Settings module for UI configuration.
Uses pydantic-settings for type-safe environment variable management.
"""
from typing import Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings

class UISettings(BaseSettings):
    """
    UI configuration settings loaded from environment variables.
    """
    
    # Backend API Configuration
    BACKEND_API_URL: str = Field(
        default="http://localhost:8000", 
        description="Backend API base URL"
    )
    BACKEND_WS_URL: str = Field(
        default="ws://localhost:8000", 
        description="Backend WebSocket base URL"
    )
    
    # Streamlit Configuration
    APP_TITLE: str = Field(default="Multi-Agent System", description="Application title")
    PAGE_ICON: str = Field(default="🤖", description="Page icon for browser tab")
    LAYOUT: str = Field(default="wide", description="Streamlit page layout")
    
    # UI Behavior
    AUTO_REFRESH_INTERVAL: int = Field(
        default=5, 
        description="Auto-refresh interval for task monitoring in seconds"
    )
    MAX_DISPLAY_TASKS: int = Field(
        default=50, 
        description="Maximum number of tasks to display in lists"
    )
    
    # API Request Configuration
    REQUEST_TIMEOUT: int = Field(default=30, description="API request timeout in seconds")
    MAX_RETRIES: int = Field(default=3, description="Maximum API request retries")
    
    # WebSocket Configuration
    WS_RECONNECT_ATTEMPTS: int = Field(
        default=5, 
        description="WebSocket reconnection attempts"
    )
    WS_RECONNECT_DELAY: int = Field(
        default=2, 
        description="Delay between WebSocket reconnection attempts in seconds"
    )
    
    # Logging Configuration  
    LOG_LEVEL: str = Field(default="INFO", description="UI logging level")
    ENABLE_DEBUG: bool = Field(default=False, description="Enable debug mode")
    
    # Theme and Styling
    THEME: str = Field(default="light", description="UI theme (light/dark)")
    PRIMARY_COLOR: str = Field(default="#FF4B4B", description="Primary color for UI elements")
    
    # Features Flags
    ENABLE_WEBSOCKETS: bool = Field(default=True, description="Enable WebSocket connections")
    ENABLE_FILE_UPLOAD: bool = Field(default=False, description="Enable file upload features")
    ENABLE_TASK_HISTORY: bool = Field(default=True, description="Enable task history tracking")
    
    @validator("LAYOUT")
    def validate_layout(cls, v):
        valid_layouts = ["centered", "wide"]
        if v not in valid_layouts:
            raise ValueError(f"LAYOUT must be one of {valid_layouts}")
        return v
    
    @validator("THEME")
    def validate_theme(cls, v):
        valid_themes = ["light", "dark"]
        if v not in valid_themes:
            raise ValueError(f"THEME must be one of {valid_themes}")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables

# Global settings instance
settings = UISettings()

def get_settings() -> UISettings:
    """
    Get the global settings instance.
    Useful for accessing settings throughout the UI application.
    """
    return settings
