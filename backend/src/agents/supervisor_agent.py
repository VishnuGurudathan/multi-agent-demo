"""
Supervisor agent implementation.
Moved from main.py to separate orchestration logic.
Responsible for task routing and workflow coordination.
"""
import json
import logging
from datetime import datetime
from pydantic import ValidationError
from langchain_core.messages import SystemMessage, HumanMessage

from .base_agent import BaseAgent
from ..models.enums import AgentRole, TaskStatus
from ..models.responses import SupervisorDecision
from ..models.agent_state import AgentState
from ..logger import setup_logger

logger = setup_logger(__name__)

class SupervisorAgent(BaseAgent):
    """
    Supervisor agent for orchestrating multi-agent workflows.
    Routes tasks to appropriate agents and manages execution flow.
    """
    
    def __init__(self, config):
        super().__init__(config, AgentRole.SUPERVISOR)
        self.agent_capabilities = {
            AgentRole.SUPERVISOR: ["task_routing", "workflow_management", "quality_control"],
            AgentRole.RESEARCHER: ["data_gathering", "fact_checking", "source_verification"],
            AgentRole.WRITER: ["content_creation", "documentation", "storytelling"],
            AgentRole.ANALYST: ["data_analysis", "pattern_recognition", "insights"],
            AgentRole.REVIEWER: ["quality_assurance", "validation", "approval"]
        }
    
    async def execute(self, state: AgentState) -> AgentState:
        """
        AGENTIC PATTERN: Supervisor-Worker Hierarchical Orchestration
        
        This method implements the core supervisor pattern in multi-agent systems:
        
        1. CENTRALIZED COORDINATION:
           - Single point of control for workflow orchestration
           - Maintains global view of task progress and agent states
           - Makes high-level decisions about workflow progression
        
        2. ITERATION CONTROL:
           - Prevents infinite loops with max iteration limits
           - Tracks workflow progress through iteration counting
           - Provides safety mechanism for complex or problematic tasks
        
        3. INTELLIGENT WORKFLOW MANAGEMENT:
           - Uses LLM-based decision making for dynamic routing
           - Adapts workflow based on current state and completed work
           - Can terminate workflow when objectives are met
        
        4. STATE MANAGEMENT:
           - Updates shared state with routing decisions and reasoning
           - Maintains audit trail of supervisor decisions
           - Coordinates state transitions between agents
        
        5. ERROR HANDLING AND RECOVERY:
           - Graceful error handling with detailed logging
           - Maintains system stability even when individual decisions fail
           - Provides clear error reporting for debugging
        """
        self.logger.info(f"Supervisor processing task: {state.task_id}")
        
        try:
            # ITERATION CONTROL - Prevent infinite loops and track progress
            state.iteration_count = (state.iteration_count or 0) + 1
            
            # Safety mechanism: Check max iteration limit to prevent runaway workflows
            if state.iteration_count >= state.max_iterations:
                self.logger.warning(f"Max iterations ({state.max_iterations}) reached for task {state.task_id}")
                state.status = TaskStatus.COMPLETED
                state.next_agent = None
                return state
            
            # INTELLIGENT WORKFLOW MANAGEMENT - Core supervisor decision making
            # This is where the supervisor analyzes current state and decides next steps
            decision = await self._make_routing_decision(state)
            
            # STATE MANAGEMENT - Update workflow state based on supervisor decision
            state.current_agent = self.role.value
            state.next_agent = decision.get("next_agent")
            
            # CENTRALIZED COORDINATION - Determine if workflow should continue or complete
            if decision.get("completed", False) or not state.next_agent:
                # Supervisor has determined all necessary work is complete
                state.status = TaskStatus.COMPLETED
                state.next_agent = None
                self.logger.info("Task marked as completed by supervisor")
            else:
                # Continue workflow with next selected agent
                self.logger.info(f"Supervisor routed task to: {state.next_agent}")

            # STATE MANAGEMENT - Add supervisor decision to audit trail
            # This maintains transparency and enables debugging of routing decisions
            self._add_message_to_state(
                state, 
                f"Routing decision: {decision['reason']}", 
                {"decision": decision}
            )
            
            return state
            
        except Exception as e:   
            # ERROR HANDLING AND RECOVERY - Maintain system stability
            self.logger.error(f"Supervisor error: {str(e)}", exc_info=True)
            state.errors.append(f"Supervisor error: {str(e)}")
            state.status = TaskStatus.FAILED
            return state
    
    async def _make_routing_decision(self, state: AgentState) -> dict:
        """
        AGENTIC PATTERN: Dynamic LLM-Based Routing
        
        This method implements sophisticated dynamic routing where the supervisor agent
        uses an LLM to make intelligent decisions about which agent should execute next.
        This is a key agentic pattern that enables:
        
        1. CONTEXT-AWARE DECISION MAKING:
           - Analyzes current task state, completed work, and remaining iterations
           - Considers task type and query content to determine optimal agent sequence
           - Makes decisions based on accumulated results from previous agents
        
        2. INTELLIGENT ORCHESTRATION:
           - Not hardcoded rules but LLM-driven reasoning about workflow optimization
           - Can adapt to unexpected situations or complex task requirements
           - Balances efficiency (avoiding unnecessary agents) with completeness
        
        3. STRUCTURED DECISION OUTPUT:
           - Returns JSON with next_agent, completion status, and reasoning
           - Enables transparent decision tracking and debugging
           - Allows for complex conditional logic beyond simple if/else rules
        
        4. STATE-DEPENDENT ROUTING:
           - Routing decisions change based on what work has already been completed
           - Can skip agents if their work is already done or unnecessary
           - Can determine when sufficient work has been completed to end the workflow
        """
        # Get available agents - this provides the LLM with the full agent ecosystem
        available_agents = list(self.agent_capabilities.keys())

        # Format prompt with comprehensive context for intelligent decision making
        # This is where CONTEXT-AWARE DECISION MAKING is implemented
        prompt_data = {
            "query": state.query,                    # Original user request
            "task_type": state.task_type or "general",  # Task classification
            "available_agents": available_agents,    # All possible agents
            "completed_agents": state.completed_agents or [],  # Work already done
            "iteration_count": state.iteration_count or 0,     # Current iteration
            "max_iterations": state.max_iterations or 10       # Iteration limit
        }
        prompt = self.config.agent_prompts[AgentRole.SUPERVISOR].format_map(prompt_data)
        
        # LangChain LLM call - this is where INTELLIGENT ORCHESTRATION happens
        # The LLM analyzes all context and makes a reasoned decision
        messages = [
            SystemMessage(content=prompt),  # Instructions and context
            HumanMessage(content=f"Current state: {json.dumps(state.results, indent=2)}")  # Current results
        ]
        response = await self.config.llm.ainvoke(messages)

        # Parse decision - converts LLM response to structured routing decision
        return self._parse_supervisor_decision(response.content, state)
    
    def _parse_supervisor_decision(self, response: str, state: AgentState) -> dict:
        """
        AGENTIC PATTERN: Structured Decision Output with Graceful Degradation
        
        This method demonstrates several advanced agentic patterns:
        
        1. STRUCTURED DECISION OUTPUT:
           - Attempts to parse LLM response as structured JSON first
           - Uses Pydantic models (SupervisorDecision) for type safety and validation
           - Ensures consistent decision format across all routing decisions
        
        2. GRACEFUL DEGRADATION:
           - If LLM doesn't return valid JSON, falls back to heuristic parsing
           - Maintains system reliability even when LLM output is malformed
           - Combines AI intelligence with rule-based backup logic
        
        3. MULTI-LAYERED DECISION LOGIC:
           - Primary: LLM-based structured reasoning (preferred)
           - Secondary: Natural language keyword detection
           - Tertiary: Rule-based heuristics (fallback)
        
        4. STATE-DEPENDENT ROUTING:
           - Fallback rules consider completed agents to avoid redundant work
           - Task type and query content influence agent selection
           - Progressive workflow (research → analysis → writing → review)
        
        This pattern ensures robust decision making while maintaining AI-driven intelligence.
        """
        self.logger.info(f"Parsing supervisor decision for task: {state.task_id}")
        response_lower = response.lower()
        self.logger.debug(f"Parsing supervisor decision from response: {response_lower}")

        try:
            # STRUCTURED DECISION OUTPUT - Primary parsing method
            # Try to parse LLM response as structured JSON for consistent decision format
            decision_dict = json.loads(response)
            decision = SupervisorDecision(**decision_dict)  # Pydantic validation
            self.logger.info(f"Parsed decision: {decision}")
            return decision.model_dump()
        except (json.JSONDecodeError, ValidationError):
            # GRACEFUL DEGRADATION - When structured parsing fails
            self.logger.warning("Structured parse failed, falling back to heuristic rules...")
    
        # Natural language completion detection - Secondary parsing method
        if any(kw in response_lower for kw in ["task_complete", "done", "completed"]):
            return {"completed": True, "next_agent": None, "reason": "Task marked complete by LLM"}

        # STATE-DEPENDENT ROUTING - Tertiary fallback with rule-based logic
        # This ensures system continues to function even with poor LLM responses
        completed = state.completed_agents or []
        rules = [
            # Research first for research tasks or when research keywords detected
            ("researcher", lambda: state.task_type == "research" or "research" in state.query.lower()),
            # Analysis for analysis tasks or analysis keywords
            ("analyst", lambda: state.task_type == "analysis" or "analysis" in state.query.lower()),
            # Writing when write keywords present or after other agents have worked
            ("writer", lambda: "write" in state.query.lower() or len(completed) > 0),
            # Review when multiple agents have completed work (quality assurance)
            ("reviewer", lambda: len(completed) > 1),
        ]

        # Apply rules in order, selecting first applicable agent not yet completed
        for agent, condition in rules:
            if agent not in completed and condition():
                return {"next_agent": agent, "completed": False, "reason": f"{agent.title()} needed"}

        # If no rules match, assume all work is completed
        return {"completed": True, "next_agent": None, "reason": "All work completed"}
