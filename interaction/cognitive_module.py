from typing import Dict
from prompt_poet import Prompt
from llm.openai_llm import OpenAIChatCompletions, OpenAIChatCompletionsParams
from state.agent_state import AgentState
class CognitiveController:
    # Prompt templates is the template using for each action
    def __init__(self,
                 prompt_template_path:str,
                 ):
        self.prompt_template_path = prompt_template_path
        self.llm = OpenAIChatCompletions(
            params = OpenAIChatCompletionsParams(
                model="gpt-4o-mini",
                temperature=0.0,
                max_tokens=1000,
                top_p=1.0)
        )
    async def run_llm(self, agent_state:AgentState):
        prompt = Prompt(
            template_path=self.prompt_template_path,
            params=agent_state.data
        )
        response = await self.llm.generate(prompt)
        return response
