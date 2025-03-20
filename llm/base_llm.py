import sys
sys.path.append(".")
from state.agent_state import AgentState
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from pydantic import BaseModel
import httpx
class LLM(ABC):
    async def run(self, state: AgentState):
        if not self.template:
            return None
        prompt = await self.template.run(state)
        res = await self.generate(
            prompt = prompt
        )
        return res
    @abstractmethod
    async def generate(self, prompt):
        pass

class LLMParams(BaseModel):
    pass

class LLMClient:
    def _get_raw_completions_req(self,prompt:str,params:LLMParams) -> dict:
        req_json = {
            "prompt":prompt,
            **params.model_dump(exclude_none=True)
        }
        return req_json
    def _get_chat_completions_req(self,messages:list[Dict],params:LLMParams) -> dict:
        if sum(m["role"] == "system" for m in messages) > 1:
            system_prompt_message = "\n".join(m["content"] for m in messages if m["role"] == "system")
            messages = [{"role":"system","content":system_prompt_message}] + [m for m in messages if m["role"] != "system"]
        req_json = {"messages":messages,
                    **params.model_dump(exclude_none=True)
                    }
        
        return req_json
    @abstractmethod
    def _get_req_headers(self) -> Dict:
        pass
    @abstractmethod
    def _get_req_url(self,key) -> str:
        pass

class TextCompletion(LLM,LLMClient):
    max_retries = 3
    async def generate(self,prompt:str) -> str:
        prompt.tokenize()
        prompt_str = prompt.string
        async with httpx.AsyncClient() as client:
            req_json = self._get_raw_completions_req(prompt,params=self.params)
            for retry_count in range(self.max_retries):
                try:
                    response =  await client.post(
                        self._get_req_url("completions"),
                        json = req_json,
                        headers = self._get_req_headers()
                    )
                    response.raise_for_status()
                except Exception as e:
                    raise e
                finally:
                    if response and response.is_success:
                        resp_json = response.json()
                break
            return resp_json
class ChatCompletion(LLM,LLMClient):
    max_retries: int = 3
    async def generate(self,prompt):
        prompt.tokenize()
        messages = [{"role":p.role,"content":p.content} for p in prompt.parts]
        async with httpx.AsyncClient() as client:
            req_json = self._get_chat_completions_req(messages,params=self.params)
            for retry_count in range(self.max_retries):
                req_json = self._get_chat_completions_req(messages = messages,params = self.params)
                try:
                    
                    response = await client.post(
                        self._get_req_url("chat_completions"),
                        json = req_json,
                        headers = self._get_req_headers()
                    )
                    response.raise_for_status()
                except Exception as e:
                    raise e
                finally:
                    if response and response.is_success:
                        resp_json = response.json()
                        break
            return resp_json
    

        