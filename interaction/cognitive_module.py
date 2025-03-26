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
    llm = OpenAIChatCompletions()
    llm.params = OpenAIChatCompletionsParams(
        model="gpt-4o-mini",
        temperature=0.0,
        max_tokens=1000,
        top_p=1.0)
    @classmethod
    async def run_llm(cls, agent_state):
        cognitive_data = agent_state.cognitive_data
        for key, value in cognitive_data.items():
            cognitive_data[key] = value.replace("-", " ").replace("\n",";")
        print(cognitive_data)
        prompt = Prompt(
            template_path="configs/template/cognitive_controller.yml.j2",
            template_data=cognitive_data
        )
        response = await cls.llm.generate(prompt)
        #print(response)
        try: 
            response = json.loads(response["choices"][0]["message"]["content"])
            action = response["action"]
            goal = response["goal"]
        except:
            raise ValueError("Invalid response from the cognitive controller")
        return action, goal
    @classmethod
    async def execute(cls, agent_state):
        all_actions = agent_state.action_controller.get_available_actions()
        if len(all_actions) == 1:
            return all_actions[0], ""
        action, goal = await cls.run_llm(agent_state)
        return action, goal

if __name__ == "__main__":
    prompt = Prompt(
        template_path="configs/template/cognitive_controller.yml.j2",
        template_data={
            'persona_info': 'Summary of Aika Shirosaki (from first person perspective): Aika Shirosaki is soft spoken and reserved, often preferring to blend into the background rather than draw attention to herself. While she struggles with confidence, she admires those who can effortlessly express themselves, Gender: female, Age: 20, Lifestyle: student. Spend her day studying and often goes to the coffee shop to study in the afternoon. Example Utterances: []', 
            'current_goal': 'Aika just want to be a normal student and keep good grades. She is curious and want to intimate with Noah Walker, but she is too shy.', 
            'available_actions': 'talk,move,find,reflection', 
            'recent_events': 'From: Aika Shirosaki To:  Type: idle Description: idle to None', 
            'retrieved_events': "I am 20 year old student living in San Francisco. I am a student and loves to study.; I love watching anime and playing video games; I am curious about the new cute guy who's on campus, Noah Walker", 
            'current_time': '2025/03/20 07:50:00', 
            'persona_name': 'Aika Shirosaki', 
            'current_location': ' Dorm for Oak Hill College:common room'}
    )
    print(prompt)