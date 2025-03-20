from agent.base_agent import Agent
from typing import Dict
from memory.base_memory import AgentMemory
from state.actions import Actions
from state.base_state import BaseState
class AgentState(BaseState):
    """
    Container class for all the agent states.
    - Passed as input to chains
    """
    def __init__(self,
                 agent:Agent,
                 location,
                 schedule = None,
                 knowledge = None ,
                 memory = None
                 ):
        self.location = location
        self.agent = agent
        self.current_goal = self.agent.goal
        self.current_time = None
        #self.schedule = schedule
        #self.knowledge = knowledge
        self.action_controller = Actions(self.agent.all_available_actions)
        if memory is None:
            self.memory = AgentMemory(max_recent_size=20,init_memory=self.agent.init_memory)
        else:
            self.memory = memory
    async def update(self, observation:Dict):
        #Update the state 
        self.current_time =  observation.get("current_time", None)
        #self.schedule.update(observation.get("schedule", None))
        #self.knowledge.update(observation.get("knowledge", None))
        self.current_goal.update(observation.get("current_goal", None))
        await self.memory.add_events(observation.get("events", None),self)
        self.action_controller.update(observation.get("action", None))
        