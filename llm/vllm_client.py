from llm.base_llm import ChatCompletion,TextCompletion, LLMClient, LLMParams
import os
VLLM_API_KEY = os.getenv("VLLM_API_KEY")
class VLLMChatCompletionsParams(LLMParams):
    model: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    max_completion_tokens: int = 1000
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    seed: int = 1357
    min_p: float = 0.0
    top_k: int = 1000

class VLLMClient(LLMClient):
    def __init__(self,endpoint:str):
        self.endpoint = endpoint
    def _get_req_url(self,key):
        url_dict = {
            "chat_completions":f"{self.endpoint}/chat/completions",
        }
        return url_dict.get(key)
    def _get_req_headers(self):
        return {
            "Authorization":f"Bearer {VLLM_API_KEY}",
            "Content-Type":"application/json"
        }

class VLLMChatCompletions(ChatCompletion, VLLMClient):
    params = VLLMChatCompletionsParams()
