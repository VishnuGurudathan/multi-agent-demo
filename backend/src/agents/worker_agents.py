"""
Worker agent implementations.
Moved from main.py to separate individual agent logic.
Each agent has a specific responsibility (research, analysis, writing, review).
"""
import json
import logging
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

from .base_agent import BaseAgent
from ..models.enums import AgentRole
from ..models.agent_state import AgentState
from ..utils.tools import AVAILABLE_TOOLS
from ..logger import setup_logger  # Fixed: Use relative import

logger = setup_logger(__name__)

class ResearcherAgent(BaseAgent):
    """Agent specialized in information gathering and research"""
    
    def __init__(self, config):
        super().__init__(config, AgentRole.RESEARCHER)
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute research tasks"""
        logger.info(f"Researcher processing task: {state.task_id}")
        
        try:
            # Count previous runs for this agent
            agent_run_count = sum(
                1 for msg in state.messages if msg.get("agent") == self.role.value
            )
            logger.info(f"Researcher has run {agent_run_count} times for this task")

            if agent_run_count >= 3:
                logger.warning(f"Researcher agent has already run {agent_run_count} times")

            # Format prompt
            prompt = self.config.agent_prompts[self.role].format(query=state.query)
            logger.debug(f"Formatted research prompt for query: {state.query[:100]}...")

            # Construct messages for LLM
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=state.query)
            ]
            logger.debug(f"Constructed {len(messages)} messages for LLM")

            # Use LLM with tools for research
            logger.info("Invoking LLM with tools for research")
            
            # Use the base class helper method for tool execution
            final_response, tool_calls = await self._execute_with_tools(messages, use_tools=True)

            # Save final research findings in state
            state.results["research"] = {
                "findings": final_response.content,
                "timestamp": datetime.now().isoformat(),
                "agent": self.role.value,
                "tool_calls": tool_calls
            }
            logger.debug("Research results stored in state")

            # Update agent state
            self._add_message_to_state(state, final_response.content)
            self._mark_agent_completed(state)
            logger.info("Research completed successfully")
            return state
            
        except Exception as e:
            logger.error(f"Researcher error: {str(e)}", exc_info=True)
            state.errors.append(f"Researcher error: {str(e)}")
            return state

class AnalystAgent(BaseAgent):
    """Agent specialized in data analysis and insights"""
    
    def __init__(self, config):
        super().__init__(config, AgentRole.ANALYST)
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute analysis tasks"""
        logger.info(f"Analyst processing task: {state.task_id}")
        
        try:
            # Get available data for analysis
            analysis_data = {
                "research": state.results.get("research", {}),
                "writing": state.results.get("writing", {})
            }
            logger.info(f"Analysis data collected: {list(analysis_data.keys())}")
            
            prompt = self.config.agent_prompts[self.role].format(query=state.query)
            logger.debug(f"Formatted analysis prompt for query: {state.query[:100]}...")
            
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=f"{state.query}\n\nData to analyze: {json.dumps(analysis_data, indent=2)}")
            ]
            logger.debug(f"Constructed {len(messages)} messages for analysis")
            
            logger.info("Invoking LLM for analysis")
            response = await self.config.llm.ainvoke(messages)
            logger.info(f"Analysis response received, content length: {len(response.content)}")

            # Store analysis results
            state.results["analysis"] = {
                "insights": response.content,
                "timestamp": datetime.now().isoformat(),
                "agent": self.role.value
            }
            logger.debug("Analysis results stored in state")
            
            # Update state
            self._add_message_to_state(state, response.content)
            self._mark_agent_completed(state)
            logger.info("State updated and analyst marked as completed")
            
            logger.info("Analysis completed successfully")
            return state
            
        except Exception as e:
            logger.error(f"Analyst error: {str(e)}", exc_info=True)
            state.errors.append(f"Analyst error: {str(e)}")
            return state

class WriterAgent(BaseAgent):
    """Agent specialized in content creation and writing"""
    
    def __init__(self, config):
        super().__init__(config, AgentRole.WRITER)
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute writing tasks"""
        logger.info(f"Writer processing task: {state.task_id}")
        
        try:
            # Build context from research and analysis
            logger.debug("Building context for writer from previous agent results")
            full_context = self._build_context_for_writer(state)
            logger.info(f"Writer context built, length: {len(full_context)}")

            # Enhanced prompt with dynamic context integration
            enhanced_prompt = self.config.agent_prompts[self.role].format(
                query=state.query,
                context=full_context,
                task_type=state.task_type or "general"
            )
            logger.debug(f"Enhanced writing prompt created for task type: {state.task_type or 'general'}")
            
            messages = [
                SystemMessage(content=enhanced_prompt),
                HumanMessage(content=state.query)
            ]
            logger.debug(f"Constructed {len(messages)} messages for writing")
            
            logger.info("Invoking LLM for content writing")
            response = await self.config.llm.ainvoke(messages)
            logger.info(f"Writing response received, content length: {len(response.content)}")
            
            # Store writing results
            state.results["writing"] = {
                "content": response.content,
                "timestamp": datetime.now().isoformat(),
                "agent": self.role.value
            }
            logger.debug("Writing results stored in state")
            
            # Update state
            self._add_message_to_state(state, response.content)
            self._mark_agent_completed(state)
            logger.info("State updated and writer marked as completed")
            
            logger.info("Writing completed successfully")
            return state
            
        except Exception as e:
            logger.error(f"Writer error: {str(e)}", exc_info=True)
            state.errors.append(f"Writer error: {str(e)}")
            return state
    
    def _build_context_for_writer(self, state: AgentState) -> str:
        """Aggregate research, analysis, and supervisor context into a single string."""
        logger.debug("Building context for writer from state results")
        context_parts = []

        if "research" in state.results:
            context_parts.append(f"RESEARCH FINDINGS:\n{state.results['research']['findings']}")
            logger.debug("Added research findings to writer context")

        if "analysis" in state.results:
            context_parts.append(f"ANALYSIS INSIGHTS:\n{state.results['analysis']['insights']}")
            logger.debug("Added analysis insights to writer context")

        supervisor_guidance = self._extract_supervisor_guidance(state.messages)
        if supervisor_guidance:
            context_parts.append(f"SUPERVISOR GUIDANCE:\n{supervisor_guidance}")
            logger.debug("Added supervisor guidance to writer context")

        result = "\n\n".join(context_parts) if context_parts else "No previous context available."
        logger.debug(f"Writer context completed with {len(context_parts)} sections")
        return result
    
    def _extract_supervisor_guidance(self, messages) -> str:
        """Extract the latest supervisor decision guidance from messages."""
        logger.debug("Extracting supervisor guidance from messages")
        
        if not messages:
            logger.debug("No messages available for supervisor guidance extraction")
            return ""
        
        supervisor_messages = [
            msg for msg in messages
            if msg.get("agent") == AgentRole.SUPERVISOR.value and "decision" in msg
        ]
        logger.debug(f"Found {len(supervisor_messages)} supervisor messages with decisions")

        if not supervisor_messages:
            logger.debug("No supervisor guidance found in messages")
            return ""
        
        latest_guidance = supervisor_messages[-1].get("decision", {})
        logger.debug("Extracted latest supervisor guidance")
        return json.dumps(latest_guidance, indent=2)

class ReviewerAgent(BaseAgent):
    """Agent specialized in quality assurance and validation"""
    
    def __init__(self, config):
        super().__init__(config, AgentRole.REVIEWER)
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute review tasks"""
        logger.info(f"Reviewer processing task: {state.task_id}")
        
        try:
            # Get all completed work for review
            work_to_review = {
                "research": state.results.get("research", {}),
                "writing": state.results.get("writing", {}),
                "analysis": state.results.get("analysis", {})
            }
            logger.info(f"Work collected for review: {list(work_to_review.keys())}")
            
            prompt = self.config.agent_prompts[self.role].format(query=state.query)
            logger.debug(f"Formatted review prompt for query: {state.query[:100]}...")
            
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=f"Review the following work:\n{json.dumps(work_to_review, indent=2)}")
            ]
            logger.debug(f"Constructed {len(messages)} messages for review")
            
            logger.info("Invoking LLM for quality review")
            response = await self.config.llm.ainvoke(messages)
            logger.info(f"Review response received, content length: {len(response.content)}")
            
            # Store review results
            state.results["review"] = {
                "assessment": response.content,
                "timestamp": datetime.now().isoformat(),
                "agent": self.role.value
            }
            logger.debug("Review results stored in state")
            
            # Update state
            self._add_message_to_state(state, response.content)
            self._mark_agent_completed(state)
            logger.info("State updated and reviewer marked as completed")
            
            logger.info("Review completed successfully")
            return state
            
        except Exception as e:
            logger.error(f"Reviewer error: {str(e)}", exc_info=True)
            state.errors.append(f"Reviewer error: {str(e)}")
            return state
