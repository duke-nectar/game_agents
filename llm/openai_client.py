from llm.base_llm import ChatCompletion,TextCompletion, LLMClient, LLMParams
import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
class OpenAIChatCompletionsParams(LLMParams):
    model: str = "gpt-4o-mini"
    max_completion_tokens: int = 1000
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    seed: int = 1357

class OpenAIClient(LLMClient):
    def _get_req_url(self,key):
        url_dict = {
            "chat_completions":"https://api.openai.com/v1/chat/completions",
        }
        return url_dict.get(key)
    def _get_req_headers(self):
        return {
            "Authorization":f"Bearer {OPENAI_API_KEY}",
            "Content-Type":"application/json"
        }

class OpenAIChatCompletions(ChatCompletion, OpenAIClient):
    params = OpenAIChatCompletionsParams()
