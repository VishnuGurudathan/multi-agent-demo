"""
Workflow Manager for LangGraph orchestration.
Moved from main.py to separate workflow management logic.
Handles graph creation, routing, and execution coordination.
"""
import logging
from typing import Callable, Dict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from ..models.enums import AgentRole
from ..models.agent_state import AgentState
from ..models import TaskStatus
from ..agents import SupervisorAgent, ResearcherAgent, AnalystAgent, WriterAgent, ReviewerAgent
from logger import setup_logger

logger = setup_logger(__name__)

class WorkflowManager:
    """
    Manages LangGraph workflow creation and execution.
    Coordinates agent routing and state management.
    """
    
    def __init__(self, config):
        self.config = config
        
        # Initialize agent instances
        self.agents = {
            AgentRole.SUPERVISOR: SupervisorAgent(config),
            AgentRole.RESEARCHER: ResearcherAgent(config),
            AgentRole.ANALYST: AnalystAgent(config),
            AgentRole.WRITER: WriterAgent(config),
            AgentRole.REVIEWER: ReviewerAgent(config)
        }
        
        # Create the workflow graph
        self.workflow = self._create_workflow()

    def _create_workflow(self) -> StateGraph:
        """
        AGENTIC PATTERN: LangGraph Multi-Agent Workflow Orchestration
        
        This method implements several sophisticated agentic patterns using LangGraph:
        
        1. GRAPH-BASED WORKFLOW MANAGEMENT:
           - Creates a state graph where each agent is a node
           - Enables complex routing between agents based on conditions
           - Supports both conditional and deterministic edges
        
        2. SUPERVISOR-WORKER ARCHITECTURE:
           - Supervisor as central orchestrator with conditional routing
           - Worker agents that return control to supervisor after completion
           - Hierarchical control flow with intelligent decision points
        
        3. STATE PERSISTENCE AND CHECKPOINTING:
           - MemorySaver enables workflow state persistence
           - Supports workflow resumption after failures
           - Maintains conversation history and intermediate results
        
        4. CONDITIONAL ROUTING LOGIC:
           - Supervisor makes dynamic routing decisions
           - Multiple possible paths based on task state and LLM decisions
           - Can terminate workflow or continue to different agents
        
        5. CYCLIC WORKFLOW SUPPORT:
           - Worker agents route back to supervisor for re-evaluation
           - Enables iterative refinement and multi-pass processing
           - Supervisor can route to same agent multiple times if needed
        """
        # Initialize LangGraph StateGraph with our AgentState model
        workflow = StateGraph(AgentState)
        memory = MemorySaver()  # STATE PERSISTENCE - Enable workflow checkpointing

        # GRAPH-BASED WORKFLOW MANAGEMENT - Register each agent as a workflow node
        logger.debug("Registering agents in workflow")
        for agent_role, agent_instance in self.agents.items():
            logger.debug(f"Adding agent node: {agent_role.value}")
            # Each agent becomes a node in the workflow graph
            workflow.add_node(agent_role.value, self._create_agent_wrapper(agent_instance))
    
        # SUPERVISOR-WORKER ARCHITECTURE - Set supervisor as workflow entry point
        # All workflows start with the supervisor making initial routing decisions
        workflow.set_entry_point(AgentRole.SUPERVISOR.value)
        
        # CONDITIONAL ROUTING LOGIC - Supervisor can route to any worker agent or end
        # This is where DYNAMIC LLM-BASED ROUTING is implemented at the graph level
        workflow.add_conditional_edges(
            AgentRole.SUPERVISOR.value,           # From supervisor
            self._supervisor_routing,             # Routing function (uses LLM decisions)
            {                                     # Possible destinations
                AgentRole.RESEARCHER.value: AgentRole.RESEARCHER.value,
                AgentRole.WRITER.value: AgentRole.WRITER.value,
                AgentRole.ANALYST.value: AgentRole.ANALYST.value,
                AgentRole.REVIEWER.value: AgentRole.REVIEWER.value,
                END: END                          # Workflow termination
            }
        )
        
        # CYCLIC WORKFLOW SUPPORT - All worker agents return to supervisor
        # This enables iterative processing and re-evaluation after each agent
        logger.info(f"non_supervisors {AgentRole.non_supervisors()}")
        for agent in AgentRole.non_supervisors():
            logger.info(f"Adding edge from {agent.value} to supervisor")
            # After each worker completes, control returns to supervisor
            workflow.add_edge(agent.value, AgentRole.SUPERVISOR.value)

        # Compile workflow with STATE PERSISTENCE AND CHECKPOINTING
        try:
            return workflow.compile(checkpointer=memory)
        except Exception as e:
            raise RuntimeError(f"Failed to compile workflow: {str(e)}")
    
    def _create_agent_wrapper(self, agent_instance):
        """Create a wrapper function for agent execution"""
        async def agent_wrapper(state: AgentState) -> AgentState:
            return await agent_instance.execute(state)
        return agent_wrapper
    
    def _supervisor_routing(self, state: AgentState) -> str:
        """
        AGENTIC PATTERN: LangGraph Conditional Edge Routing
        
        This method implements the routing logic that LangGraph uses to determine
        workflow transitions. It demonstrates several key agentic patterns:
        
        1. STATE-BASED ROUTING:
           - Routing decisions based on current workflow state
           - Considers task completion status and iteration limits
           - Uses supervisor's LLM-based decisions stored in state
        
        2. WORKFLOW TERMINATION LOGIC:
           - Intelligent workflow completion detection
           - Safety mechanisms (max iterations) to prevent infinite loops
           - Clear termination conditions for different scenarios
        
        3. DYNAMIC AGENT SELECTION:
           - Routes to agent selected by supervisor's LLM reasoning
           - Not hardcoded but based on intelligent analysis
           - Enables adaptive workflows based on task requirements
        
        This method is called by LangGraph's conditional edge system and translates
        the supervisor's intelligent decisions into actual workflow routing.
        """
        logger.info(f"Routing decision for task ID {state.task_id}")

        # WORKFLOW TERMINATION LOGIC - Check if workflow should end
        if state.status.value == TaskStatus.COMPLETED or state.iteration_count >= state.max_iterations:
            logger.info("Task marked complete or max iterations reached.")
            return END  # Terminate workflow

        # DYNAMIC AGENT SELECTION - Route to agent selected by supervisor's LLM
        # The next_agent was determined by the supervisor's intelligent analysis
        logger.info(f"Supervisor selected next agent: {state.next_agent} for task {state.task_id}")
        return state.next_agent  # Continue workflow to selected agent

    async def execute_workflow(self, initial_state: AgentState) -> AgentState:
        """Execute the complete workflow"""
        try:
            config = {"configurable": {"thread_id": initial_state.task_id}}
            
            logger.info(f"Starting workflow execution for task {initial_state.task_id}")
            # Run the workflow and get final state
            raw_final_state = await self.workflow.ainvoke(initial_state, config)
            
            # Convert returned dict to AgentState object if needed
            if isinstance(raw_final_state, dict):
                final_state = AgentState(**raw_final_state)
            else:
                final_state = raw_final_state
            
            logger.info(f"Workflow completed for task {initial_state.task_id}")
            return final_state
            
        except Exception as e:
            logger.error(f"Workflow execution error: {str(e)}", exc_info=True)
            initial_state.errors.append(f"Workflow error: {str(e)}")
            return initial_state
