from typing import Dict
from prompt_poet import Prompt
from llm.openai_client import OpenAIChatCompletions, OpenAIChatCompletionsParams
from interaction.action_executor import TalkExecutor, MoveExecutor
import json
# used to choose the high-level action for the agent
action_executor = {
    "talk": TalkExecutor,
    "move": MoveExecutor,
}
class CognitiveController:
    # Prompt templates is the template using for each action
    llm = OpenAIChatCompletions(
        params = OpenAIChatCompletionsParams(
            model="gpt-4o-mini",
                temperature=0.0,
                max_tokens=1000,
                top_p=1.0)
        )
    @classmethod
    async def run_llm(cls, agent_state):
        prompt = Prompt(
            template_path="configs/template/cognitive_controller.yml.j2",
            params=agent_state.data
        )
        response = await cls.llm.generate(prompt)
        try: 
            response = json.loads(response)
            action = response["action"]
            goal = response["goal"]
        except:
            raise ValueError("Invalid response from the cognitive controller")
        return action, goal
    @classmethod
    async def execute(cls, agent_state):
        all_actions = agent_state.action_controller.get_available_actions()
        if len(all_actions) == 0:
            return None
        
        return action, goal