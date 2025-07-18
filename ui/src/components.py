"""
UI Components factory
Creates reusable UI components following the Factory pattern
"""
import streamlit as st
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
from ui_config import UIConfig

class ComponentFactory:
    """Factory for creating UI components"""
    
    @staticmethod
    def create_progress_chart(task_data: Dict) -> Optional[go.Figure]:
        """Create a progress visualization chart"""
        if not task_data:
            return None
        
        completed_agents = task_data.get("completed_agents", [])
        current_agent = task_data.get("current_agent")
        
        # Create status for each agent
        agent_status = []
        for agent in UIConfig.AGENT_LIST:
            if agent.lower() in [a.lower() for a in completed_agents]:
                agent_status.append("Completed")
            elif current_agent and agent.lower() == current_agent.lower():
                agent_status.append("In Progress")
            else:
                agent_status.append("Pending")
        
        # Create the chart
        fig = go.Figure()
        
        for status in ["Completed", "In Progress", "Pending"]:
            agent_indices = [i for i, s in enumerate(agent_status) if s == status]
            if agent_indices:
                fig.add_trace(go.Bar(
                    x=[UIConfig.AGENT_LIST[i] for i in agent_indices],
                    y=[1] * len(agent_indices),
                    name=status,
                    marker_color=UIConfig.CHART_COLORS[status],
                    text=status,
                    textposition="inside"
                ))
        
        fig.update_layout(
            title="Agent Progress",
            yaxis=dict(showticklabels=False, range=[0, 1.2]),
            barmode="group",
            height=300,
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def create_task_metrics(task_data: Dict):
        """Create task metrics display"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Task Status", task_data.get("status", "Unknown"))
            st.metric("Current Agent", task_data.get("current_agent", "None"))
            st.metric("Progress", f"{task_data.get('progress', 0):.1f}%")
        
        with col2:
            st.metric(
                "Iteration", 
                f"{task_data.get('iteration_count', 0)}/{task_data.get('max_iterations', 10)}"
            )
            st.metric("Completed Agents", len(task_data.get("completed_agents", [])))
            st.metric("Errors", len(task_data.get("errors", [])))
    
    @staticmethod
    def create_task_form() -> Dict:
        """Create task submission form"""
        with st.form("task_form"):
            query = st.text_area(
                "Task Description",
                placeholder="Describe what you'd like the AI agents to accomplish",
                height=120
            )
            
            col1, col2 = st.columns(2)
            with col1:
                task_type = st.selectbox("Task Type", UIConfig.TASK_TYPES)
            with col2:
                priority = st.select_slider(
                    "Priority", 
                    options=[1, 2, 3, 4, 5],
                    value=3,
                    format_func=lambda x: f"{'⭐' * x}"
                )
            
            submitted = st.form_submit_button(
                "Submit Task",
                use_container_width=True,
                type="primary"
            )
            
            return {
                "query": query,
                "task_type": task_type,
                "priority": priority,
                "submitted": submitted
            }
    
    @staticmethod
    def create_health_metrics(health_data: Dict):
        """Create system health metrics display"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Status", health_data.get("status", "Unknown"))
        with col2:
            st.metric("Active Tasks", health_data.get("active_tasks", 0))
        with col3:
            st.metric("Version", health_data.get("version", "Unknown"))
    
    @staticmethod
    def create_features_display(features: Dict):
        """Create features display"""
        st.subheader("Features")
        for feature, enabled in features.items():
            status = "✅" if enabled else "❌"
            st.write(f"{status} **{feature.replace('_', ' ').title()}:** {enabled}")
    
    @staticmethod
    def create_task_action_buttons(task_id: str, task_status: str) -> Dict:
        """Create task action buttons"""
        col1, col2, col3 = st.columns(3)
        actions = {}
        
        with col1:
            actions["refresh"] = st.button(f"Refresh {task_id[:8]}", key=f"refresh_{task_id}")
        
        with col2:
            actions["connect_ws"] = st.button(f"Connect WS {task_id[:8]}", key=f"ws_{task_id}")
        
        with col3:
            if task_status not in ["completed", "failed"]:
                actions["cancel"] = st.button(f"Cancel {task_id[:8]}", key=f"cancel_{task_id}")
            else:
                actions["cancel"] = False
        
        return actions
    
    @staticmethod
    def create_task_id_display(task_id: str):
        """Create a task ID display"""
        st.code(f"Task ID: {task_id}", language=None)



# Create instance for use across the application
component_factory = ComponentFactory()