from agent.base_agent import Agent
from typing import Dict
from memory.base_memory import AgentMemory
from state.actions import Actions
class AgentState:
    """
    Container class for all the agent states.
    - Passed as input to chains
    """
    def __init__(self,
                 agent:Agent,
                 current_goal:str,
                 location,
                 schedule = None,
                 knowledge = None ,
                 memory = None
                 ):
        self.location = location
        self.action = {"action":"idle","expired":True}
        self.agent = agent
        self.current_goal = current_goal
        #self.schedule = schedule
        #self.knowledge = knowledge
        self.available_actions = []
        self.all_available_actions = Actions(self.agent.all_available_actions)
        if memory is None:
            self.memory = AgentMemory(max_recent_size=20)
        else:
            self.memory = memory
    def update(self, observation:Dict):
        self.current_time =  observation.get("current_time", None)
        self.schedule.update(observation.get("schedule", None))
        self.knowledge.update(observation.get("knowledge", None))
        self.current_goal.update(observation.get("current_goal", None))
        self.memory.add_events(observation.get("events", None))
        