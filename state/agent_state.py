from agent.base_agent import Agent
from typing import Dict 
from memory.base_memory import AgentMemory
from state.actions import Actions
from state.base_state import BaseState
import threading
from interaction.monitoring import Monitoring
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

        #Lock for thread-safe
        self.lock = threading.Lock()
        #self.schedule = schedule
        #self.knowledge = knowledge
        self.related_events = []
        self.action_controller = Actions(self.agent.all_available_actions)
        if memory is None:
            self.memory = AgentMemory(max_recent_size=20,init_memory=self.agent.init_memory)
        else:
            self.memory = memory
    async def get_observation(self, observation:Dict):
        #Update the state 
        self.current_time =  observation.get("current_time", self.current_time)
        #self.schedule.update(observation.get("schedule", None))
        #self.knowledge.update(observation.get("knowledge", None))
        await self.memory.add_events(observation.get("event", None),self)
        self.related_events = self.memory.retrieve(observation.get("event", None))
        new_goal = Monitoring.update(self,observation.get("event", None))
        with self.lock:
            await self.update_goal(new_goal)
    async def update_goal(self,goal:str):
        self.current_goal = goal
    async def update_action(self,action:str | None):
        self.action_controller.update(action)