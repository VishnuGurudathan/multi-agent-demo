"""
Streamlit UI for Multi-Agent System - Refactored Version
Clean, maintainable architecture following design patterns:
- Strategy Pattern: Page handlers
- Factory Pattern: UI components
- Repository Pattern: API service
- Observer Pattern: WebSocket manager
- Singleton Pattern: Service instances
"""
import streamlit as st
from ui_config import UIConfig
from page_handlers import PageHandlerFactory

class MultiAgentUI:
    """Main UI application class"""
    
    def __init__(self):
        self.config = UIConfig()
        self._configure_page()
        self._initialize_session_state()
    
    def _configure_page(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title=self.config.PAGE_TITLE,
            page_icon=self.config.PAGE_ICON,
            layout=self.config.LAYOUT,
            initial_sidebar_state=self.config.SIDEBAR_STATE
        )
    
    def _initialize_session_state(self):
        """Initialize session state variables"""
        session_defaults = {
            'tasks': {},
            'task_updates': {},
            'ws_connections': {}
        }
        
        for key, default_value in session_defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def _render_header(self):
        """Render main header"""
        st.title(f"{self.config.PAGE_ICON} {self.config.PAGE_TITLE}")
        st.markdown("**Production-ready multi-agent system with LangGraph orchestration**")
    
    def _render_sidebar(self) -> str:
        """Render sidebar navigation and return selected page"""
        st.sidebar.title("Navigation")
        return st.sidebar.selectbox(
            "Choose a page", 
            ["Submit Task", "Monitor Tasks", "System Info"]
        )
    
    def run(self):
        """Main application entry point"""
        self._render_header()
        
        # Get selected page from sidebar
        selected_page = self._render_sidebar()
        
        # Create and execute appropriate page handler
        page_handler = PageHandlerFactory.create_handler(selected_page)
        page_handler.render()

def main():
    """Application entry point"""
    app = MultiAgentUI()
    app.run()

if __name__ == "__main__":
    main()
