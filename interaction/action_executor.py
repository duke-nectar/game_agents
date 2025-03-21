from abc import ABC, abstractmethod
from llm.openai_client import OpenAIChatCompletions, OpenAIChatCompletionsParams
from llm.openrouter_client import OpenRouterChatCompletions, OpenRouterChatCompletionsParams
# After cognitive controller choose the action and update to the agent state (action_name, duration)
# The action executor will execute the action
class BaseActionExecutor:
    @classmethod
    def execute(self, agent_state):
        raise NotImplementedError("Subclasses must implement this method")

# Currently will have move, talk, find, maybe intimate. 
class TalkExecutor(BaseActionExecutor):
    llm = OpenRouterChatCompletions(
        params = OpenRouterChatCompletionsParams(
            model="deepseek/deepseek-chat",
            temperature=0.0,
            min_p=0.1,
            top_k = 250,
            repetition_penalty = 1.1)
    )
    template_path = "configs/template/iterative_convo.yml.j2"
    def __init__(self, first_talker, second_talker, goal):
        self.first_talker = first_talker
        self.second_talker = second_talker
        self.goal = goal
    async def execute(self, agent_state):
        pass
class MoveExecutor(BaseActionExecutor):
    async def execute(self, agent_state):
        pass
class FindExecutor(BaseActionExecutor):
    async def execute(self, agent_state):
        pass
