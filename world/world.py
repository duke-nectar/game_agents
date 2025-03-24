import sys
sys.path.append(".")
import os 
from agent.base_agent import Agent
import json
from state.agent_state import AgentState
class World:
    def __init__(self,load_from_dir:str):
        self.load_from_dir = load_from_dir
        self.agents = []
        self.agent_states = []
        self.load_world()
    def load_world(self):
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

if __name__ == "__main__":
    world = World("configs/base_world")
    print(world.agents)
    print(world.agent_states)