"""
Centralized logging configuration for the multi-agent system.
Provides consistent logging setup across all modules.
"""
import logging
import sys
import os

def setup_logger(name: str) -> logging.Logger:
    """
    Set up a logger with consistent formatting and configuration.
    
    Args:
        name: The name for the logger (usually __name__ of the calling module)
        
    Returns:
        Configured logger instance
    """
    # Get log level from environment or default to INFO
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Don't add handlers to module loggers if root logger is configured
    # Let them propagate to the root logger instead to avoid duplication
    logger.propagate = True
    
    return logger

def configure_root_logging():
    """
    Configure root logging to ensure all logs are visible in terminal.
    Call this during application startup.
    """
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Add console handler if not already present
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        console_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Configure uvicorn loggers to be visible
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    
    for uvicorn_log in [uvicorn_logger, uvicorn_access_logger]:
        uvicorn_log.setLevel(getattr(logging, log_level, logging.INFO))
        uvicorn_log.propagate = True

def get_logger(name: str) -> logging.Logger:
    """
    Convenience function to get a logger instance.
    Alias for setup_logger for easier importing.
    """
    return setup_logger(name)

def set_log_level(level: str):
    """
    Set the global log level for all loggers.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.getLogger().setLevel(getattr(logging, level.upper(), logging.INFO))
