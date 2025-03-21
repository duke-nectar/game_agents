from prompt_poet import Prompt
from typing import ClassVar
from llm.openai_llm import OpenAIChatCompletions, OpenAIChatCompletionsParams
class Monitoring:
    llm: ClassVar[OpenAIChatCompletions] = OpenAIChatCompletions(
        params = OpenAIChatCompletionsParams(
            model="gpt-4o-mini",
            temperature=0.0,
        )
    )
    @classmethod
    async def update_summary(cls,agent_state):
        current_goal = agent_state.current_goal
        recent_events = [event.description for event in agent_state.recent_events]
        prompt = Prompt(
            template_path="configs/template/monitoring.yml.j2",
            template_data={
                "current_goal":current_goal,
                "summary": agent_state.summary,
                "new_events":"\n".join(recent_events)
            }
        )
        response = await cls.llm.generate(prompt)
        return response.choices[0].message.content

