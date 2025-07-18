"""
Page handlers implementing the Strategy pattern
Each page is handled by a separate class with consistent interface
"""
import streamlit as st
import time
from abc import ABC, abstractmethod
from typing import Dict, Any
from api_service import api_service
from websocket_manager import websocket_manager
from components import component_factory
from ui_config import UIConfig

class PageHandler(ABC):
    """Abstract base class for page handlers"""
    
    @abstractmethod
    def render(self):
        """Render the page content"""
        pass

class SubmitTaskPageHandler(PageHandler):
    """Handler for the Submit Task page"""
    
    def render(self):
        st.header("Submit New Task")
        
        # Task submission form
        form_data = component_factory.create_task_form()
        
        if form_data["submitted"] and form_data["query"].strip():
            self._submit_task(form_data)
        elif form_data["submitted"]:
            st.error("⚠️ Please enter a task description")
    
    def _submit_task(self, form_data: Dict):
        """Submit a new task"""
        task_data = {
            "query": form_data["query"],
            "task_type": form_data["task_type"],
            "priority": form_data["priority"]
        }
        
        with st.spinner("Creating task..."):
            result = api_service.create_task(task_data)
        
        if result:
            task_id = result["task_id"]
            
            # Store task in session state for persistence
            if 'tasks' not in st.session_state:
                st.session_state.tasks = {}
            if 'last_submitted_task' not in st.session_state:
                st.session_state.last_submitted_task = None
            
            task_info = {
                "task_id": task_id,
                "query": form_data["query"],
                "task_type": form_data["task_type"],
                "priority": form_data["priority"],
                "status": "submitted"
            }
            
            st.session_state.tasks[task_id] = task_info
            st.session_state.last_submitted_task = task_info
            
            # Show success with task ID display
            st.success(f"✅ Task created successfully!")
            component_factory.create_task_id_display(task_id)
            st.toast(f"✅ Task {task_id[:8]}... created!", icon="✅")
            
            # Connect WebSocket
            if websocket_manager.connect(task_id):
                st.toast("🔗 Real-time monitoring connected", icon="🔗")
        else:
            st.error("❌ Failed to create task. Please try again.")

class MonitorTasksPageHandler(PageHandler):
    """Handler for the Monitor Tasks page"""
    
    def render(self):
        st.header("Task Monitoring")
        
        tasks_data = api_service.get_all_tasks()
        
        if not tasks_data:
            st.info("No active tasks found")
            return
        
        self._render_tasks(tasks_data)
        self._render_auto_refresh()
    
    def _render_tasks(self, tasks_data: list):
        """Render the list of tasks"""
        for task in tasks_data:
            task_id = task["task_id"]
            
            with st.expander(f"Task: {task_id[:8]}... - {task['status'].upper()}", expanded=True):
                st.write(f"**Query:** {task['query']}")
                
                detailed_task = api_service.get_task_status(task_id)
                
                if detailed_task:
                    self._render_task_details(task_id, detailed_task)
                    
                    if detailed_task["status"] == "completed":
                        self._render_task_results(task_id)
                    
                    self._handle_task_actions(task_id, detailed_task)
    
    def _render_task_details(self, task_id: str, task_data: Dict):
        """Render detailed task information"""
        component_factory.create_task_metrics(task_data)
        
        # Progress chart
        fig = component_factory.create_progress_chart(task_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Real-time updates
        if task_id in st.session_state.get('task_updates', {}):
            latest_update = st.session_state.task_updates[task_id]
            st.subheader("Latest Update")
            st.json(latest_update)
    
    def _render_task_results(self, task_id: str):
        """Render task results for completed tasks"""
        results_data = api_service.get_task_results(task_id)
        if not results_data:
            st.info("Results will appear here when the task completes.")
            return
        
        st.subheader("Results")
        
        # Display results by agent
        results = results_data.get("results", {})
        for agent_type, agent_result in results.items():
            with st.expander(f"{agent_type.title()} Results"):
                if isinstance(agent_result, dict):
                    for key, value in agent_result.items():
                        if key == "timestamp":
                            st.text(f"**{key.title()}:** {value}")
                        elif isinstance(value, str) and len(value) > 100:
                            st.text_area(f"**{key.title()}:**", value, height=150)
                        else:
                            st.text(f"**{key.title()}:** {value}")
                else:
                    st.write(agent_result)
        
        # Final report
        if results_data.get("final_report"):
            st.subheader("Final Report")
            st.text_area("Report", results_data["final_report"], height=300)
    
    def _handle_task_actions(self, task_id: str, task_data: Dict):
        """Handle task action buttons"""
        actions = component_factory.create_task_action_buttons(task_id, task_data["status"])
        
        if actions.get("refresh"):
            st.rerun()
        
        if actions.get("connect_ws"):
            if websocket_manager.connect(task_id):
                st.success("WebSocket connected")
        
        if actions.get("cancel"):
            result = api_service.cancel_task(task_id)
            if result:
                st.success("Task cancelled")
                st.rerun()
    
    def _render_auto_refresh(self):
        """Render auto-refresh option"""
        if st.checkbox("Auto-refresh (every 5 seconds)"):
            time.sleep(5)
            st.rerun()

class SystemInfoPageHandler(PageHandler):
    """Handler for the System Info page"""
    
    def render(self):
        st.header("System Information")
        
        self._render_health_section()
        self._render_agents_section()
    
    def _render_health_section(self):
        """Render system health section"""
        health_data = api_service.get_health()
        if not health_data:
            return
        
        st.subheader("System Health")
        component_factory.create_health_metrics(health_data)
        
        features = health_data.get("features", {})
        if features:
            component_factory.create_features_display(features)
    
    def _render_agents_section(self):
        """Render agents information section"""
        agents_data = api_service.get_agents()
        if not agents_data:
            return
        
        st.subheader("Available Agents")
        
        agents = agents_data.get("agents", {})
        for agent_name, agent_info in agents.items():
            with st.expander(f"{agent_name.title()} Agent"):
                st.write(f"**Description:** {agent_info['description']}")
                st.write(f"**Capabilities:** {', '.join(agent_info['capabilities'])}")
        
        # Workflow info
        workflow = agents_data.get("workflow", {})
        if workflow:
            st.subheader("Workflow Configuration")
            for key, value in workflow.items():
                st.write(f"**{key.replace('_', ' ').title()}:** {value}")

# Page handler factory
class PageHandlerFactory:
    """Factory for creating page handlers"""
    
    @staticmethod
    def create_handler(page_name: str) -> PageHandler:
        """Create appropriate page handler based on page name"""
        handlers = {
            "Submit Task": SubmitTaskPageHandler(),
            "Monitor Tasks": MonitorTasksPageHandler(),
            "System Info": SystemInfoPageHandler()
        }
        
        return handlers.get(page_name, SubmitTaskPageHandler())