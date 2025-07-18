"""
Base agent class for common agent functionality.
Provides common structure for all agent implementations.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from langchain_core.messages import ToolMessage
from ..models.agent_state import AgentState
from ..models.enums import AgentRole
from ..logger import setup_logger

logger = setup_logger(__name__)

class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    Implements common agent functionality and defines the interface.
    """
    
    def __init__(self, config, role: AgentRole):
        self.config = config
        self.role = role
        self.logger = setup_logger(f"{__name__}.{role.value}")
        
    @abstractmethod
    async def execute(self, state: AgentState) -> AgentState:
        """Execute the agent's primary function"""
        pass
    
    async def _execute_with_tools(self, messages: list, use_tools: bool = True):
        """
        Execute LLM with tools and handle tool calls automatically.
        
        Args:
            messages: List of messages to send to LLM
            use_tools: Whether to use tools-enabled LLM or regular LLM
            
        Returns:
            Final response after tool execution (if any)
        """
        # Choose LLM based on whether tools are needed
        llm = self.config.llm_with_tools if use_tools else self.config.llm
        
        # Get initial response
        self.logger.info(f"Invoking LLM {'with tools' if use_tools else 'without tools'}")
        initial_response = await llm.ainvoke(messages)
        self.logger.info(f"Initial response received, content length: {len(initial_response.content)}")
        
        # Default to initial response
        final_response = initial_response
        
        # Handle tool calls if present
        if use_tools and hasattr(initial_response, 'tool_calls') and initial_response.tool_calls:
            self.logger.info(f"Tool calls detected: {len(initial_response.tool_calls)} calls")
            
            # Execute tools
            tool_outputs = await self._execute_tools(initial_response.tool_calls)
            
            if tool_outputs:
                # Re-invoke LLM with tool outputs
                messages_with_tools = messages.copy()
                messages_with_tools.append(initial_response)  # Add the initial response with tool calls
                messages_with_tools.extend(tool_outputs)
                
                self.logger.info("Re-invoking LLM with tool outputs")
                final_response = await self.config.llm.ainvoke(messages_with_tools)
                self.logger.info(f"Final response received, content length: {len(final_response.content)}")
                self.logger.debug(f"Final LLM content (excerpt): {final_response.content[:200] if final_response.content else 'No content'}")
        
        elif use_tools:
            self.logger.info("No tool calls detected in LLM response")
            if not initial_response.content:
                self.logger.warning("LLM returned empty response - this may indicate API key issues")
        
        return final_response, getattr(initial_response, 'tool_calls', [])
    
    async def _execute_tools(self, tool_calls: list) -> list:
        """
        Execute a list of tool calls and return ToolMessage objects.
        
        Args:
            tool_calls: List of tool call dictionaries from LLM response
            
        Returns:
            List of ToolMessage objects with tool results
        """
        from ..utils.tools import AVAILABLE_TOOLS
        
        tool_outputs = []
        
        for tool_call in tool_calls:
            try:
                tool_name = tool_call['name']
                args = tool_call['args']
                tool_id = tool_call['id']
                
                # Find the tool
                tool = next((t for t in AVAILABLE_TOOLS if t.name == tool_name), None)
                if not tool:
                    self.logger.warning(f"Tool {tool_name} not found in available tools")
                    continue
                
                self.logger.info(f"Executing tool: {tool_name} with args: {args}")
                
                # Execute the tool
                tool_result = tool.invoke(args)
                tool_outputs.append(ToolMessage(content=str(tool_result), tool_call_id=tool_id))
                
                self.logger.info(f"Tool {tool_name} executed successfully, result length: {len(str(tool_result))}")
                
            except Exception as e:
                self.logger.error(f"Error executing tool {tool_name}: {str(e)}")
                # Add error message as tool output
                tool_outputs.append(ToolMessage(
                    content=f"Error executing {tool_name}: {str(e)}", 
                    tool_call_id=tool_call.get('id', 'unknown')
                ))
        
        return tool_outputs
    
    def _add_message_to_state(self, state: AgentState, content: str, metadata: dict = None):
        """Helper method to add agent message to state"""
        message = {
            "agent": self.role.value,
            "timestamp": datetime.now().isoformat(),
            "content": content
        }
        if metadata:
            message.update(metadata)
        
        state.messages.append(message)
        
    def _mark_agent_completed(self, state: AgentState):
        """Mark this agent as completed in the state"""
        if self.role.value not in state.completed_agents:
            state.completed_agents.append(self.role.value)
        state.current_agent = self.role.value
