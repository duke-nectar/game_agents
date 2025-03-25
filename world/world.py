import sys
import asyncio
import os 
from agent.base_agent import Agent
from state.agent_state import ObservationEvent, Observation
import json
from state.agent_state import AgentState
from map import Map
from utils import map_dir
import time
import threading
import datetime
class World:
    def __init__(self,load_from_dir:str):
        self.load_from_dir = load_from_dir
        self.map = Map(map_dir=map_dir)
        self.agents = []
        self.current_time = None
        self.agent_states = []
        self.running = True
        self.threads = []
    async def load_world(self):
        all_agents = os.listdir(self.load_from_dir)
        for agent in all_agents:
            with open(os.path.join(self.load_from_dir, agent, "agent.json"), "r") as f:
                data = json.load(f)
                self.agents.append(Agent(**data))
            with open(os.path.join(self.load_from_dir, agent, "state.json"), "r") as f:
                data = json.load(f)
                if self.current_time is None:
                    self.current_time = datetime.datetime.fromtimestamp(data["current_time"])
                agent_state = AgentState(self.agents[-1], location=data["location"], current_time=self.current_time)
                for agent_state in self.agent_states:
                    agent_state.add_relationship(agent_state)
                self.agent_states.append(agent_state)
    def capture_world(self):
        while self.running:
            for agent_state in self.agent_states:
                #agent_state.action_controller.get_action()
                self.map.clear_events()
                self.map.set_event(agent_state.location[0],agent_state.location[1],agent_state.get_action_event)
            time.sleep(0.5)
            self.current_time += datetime.timedelta(seconds=5)
            ## TODO: Get all agent_state data 
    def update_agent(self,agent_state):
        while self.running:
            x,y = agent_state.location
            events = self.map.get_nearby_tiles(x,y)
            observation = Observation(current_time=self.current_time,events=events)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(agent_state.update(observation))
            finally:
                loop.close()
            time.sleep(1)
    async def start_task(self):
        capture_thread = threading.Thread(target=self.capture_world)
        capture_thread.daemon = True
        capture_thread.start()
        self.threads.append(capture_thread)
        for agent_state in self.agent_states:
            update_thread = threading.Thread(target=self.update_agent,args=(agent_state,))
            update_thread.daemon = True
            update_thread.start()
            self.threads.append(update_thread)
async def main():
    world = World("configs/base_world")
    await world.load_world()
    await asyncio.gather(*[agent_state.memory.init_task for agent_state in world.agent_states])
    world.start_task()
if __name__ == "__main__":
    asyncio.run(main())