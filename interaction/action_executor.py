from abc import ABC, abstractmethod
from llm.openai_client import OpenAIChatCompletions, OpenAIChatCompletionsParams
from llm.openrouter_client import OpenRouterChatCompletions, OpenRouterChatCompletionsParams
from prompt_poet import Prompt
import json
import threading
# After cognitive controller choose the action and update to the agent state (action_name, duration)
# The action executor will execute the action
class BaseActionExecutor:
    @classmethod
    def execute(self, agent_state):
        raise NotImplementedError("Subclasses must implement this method")

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
            context = f"{self.first_talker}'s goal: {self.goal}\n"
            recent_events = "\n".join(agent_state.recent_events) if agent_state.recent_events is not None else ""
            retrieved_memory = agent_state.memory.retrieve([self.goal,self.second_talker])
            retrieved_memory_str = "\n".join(retrieved_memory)
            context += f"Recent events: {recent_events}\n"
            context += f"Memory in {self.first_talker}'s head: {retrieved_memory_str}\n"
            prompt = Prompt(
                template_path=self.template_path,
                params={
                    "target_agent_name": agent_state.agent.name,
                    "description": agent_state.agent.get_information(),
                    "current_conversation": agent_state.current_conversation,
                    "context": self.context
                }
            )
            response = await self.llm.generate(prompt)
            response = json.loads(response)
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
    async def execute(self, agent_state):
        pass


class FindExecutor(BaseActionExecutor):
    async def execute(self, agent_state):
        pass

class ReflectionExecutor(BaseActionExecutor):
    async def execute(self, agent_state):
        pass