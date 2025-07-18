"""
WebSocket manager for real-time updates
Implements the Observer pattern for handling real-time events
"""
import json
import threading
import websocket
import streamlit as st
from typing import Dict, Callable
from ui_config import UIConfig

class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.connections: Dict[str, websocket.WebSocketApp] = {}
        self.base_url = UIConfig.WS_BASE_URL
    
    def connect(self, task_id: str, on_message_callback: Callable = None) -> bool:
        """Connect to WebSocket for a specific task"""
        if task_id in self.connections:
            return True
            
        try:
            ws_url = f"{self.base_url}/ws/tasks/{task_id}"
            
            def on_message(ws, message):
                try:
                    data = json.loads(message)
                    if 'task_updates' not in st.session_state:
                        st.session_state.task_updates = {}
                    st.session_state.task_updates[task_id] = data
                    
                    if on_message_callback:
                        on_message_callback(data)
                        
                    st.rerun()
                except Exception as e:
                    st.error(f"WebSocket message error: {str(e)}")
            
            def on_error(ws, error):
                st.error(f"WebSocket error: {str(error)}")
            
            def on_close(ws, close_status_code, close_msg):
                if task_id in self.connections:
                    del self.connections[task_id]
                st.info("WebSocket connection closed")
            
            ws = websocket.WebSocketApp(
                ws_url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            
            def run_websocket():
                ws.run_forever()
            
            thread = threading.Thread(target=run_websocket, daemon=True)
            thread.start()
            
            self.connections[task_id] = ws
            return True
            
        except Exception as e:
            st.error(f"Failed to connect WebSocket: {str(e)}")
            return False
    
    def disconnect(self, task_id: str):
        """Disconnect WebSocket for a specific task"""
        if task_id in self.connections:
            self.connections[task_id].close()
            del self.connections[task_id]
    
    def disconnect_all(self):
        """Disconnect all WebSocket connections"""
        for ws in self.connections.values():
            ws.close()
        self.connections.clear()

# Singleton instance
websocket_manager = WebSocketManager()
