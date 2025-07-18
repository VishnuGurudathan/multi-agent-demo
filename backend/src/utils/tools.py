"""
Tools module for LangChain tools used by agents.
Moved from main.py to centralize tool definitions.
"""
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
import os
import sys
from pathlib import Path

from ..logger import setup_logger

logger = setup_logger(__name__)

def get_tavily_api_key():
    """Get Tavily API key from settings or environment"""
    try:
        from ..config.settings import get_settings
        settings = get_settings()
        logger.info("Successfully loaded Tavily API key from settings")
        return settings.TAVILY_API_KEY
    except ImportError as e:
        logger.warning(f"Could not import settings: {e}. Falling back to environment variable")
        api_key = os.environ.get("TAVILY_API_KEY", "")
        if api_key:
            logger.info("Successfully loaded Tavily API key from environment")
        else:
            logger.error("No Tavily API key found in settings or environment")
        return api_key
    except Exception as e:
        logger.error(f"Error loading Tavily API key from settings: {e}. Falling back to environment")
        return os.environ.get("TAVILY_API_KEY", "")

@tool
def search_web(query: str) -> str:
    """Search the web for information using Tavily."""
    logger.info(f"Starting web search for query: {query}")
    
    try:
        tavily_key = get_tavily_api_key()
        if tavily_key:
            logger.debug("Using Tavily API key from configuration")
            search = TavilySearch(max_results=3, tavily_api_key=tavily_key)
        else:
            logger.warning("No Tavily API key available, using default configuration")
            search = TavilySearch(max_results=3)
        
        results = search.invoke(query)
        logger.info(f"Web search completed successfully. Results length: {len(str(results))}")
        return str(results)
        
    except Exception as e:
        logger.error(f"Error during web search: {str(e)}")
        return f"Error performing web search: {str(e)}"

@tool
def write_summary(content: str) -> str:
    """Write a summary of the provided content."""
    logger.info(f"Creating summary for content of length: {len(content)}")
    
    try:
        if not content:
            logger.warning("Empty content provided for summary")
            return "No content provided for summary."
        
        summary = f"Summary of findings:\n\n{content[:500]}..."
        logger.info("Summary created successfully")
        return summary
        
    except Exception as e:
        logger.error(f"Error creating summary: {str(e)}")
        return f"Error creating summary: {str(e)}"

# Export all available tools
AVAILABLE_TOOLS = [search_web, write_summary]

logger.info(f"Tools module loaded successfully. Available tools: {[tool.name for tool in AVAILABLE_TOOLS]}")
