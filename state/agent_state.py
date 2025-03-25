from agent.base_agent import Agent
from typing import Dict 
from memory.base_memory import AgentMemory
from state.actions import Actions
from state.base_state import BaseState
from pydantic import BaseModel
import asyncio
import threading
from typing import List
from interaction.monitoring import Monitoring
from interaction.cognitive_module import CognitiveController
from interaction.action_executor import  TalkExecutor, MoveExecutor, FindExecutor
str_to_executor = {
    "talk": TalkExecutor,
    "move": MoveExecutor,
    "find": FindExecutor
}

class ObservationEvent(BaseModel):
    description: str
    agent_name: str
    target: str
    type: str


class Observation(BaseModel):
    current_time: str
    events: List[ObservationEvent]

class AgentState:
    """ 
    Container class for all the agent states.
    - Passed as input to chains
    """
    lock = threading.Lock()
    def __init__(self,
                 agent:Agent,
                 location,
                 current_time,
                 map,
                 monitoring_trigger = 5,
                 ):
        self.map = map
        self.location = location
        self.agent = agent
        self.current_goal = self.agent.goal
        self.current_time = current_time
        self.summary = self.agent.summary
        self.nearby_objects = None
        self.recent_events = []
        self.all_event_observation = []
        # Number of new events to trigger the self-monitoring module
        self.monitoring_trigger = monitoring_trigger
        self.current_conversation = None
        
        # Used to add the agent to the network
        self.relationships = {}
        self.action_controller = Actions(self.agent.all_available_actions) #Handle all the actions of the agent
        self.executor = None # execute the action
        self.executor_lock = threading.Lock()
        self.memory = AgentMemory(
            name=self.agent.name,
            max_recent_size=20,
            init_memory=self.agent.init_memory
        )
    # Main function, get observation from the game engine, update the agent state
    def add_relationship(self, agent_state:'AgentState'):
        self.relationships[agent_state.agent.name] = agent_state 
    #observation is the observation from the game engine
    # observation["events"] = [{"description":"description (action and goal)", "agent":"agent_name"},"target": "can be a location or an agent name","type":"move,talk,.."....]
    # observation["current_time"] = current time
    async def get_observation(self, observation:Observation):
        #Update the state   
        self.current_time =  observation.current_time 
        # The observation["events"] should be in form like a list of dictionaries
        # observation["events"] = [{"description":"description (action and goal)", "agent":"agent_name"},"target": "can be a location or an agent name","type":"move,talk,.."....]
        # This could be changed due to the game engine
        new_events = observation.events
        new_events = [event for event in new_events if event not in self.all_event_observation]
        #for event in new_events:
        #    if event.type == "talk" and event.target == self.agent.name:
        #        self.receive_utterance(event.description)
        # Stop if there is no new events
        if len(new_events) == 0:
            return 
        self.recent_events.extend(new_events)
        self.all_event_observation.extend(new_events)
        if len(self.recent_events) >= self.monitoring_trigger:
            thread = threading.Thread(target=self._update_summary_thread)
            thread.daemon = True
            thread.start()

        #TODO: Must check if receive the utterance from the other agent, and update the action controller
        # observation["talk"] = [{"from":"agent_name", "to":"agent_name", "utterance":"utterance"}....]
        should_call_coginitve = len(self.action_controller.get_available_actions()) > 0 
        if should_call_coginitve:
            self.executor = None
            action, goal = await CognitiveController.execute(self)
            with AgentState.lock:
                if self.executor is None:
                    self.update_action(action,goal)
                    if action == "talk":
                        executor = TalkExecutor(self.agent.name, self.relationships[goal.split(" ")[0]], " ".join(goal.split(" ")[1:]))
                        self.executor = executor
                        # if the other agent is already doing something, need to update the action too
                        # TODO: Need to check if the other agent is already doing something, and do it after talking with the current agent. 
                        if self.relationships[goal.split(":")[0]].executor is not None:
                            self.relationships[goal.split(":")[0]].update_action("talk", "")
                        self.relationships[goal.split(":")[0]].executor = executor
                    elif action == "move":
                        self.executor = MoveExecutor(goal)
                        # goal is like: "agent_name: The goal of the conversation"
        else:
            # Only 1 thread can use the executor at a time
            if hasattr(self.executor, "lock"):
                lock = self.executor.lock
            else:
                lock = self.executor_lock
            with lock:
                self.executor.execute(self)
            self.update_action()

        #self.schedule.update(observation.get("schedule", None))
        #self.knowledge.update(observation.get("knowledge", None))
    def _update_summary_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            new_summary = loop.run_until_complete(Monitoring.update_summary(self.current_goal,self.recent_events,self.summary))
            with self.lock:
                self.summary = new_summary
                self.memory.add_events(descriptions=[new_summary])
        finally:
            loop.close()
    @property
    def get_action_str(self):
        return self.action_controller.action_str
    @property
    def get_action_event(self):
        if self.action_controller.current_action["name"] == "move":
            sector = self.action_controller.sector if self.action_controller.sector is not None else ""
            arena = self.action_controller.arena if self.action_controller.arena is not None else ""
            to = f"{sector} {arena}"
        elif self.action_controller.current_action["name"] == "talk":
            to = self.action_controller.talking_with
        else:
            to = ""
        return ObservationEvent(description=self.get_action_str,from_agent=self.agent.name,to=to,type=self.action_controller.current_action["name"])
    def update_action(self,action:str | None,goal:str | None):
        self.action_controller.update(action,goal)
    # Module for the agent to perceive the environment and get the observation
    async def perceive(self):
        #TODO: Implement the perception module
        pass
    @property
    def cognitive_data(self):
        return {
            "persona_info":self.agent.get_information(),
            "current_goal":self.current_goal,
            "available_actions":self.action_controller.get_available_actions(),
            "recent_events": self.recent_events,
            "retrieved_events": self.memory.retrieve(queries=[self.current_goal])
        }