from prompt_poet import Prompt
from typing import ClassVar
from llm.openai_client import OpenAIChatCompletions, OpenAIChatCompletionsParams
class Monitoring:
    llm = OpenAIChatCompletions()
    llm.params = OpenAIChatCompletionsParams(
        model="gpt-4o-mini",
        temperature=0.0,
    )
    @classmethod
    async def update_summary(cls,current_goal,recent_events,summary):
        recent_events = [event.description for event in recent_events]
        prompt = Prompt(
            template_path="configs/template/monitoring.yml.j2",
            template_data={
                "current_goal":current_goal,
                "summary": summary,
                "new_events":"\n".join(recent_events)
            }
        )
        response = await cls.llm.generate(prompt)
        return response.choices[0].message.content

