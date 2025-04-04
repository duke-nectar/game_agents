from abc import ABC, abstractmethod
from llm.openai_client import OpenAIChatCompletions, OpenAIChatCompletionsParams
from llm.openrouter_client import OpenRouterChatCompletions, OpenRouterChatCompletionsParams
from prompt_poet import Prompt
import json
import threading
import random
from interaction.utils import path_finder
# After cognitive controller choose the action and update to the agent state (action_name, duration)
# The action executor will execute the action
class BaseActionExecutor:
    @classmethod
    def execute(self, agent_state):
        raise NotImplementedError("Subclasses must implement this method")
    def shut_down(self,agent_state):
        agent_state.action_controller.set_lifespan(0)
# Currently will have move, talk, find, maybe intimate. 
class TalkExecutor(BaseActionExecutor):
    llm = OpenRouterChatCompletions()
    llm.params = OpenRouterChatCompletionsParams(
        model="deepseek/deepseek-chat",
        temperature=0.0,
        min_p=0.1,
        top_k = 250,
        repetition_penalty = 1.1)
    template_path = "configs/template/iterative_convo.yml.j2"
    def __init__(self, first_talker, second_talker, goal):
        self.first_talker = first_talker
        self.second_talker = second_talker
        self.goal = goal
        self.is_conversation_end = False
        self.line_duration = 0
        self.current_conversation = []
        self.lock = threading.Lock()
    async def execute(self,agent_state):
        if agent_state.agent.name == self.first_talker and len(self.current_conversation) % 2 == 1:
            return
        elif agent_state.agent.name == self.second_talker and len(self.current_conversation) % 2 == 0:
            return
        elif (self.line_duration <= 0) and (not self.is_conversation_end):
            ## TODO: Get new utterance and decide to end the conversation or not
            ## Also create a function to generate the duration of the utterance, add to self.line_duration, each step will decrease the duration by 1 
            context = {}
            context["goal"] =  f"{self.first_talker}'s goal: {self.goal}"
            recent_events = ";".join([x.description for x in agent_state.recent_events]) if agent_state.recent_events is not None else ""
            retrieved_memory = await agent_state.memory.retrieve([self.goal,self.second_talker])
            retrieved_memory_str = ";".join(retrieved_memory)
            context["recent_events"] = recent_events
            context["memory"] = retrieved_memory_str
            print(context)
            prompt = Prompt(
                template_path="configs/template/iterative_convo.yml.j2",
                template_data={
                    "target_agent_name": agent_state.agent.name,
                    "description": agent_state.agent.get_information().replace("\n",";\t"),
                    "current_conversation": self.current_conversation if len(self.current_conversation) > 0 else "[The conversation haven't started yet]",
                    "context": context
                }
            )
            response = await self.llm.generate(prompt)
            print(response["choices"][0]["message"]["content"].replace("```json","").strip())
            response = json.loads(response["choices"][0]["message"]["content"].replace("```json","").strip())
            utterance = response["utterance"]
            end_conversation = response["end_conversation"]
            self.current_conversation.append({"name":agent_state.agent.name, "utterance":utterance})
            agent_state.current_conversation = self.current_conversation
            # Sync 
            self.line_duration = self.get_line_duration(utterance)
            if end_conversation:
                agent_state.action_controller.set_lifespan(self.line_duration+1)
        else:
            self.line_duration -= 1
    def get_line_duration(self,utterance:str):
        return 10 
    


class MoveExecutor(BaseActionExecutor):
    llm = OpenRouterChatCompletions()
    llm.params = OpenRouterChatCompletionsParams(
        model="deepseek/deepseek-chat",
        temperature=0.0,
        min_p=0.1,
        top_k = 250,
        repetition_penalty = 1.1)
    def __init__(self,goal):
        self.goal = goal
        self.sector = None
        self.arena = None
    async def execute(self, agent_state):
        agent_current_location = agent_state.map.access_tile(agent_state.location[0],agent_state.location[1])
        sector = agent_current_location["sector"] if agent_current_location["sector"] != "empty" else ""
        arena = agent_current_location["arena"] if agent_current_location["arena"] != "empty" else ""
        agent_current_location_str = f"{sector} {arena}"
        if self.sector is None:
            all_sectors = agent_state.map.get_all_locations("sector")
            prompt = Prompt(
                template_path="configs/template/move_sector.yml.j2",
                template_data={
                    "name": agent_state.agent.name,
                    "current_goal": self.goal,
                    "current_location": agent_current_location_str,
                    "all_sectors": all_sectors
                }
            )
            response = await self.llm.generate(prompt)
            response = response["choices"][0]["message"]["content"].strip()
            self.sector = response.strip("'").strip('"')
            #response = json.loads(response["choices"][0]["message"]["content"])
            #self.sector = response["sector"]
        elif self.arena is None:
            print(f"Agent {agent_state.agent.name} is moving to {self.sector}")
            prompt = Prompt(
                template_path="configs/template/move_arena.yml.j2",
                template_data={
                    "name": agent_state.agent.name,
                    "sector": self.sector,
                    "current_goal": self.goal,
                    "arenas": agent_state.map.get_arenas_in_sector(self.sector)
                }
            )
            response = await self.llm.generate(prompt)
            response = response["choices"][0]["message"]["content"].strip()
            self.arena = response.strip("'").strip('"')
            #response = json.loads(response["choices"][0]["message"]["content"])
            #self.arena = response["arena"]
        elif agent_state.planned_path is None:
            all_tiles = agent_state.map.get_tile_by_location(self.sector,self.arena)
            tile = random.choice(all_tiles)
            print(f"Agent {agent_state.agent.name} is moving to {tile}")
            agent_state.planned_path = path_finder(agent_state.location,tile)[1:]
        else:
            print(f"Agent {agent_state.agent.name} is moving to {self.sector}:{self.arena} according to the planned path: {agent_state.planned_path[0]}")
            next_step = agent_state.planned_path[0]
            agent_state.planned_path = agent_state.planned_path[1:]
            agent_state.location = next_step
            if len(agent_state.planned_path) <= 1:
                self.shut_down(agent_state)
class FindExecutor(BaseActionExecutor):
    async def execute(self, agent_state):
        pass

class ReflectionExecutor(BaseActionExecutor):
    async def execute(self, agent_state):
        pass