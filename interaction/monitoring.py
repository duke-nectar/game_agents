from prompt_poet import Prompt
from typing import ClassVar
from llm.openai_client import OpenAIChatCompletions, OpenAIChatCompletionsParams
from llm.openrouter_client import OpenRouterChatCompletions, OpenRouterChatCompletionsParams
class Monitoring:
    llm = OpenRouterChatCompletions()
    llm.params = OpenRouterChatCompletionsParams(
        model="openai/gpt-4o-mini",
        temperature=0.0,
    )
    @classmethod
    async def update_summary(cls,current_goal,recent_events,summary):
        recent_events = [event.description for event in recent_events]
        print("Monitoring trigger: ")
        print(f"Current goal: {current_goal}")
        print(f"Summary: {summary}")
        print('\n\t'.join(recent_events).strip())
        prompt = Prompt(
            template_path="configs/template/monitoring.yml.j2",
            template_data={
                "current_goal":current_goal,
                "summary": summary,
                "new_events":";\t".join(recent_events).strip()
            }
        )
        response = await cls.llm.generate(prompt)
        return response["choices"][0]["message"]["content"]

