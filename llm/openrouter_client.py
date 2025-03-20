from base_llm import ChatCompletion, LLMClient, LLMParams
import os
import asyncio
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
class OpenRouterChatCompletionsParams(LLMParams):
    model: str = "deepseek/deepseek-chat"
    max_completion_tokens: int = 1000
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    seed: int = 1357

class OpenRouterClient(LLMClient):
    def _get_req_url(self,key):
        url_dict = {
            "chat_completions":"https://openrouter.ai/api/v1/chat/completions",
        }
        return url_dict.get(key)
    def _get_req_headers(self):
        return {
            "Authorization":f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type":"application/json"
        }

class OpenRouterChatCompletions(ChatCompletion, OpenRouterClient):
    params = OpenRouterChatCompletionsParams()

if __name__ == "__main__":
    from prompt_poet import Prompt
    template_data = {
        "character_name": "Character Assistant",
        "username": "Jeff",
        "user_query": "Can you help me with my homework?"
    }
    prompt = Prompt(
        template_path = "configs/template/test.yml.j2",
        template_data = template_data       
    )
    client = OpenRouterChatCompletions()
    res = asyncio.run(client.generate(prompt))
    print(res['usage']['cost'])