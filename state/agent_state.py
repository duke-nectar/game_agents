from agent.base_agent import Agent
from typing import Dict 
from memory.base_memory import AgentMemory
from state.actions import Actions
from state.base_state import BaseState
import asyncio
import threading
from interaction.monitoring import Monitoring
from interaction.cognitive_module import CognitiveController
class AgentState(BaseState):
    """
    Container class for all the agent states.
    - Passed as input to chains
    """
    def __init__(self,
                 agent:Agent,
                 location,
                 monitoring_trigger = 5,
                 schedule = None,
                 knowledge = None ,
                 memory = None
                 ):
        self.location = location
        self.agent = agent
        self.current_goal = self.agent.goal
        self.current_time = None
        self.summary = self.agent.summary
        self.nearby_objects = None
        self.recent_events = []
        self.all_event_observation = []
        # Number of new events to trigger the self-monitoring module
        self.monitoring_trigger = monitoring_trigger
        #Lock for thread-safe
        self.lock = threading.Lock()
        #self.schedule = schedule
        #self.knowledge = knowledge
        #self.related_events = []
        self.action_controller = Actions(self.agent.all_available_actions) #Handle all the actions of the agent
        if memory is None:
            self.memory = AgentMemory(max_recent_size=20,init_memory=self.agent.init_memory)
            # Add the initial summary to the memory
            self.memory.add_event(description=self.summary)
        else:
            self.memory = memory

    # Main function, get observation from the game engine, update the agent state
    async def get_observation(self, observation:Dict):
        #Update the state 
        self.current_time =  observation.get("current_time", self.current_time)
        # The observation["events"] should be in form like a list of dictionaries
        # observation["events"] = [{"description":"description (action and goal)", "agent":"agent_name"},....]
        # This could be changed due to the game engine
        new_events = observation.get("events", [])
        new_events = [event for event in new_events if event not in self.all_event_observation]
        self.recent_events.extend(new_events)
        self.all_event_observation.extend(new_events)
        if len(self.recent_events) >= self.monitoring_trigger:
            thread = threading.Thread(target=self._update_summary_thread)
            thread.daemon = True
            thread.start()

        #TODO: Must check if receive the utterance from the other agent, and update the action controller
        # observation["talk"] = [{"from":"agent_name", "to":"agent_name", "utterance":"utterance"}....]
        for talk in observation["talk"]:
            if talk["to"] == self.agent.name:
                self.receive_utterance(talk["utterance"])
        should_call_coginitve = len(self.action_controller.get_available_actions()) > 0 
        if should_call_coginitve:
            action, goal = await CognitiveController.execute(self)
            with self.lock:
                self.update_action(action,goal)
        #else:

        #self.schedule.update(observation.get("schedule", None))
        #self.knowledge.update(observation.get("knowledge", None))
    def _update_summary_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            new_summary = loop.run_until_complete(Monitoring.update_summary(self))
            with self.lock:
                self.summary = new_summary
                self.memory.add_events(descriptions=[new_summary])
        finally:
            loop.close()
    def update_action(self,action:str | None,goal:str | None):
        self.action_controller.update(action,goal)
    def receive_utterance(self,utterance:str):
        self.action_controller.receive_utterance(utterance)
    # Module for the agent to perceive the environment and get the observation
    async def perceive(self):
        #TODO: Implement the perception module
        pass