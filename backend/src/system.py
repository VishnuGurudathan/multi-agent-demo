"""
Multi-Agent System main controller.
Moved from main.py to backend/system.py for better organization.
Coordinates the entire multi-agent workflow execution.
"""
import logging
from datetime import datetime
from typing import Dict

from .models import AgentState, TaskStatus, TaskRequest
from .config import AgentConfig, get_max_iterations
from .workflows import WorkflowManager
from .utils.reporting import ReportGenerator
from .logger import setup_logger

logger = setup_logger(__name__)

class MultiAgentSystem:
    """
    Main controller for the multi-agent system.
    Orchestrates task processing through the LangGraph workflow.
    """
    
    def __init__(self):
        self.config = AgentConfig()
        self.workflow_manager = WorkflowManager(self.config)
        self.report_generator = ReportGenerator()
        self.active_tasks: Dict[str, AgentState] = {}
        self.max_iterations = get_max_iterations()
        
    async def process_task(self, task_request: TaskRequest) -> AgentState:
        """Process a task through the multi-agent system"""
        logger.info(f"Processing task: {task_request.task_id}")
        
        # Initialize state with all required fields
        initial_state = AgentState(
            messages=[],
            current_agent=None,
            next_agent=None,
            final_report=None,
            task_id=task_request.task_id,
            task_type=task_request.task_type,
            query=task_request.query,
            results={},
            status=TaskStatus.IN_PROGRESS,
            completed_agents=[],
            errors=[],
            metadata={},
            iteration_count=0,
            max_iterations=self.max_iterations
        )
        
        # Store active task
        self.active_tasks[task_request.task_id] = initial_state
        
        try:
            # Execute the workflow
            final_state = await self.workflow_manager.execute_workflow(initial_state)

            logger.info(f"Task {task_request.task_id} processed successfully")
            
            # Generate final report
            final_report = self.report_generator.generate_final_report(final_state)
            final_state.final_report = final_report

            # Update stored state
            self.active_tasks[task_request.task_id] = final_state
            
            logger.info(f"Task completed: {task_request.task_id}")
            return final_state
            
        except Exception as e:
            logger.error(f"Task processing error: {str(e)}", exc_info=True)
            initial_state.status = TaskStatus.FAILED
            initial_state.errors.append(f"Processing error: {str(e)}")
            return initial_state
    
    def get_task_status(self, task_id: str) -> AgentState:
        """Get current status of a task"""
        return self.active_tasks.get(task_id)
    
    def list_active_tasks(self) -> Dict[str, AgentState]:
        """List all active tasks"""
        return self.active_tasks
