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
        self.log_dir = os.path.join("log",datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        os.makedirs(self.log_dir,exist_ok=True)
    async def load_world(self):
        all_agents = os.listdir(self.load_from_dir)
        for agent in all_agents:
            with open(os.path.join(self.load_from_dir, agent, "agent.json"), "r") as f:
                data = json.load(f)
                new_agent = Agent(**data)
                self.agents.append(new_agent)
            with open(os.path.join(self.load_from_dir, agent, "state.json"), "r") as f:
                data = json.load(f)
                if self.current_time is None:
                    self.current_time = datetime.datetime.strptime(data["current_time"],
                                                                   "%Y-%m-%d %I:%M:%S %p")
            new_agent_state = AgentState(new_agent, location=data["location"], current_time=self.current_time, map = self.map)
            for agent_state in self.agent_states:
                agent_state.add_relationship(new_agent_state)
                new_agent_state.add_relationship(agent_state)
            self.agent_states.append(new_agent_state)
            
    def capture_world(self):
        while self.running:
            #print("--------------------------------")
            #print(f"Current time: {self.current_time}")
            self.map.clear_events()
            agent = {}
            for agent_state in self.agent_states:
                self.map.set_event(agent_state.location[0], agent_state.location[1], agent_state.get_action_event)
                #print(f"Agent: {agent_state.agent.name} in {agent_state.location}")
                #print(f"Action: {agent_state.get_action_event}")
                agent[agent_state.agent.name] = {
                    "location":agent_state.location,
                    "goal":agent_state.current_goal,
                    "summary":agent_state.summary,
                    "action_description": agent_state.get_action_event.description,
                    "action_lifespan": agent_state.action_controller.current_action['lifespan']
                }
            time.sleep(0.5)
            with open(os.path.join(self.log_dir,f"world_{self.current_time}.json"),"w") as f:
                json.dump(agent,f,ensure_ascii=False,indent=2)
            self.current_time += datetime.timedelta(seconds=5)
            ## TODO: Get all agent_state data 
    def update_agent(self,agent_state):
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        async def agent_task():
            while self.running:
                try:
                    print(f"Agent state: {agent_state.agent.name} started update at {self.current_time}")
                    x,y = agent_state.location
                    current_time = str(self.current_time)
                    events = self.map.get_nearby_tiles(x,y)
                    observation = Observation(current_time=current_time,events=events)
                    await agent_state.get_observation(observation)
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"Error updating agent {agent_state.agent.name}: {str(e)}")
                    # Add a small delay before retrying after an error
                    await asyncio.sleep(1)
        try:
            loop.run_until_complete(agent_task())
        except Exception as e:
            print(f"Fatal error in agent {agent_state.agent.name} thread: {str(e)}")
        finally:
            loop.close()
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
        try:
            while self.running:
                await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            self.running = False
            for thread in self.threads:
                thread.join()
            print("World stopped")
async def main():
    world = World("configs/base_world")
    await world.load_world()
    await asyncio.gather(*[agent_state.memory.init_task for agent_state in world.agent_states])
    #print(world.agent_states[-1].relationships)
    #for agent in world.agent_states:
    #    print(agent.relationships)
    await world.start_task()   
if __name__ == "__main__":
    asyncio.run(main())