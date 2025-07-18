"""
Agent-related API routes.
Provides information about available agents and their capabilities.
"""
from fastapi import APIRouter, Depends

from ...config.settings import get_settings, BackendSettings

router = APIRouter()

@router.get("")
async def get_agent_info(settings: BackendSettings = Depends(get_settings)):
    """Get information about available agents"""
    from ...models.enums import AgentRole, AGENT_CAPABILITIES
    
    return {
        "agents": {
            role.value: {
                "role": role.value,
                "capabilities": role.capabilities,
                "description": f"{role.value.title()} agent for {', '.join(role.capabilities)}"
            }
            for role in AgentRole
        },
        "workflow": {
            "entry_point": AgentRole.SUPERVISOR.value,
            "routing": "Dynamic routing based on task requirements",
            "max_iterations": settings.MAX_ITERATIONS,
            "max_agents": settings.MAX_AGENTS
        }
    }
