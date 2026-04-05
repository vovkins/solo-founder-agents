"""Agent factory for configuration-driven agent creation.

Architecture improvement D: Configuration-driven agent creation.
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from crewai import Agent

from config.settings import settings
from src.crews.base import LLMProvider
from src.tools import get_artifact_tools
from src.tools.github_tools import (
    create_github_issue_tool,
    list_open_issues_tool,
    read_file_from_repo_tool,
    create_branch_tool,
    create_pull_request_tool,
    get_pull_request_tool,
)
from src.tools.file_permissions import set_current_role, format_permissions_for_prompt

logger = logging.getLogger(__name__)


class AgentFactory:
    """Factory for creating agents from YAML configuration.
    
    Loads agent definitions from config/agents.yaml and creates
    Agent instances dynamically.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize factory with configuration.
        
        Args:
            config_path: Path to agents.yaml (default: config/agents.yaml)
        """
        self.config_path = Path(config_path or "config/agents.yaml")
        self._config: Dict[str, Any] = {}
        self._agents: Dict[str, Dict[str, Any]] = {}
        self._load_config()
        self._validate_prompts()  # Validate prompt files exist at startup
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            return
        
        with open(self.config_path, "r") as f:
            self._config = yaml.safe_load(f)
        
        # Index agents by name
        for agent_config in self._config.get("agents", []):
            name = agent_config["name"]
            self._agents[name] = agent_config
        
        logger.info(f"Loaded {len(self._agents)} agent configurations")
    
    def get_llm(self, llm_name: str):
        """Get LLM instance by name.
        
        Args:
            llm_name: LLM name (e.g., "z-ai/glm-5")
        
        Returns:
            LLM instance
        """
        llm_map = {
            "z-ai/glm-5": LLMProvider.get_pm_llm,  # Default
            "openai/gpt-5.1-codex-mini": LLMProvider.get_reviewer_llm,
        }
        
        return llm_map.get(llm_name, LLMProvider.get_pm_llm)()
    
    def get_tools(self, tool_names: List[str]) -> list:
        """Get tool instances by names.
        
        Args:
            tool_names: List of tool names
        
        Returns:
            List of tool instances
        """
        tools_map = {
            "save_artifact": get_artifact_tools(),
            "read_artifact": get_artifact_tools(),
            "create_github_issue": [create_github_issue_tool],
            "list_open_issues": [list_open_issues_tool],
            "read_file_from_repo": [read_file_from_repo_tool],
            "create_file_in_repo": [create_github_issue_tool],  # Simplified
            "create_branch": [create_branch_tool],
            "create_pull_request": [create_pull_request_tool],
            "get_pull_request": [get_pull_request_tool],
        }
        
        tools = []
        for name in tool_names:
            if name in tools_map:
                tool_or_list = tools_map[name]
                if isinstance(tool_or_list, list):
                    tools.extend(tool_or_list)
                else:
                    tools.extend(tool_or_list)
        
        return tools
    
    def load_backstory(self, backstory_file: str, role: str) -> str:
        """Load backstory from file with validation.

        Args:
            backstory_file: Path to backstory markdown file
            role: Agent role name

        Returns:
            Backstory string

        Raises:
            FileNotFoundError: If backstory file not found
            ValueError: If FILE_PERMISSIONS placeholder missing
        """
        backstory_path = Path(backstory_file)

        # VALIDATION: Check file exists
        if not backstory_path.exists():
            logger.error(f"Backstory file not found: {backstory_file}")
            raise FileNotFoundError(
                f"Backstory file not found: {backstory_file}. "
                f"All agents require a system prompt file in prompts/{{role}}/system-prompt.md"
            )

        # Load file
        try:
            with open(backstory_path, "r", encoding="utf-8") as f:
                backstory = f.read()
        except IOError as e:
            logger.error(f"Failed to read backstory file {backstory_file}: {e}")
            raise

        # VALIDATION: Check placeholder exists
        if "{{FILE_PERMISSIONS}}" not in backstory:
            logger.warning(
                f"Missing {{{{FILE_PERMISSIONS}}}} placeholder in {backstory_file}. "
                f"File permissions will not be injected for role \"{role}\"."
            )

        # Inject file permissions
        permissions_section = format_permissions_for_prompt(role)
        backstory = backstory.replace("{{FILE_PERMISSIONS}}", permissions_section)

        logger.info(f"Loaded backstory for {role} from {backstory_file} ({len(backstory)} chars)")
        return backstory



    def _validate_prompts(self) -> None:
        """Validate that all system prompt files exist at startup.

        Raises:
            FileNotFoundError: If any prompt file is missing
        """
        missing_files = []

        for agent_config in self._config.get("agents", []):
            name = agent_config.get("name")
            backstory_file = agent_config.get("backstory_file")

            if backstory_file:
                prompt_path = Path(backstory_file)
                if not prompt_path.exists():
                    missing_files.append(f"{name}: {backstory_file}")

        if missing_files:
            error_msg = f"Missing system prompt files:\n" + "\n".join(f"  - {f}" for f in missing_files)
            logger.error(error_msg)
            raise FileNotFoundError(
                f"Missing system prompt files. Please create all .md files in prompts/ directory.\n{error_msg}"
            )

        logger.info(f"Validated {len(self._config.get('''agents''', []))} agent prompt files - all present")

    def create_agent(self, agent_name: str) -> Agent:
        """Create an agent by name.
        
        Args:
            agent_name: Agent name (e.g., "pm", "analyst")
        
        Returns:
            Agent instance
        """
        if agent_name not in self._agents:
            raise ValueError(f"Agent not found in config: {agent_name}")
        
        config = self._agents[agent_name]
        
        # Create backstory
        backstory = self.load_backstory(
            config.get("backstory_file", f"prompts/{agent_name}/system-prompt.md"),
            config.get("permissions", agent_name)
        )
        
        # Get LLM
        llm = self.get_llm(config.get("llm", "z-ai/glm-5"))
        
        # Get tools
        tools = self.get_tools(config.get("tools", []))
        
        # Set role context
        set_current_role(config.get("permissions", agent_name))
        
        # Create agent
        agent = Agent(
            role=config.get("role", f"{agent_name.title()} Agent"),
            goal=config.get("goal", "Execute tasks"),
            backstory=backstory,
            llm=llm,
            tools=tools,
            verbose=config.get("verbose", True),
            allow_delegation=config.get("allow_delegation", False),
        )
        
        logger.info(f"Created agent: {agent_name}")
        return agent
    
    def list_agents(self) -> List[str]:
        """List all available agent names.
        
        Returns:
            List of agent names
        """
        return list(self._agents.keys())
    
    def get_agent_config(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for an agent.
        
        Args:
            agent_name: Agent name
        
        Returns:
            Agent configuration or None
        """
        return self._agents.get(agent_name)
    
    def reload_config(self) -> None:
        """Reload configuration from file."""
        self._load_config()
        self._validate_prompts()  # Validate prompt files exist at startup


# Global agent factory instance
agent_factory = AgentFactory()
