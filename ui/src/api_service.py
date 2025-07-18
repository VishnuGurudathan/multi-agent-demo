"""
API Service module for handling all backend communication
Implements the Repository pattern for data access
"""
import requests
import streamlit as st
from typing import Dict, List, Any, Optional
from ui_config import UIConfig

class APIService:
    """Handles all API communication with the backend"""
    
    def __init__(self):
        self.base_url = UIConfig.API_BASE_URL
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Optional[Dict]:
        """Make API request with error handling"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, json=data)
            elif method == "DELETE":
                response = requests.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            # Handle specific HTTP status codes with better messages
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                if status_code == 404:
                    st.error("❌ Task not found")
                elif status_code == 409:
                    st.warning("⏳ Task is still in progress. Results will be available when the task completes.")
                elif status_code == 500:
                    st.error("🚨 Server error occurred")
                else:
                    st.error(f"API Error ({status_code}): {str(e)}")
            else:
                st.error(f"API Error: {str(e)}")
            return None
    
    def get_health(self) -> Optional[Dict]:
        """Get system health status"""
        return self._make_request("/health")
    
    def get_agents(self) -> Optional[Dict]:
        """Get agent information"""
        return self._make_request("/agents")
    
    def create_task(self, task_data: Dict) -> Optional[Dict]:
        """Create a new task"""
        return self._make_request("/tasks", "POST", task_data)
    
    def get_all_tasks(self) -> Optional[List[Dict]]:
        """Get all active tasks"""
        return self._make_request("/tasks")
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get specific task status"""
        return self._make_request(f"/tasks/{task_id}")
    
    def get_task_results(self, task_id: str) -> Optional[Dict]:
        """Get task results"""
        return self._make_request(f"/tasks/{task_id}/results")
    
    def cancel_task(self, task_id: str) -> Optional[Dict]:
        """Cancel a task"""
        return self._make_request(f"/tasks/{task_id}", "DELETE")

# Singleton instance
api_service = APIService()
