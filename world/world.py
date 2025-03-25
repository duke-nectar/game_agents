import sys
import asyncio
sys.path.append(".")
import os 
from agent.base_agent import Agent
from state.agent_state import ObservationEvent
import json
from state.agent_state import AgentState
from world.map import Map
from utils import map_dir
class World:
    def __init__(self,load_from_dir:str):
        self.load_from_dir = load_from_dir
        self.map = Map(map_dir=map_dir)
        self.agents = []
        self.agent_states = []
    async def load_world(self):
        all_agents = os.listdir(self.load_from_dir)
        for agent in all_agents:
            with open(os.path.join(self.load_from_dir, agent, "agent.json"), "r") as f:
                data = json.load(f)
                self.agents.append(Agent(**data))
            with open(os.path.join(self.load_from_dir, agent, "state.json"), "r") as f:
                data = json.load(f)
                agent_state = AgentState(self.agents[-1], location=data["location"], current_time=data["current_time"])
                for agent_state in self.agent_states:
                    agent_state.add_relationship(agent_state)
                self.agent_states.append(agent_state)
    async def capture_world(self):
        # TODO: Implement the world capture
        for agent_state in self.agent_states:
            #agent_state.action_controller.get_action()
            self.map.set_event(agent_state.location[0],agent_state.location[1],agent_state.get_action_event)
        
            ## TODO: Get all agent_state data 
    async def update_all_agents(self):
        for agent_state in self.agent_states:
            agent_state.update()
async def main():
    world = World("configs/base_world")
    await world.load_world()
    await asyncio.gather(*[agent_state.memory.init_task for agent_state in world.agent_states])
    print(world.agent_states[0].memory.long_term_memory)
if __name__ == "__main__":
    asyncio.run(main())