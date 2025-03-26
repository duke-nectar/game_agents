from typing import Optional, List
from abc import ABC, abstractmethod
from pydantic.dataclasses import dataclass

@dataclass
class ActionSchema(ABC):
    """Base class for defining actions that can be executed by agents.
    
    Attributes:
        name: The name of the action
        description: A description of what the action does
        sub_actions: Optional list of sub-actions that this action can perform
    """
    name: str
    description: str
    sub_actions: Optional[List['ActionSchema']] = None

    @abstractmethod
    async def run(self, agent_state: AgentState) -> AgentState:
        """Perform the action and update the agent state.
        
        Args:
            agent_state: The current state of the agent
            
        Returns:
            agent_state: The updated state of the agent
            
        Raises:
            NotImplementedError: If the child class doesn't implement this method
        """
        pass