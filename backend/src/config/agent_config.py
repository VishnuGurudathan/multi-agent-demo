"""
Configuration module for agent setup and LLM initialization.
"""
import yaml
import sys
from pathlib import Path
from langchain_groq import ChatGroq
from ..models.enums import AgentRole
from ..utils.tools import AVAILABLE_TOOLS
from .settings import get_settings
from ..logger import setup_logger

logger = setup_logger(__name__)

# Add current directory to path to handle imports properly
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

class AgentConfig:
    """
    Configuration class for agent setup.
    Handles LLM initialization, prompt loading, and tool binding.
    """
    
    def __init__(self):
        # Get settings instance
        settings = get_settings()
        
        self.llm = ChatGroq(
            model=settings.MODEL_NAME,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
            groq_api_key=settings.GROQ_API_KEY
        )
        
        # Bind tools to LLM for agents that need them
        self.llm_with_tools = self.llm.bind_tools(AVAILABLE_TOOLS)
        
        # Load agent prompts from configuration
        self.agent_prompts = self._load_prompts()

    def _load_prompts(self) -> dict:
        """Load agent prompts from YAML configuration file"""
        prompt_file = Path(__file__).parent.parent.parent / "prompts" / "agent_prompts.yaml"
        logger.info(f"Loading agent prompts from {prompt_file}")
        try:
            with open(prompt_file, "r", encoding="utf-8") as f:
                raw_prompts = yaml.safe_load(f)

            # Map YAML keys to AgentRole enum members
            prompts = {
                AgentRole[key]: prompt
                for key, prompt in raw_prompts.items()
                if key in AgentRole.__members__
            }
            
            logger.info(f"Loaded prompts for agents: {list(prompts.keys())}")
            return prompts
            
        except Exception as e:
            logger.error(f"Failed to load agent prompts: {str(e)}")
            raise RuntimeError(f"Could not load agent prompts: {str(e)}")

# Global configuration settings (using settings module)
def get_max_iterations() -> int:
    """Get maximum iterations from settings"""
    return get_settings().MAX_ITERATIONS
