"""
Configuration module for Streamlit UI
Centralizes all configuration constants and settings
"""
import os

class UIConfig:
    """UI Configuration constants"""
    
    # API Configuration
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    WS_BASE_URL = os.getenv("WS_BASE_URL", "ws://localhost:8000")
    
    # UI Configuration
    PAGE_TITLE = "Multi-Agent AI System"
    PAGE_ICON = "🤖"
    LAYOUT = "wide"
    SIDEBAR_STATE = "expanded"
    
    # Chart Configuration
    CHART_COLORS = {
        "Completed": "#28a745",
        "In Progress": "#ffc107", 
        "Pending": "#6c757d"
    }
    
    # Status Indicators
    STATUS_ICONS = {
        "submitted": "🟢",
        "in_progress": "🟡", 
        "completed": "✅",
        "failed": "🔴"
    }
    
    # UI Styling
    SUCCESS_COLOR = "#d4edda"
    WARNING_COLOR = "#fff3cd"
    INFO_COLOR = "#d1ecf1"
    
    # Form Configuration
    FORM_SUBMIT_DELAY = 2  # seconds to grey out form after submission
    
    # Agent Configuration
    AGENT_LIST = ["Supervisor", "Researcher", "Analyst", "Writer", "Reviewer"]
    
    # Task Configuration
    TASK_TYPES = ["general", "analysis", "writing", "review", "research"]
    
    # Refresh Configuration
    AUTO_REFRESH_INTERVAL = 5  # seconds
    
    # WebSocket Configuration
    WS_TIMEOUT = 30
    
    # UX Enhancement Configuration
    TOAST_DURATION = 3000  # milliseconds
    FORM_DISABLE_DURATION = 3  # seconds
    CONNECTION_BADGE_REFRESH = 2  # seconds
    
    # Button Configuration
    BUTTON_SPACING = "0.5rem"
    MOBILE_BREAKPOINT = 768  # pixels
    
    # Notification Configuration
    MAX_NOTIFICATIONS = 3
    NOTIFICATION_AUTO_CLEAR = 10  # seconds
    
    # Success Display Configuration
    COMPACT_TASK_ID_LENGTH = 8
    EXPANDABLE_DETAILS_DEFAULT = False
