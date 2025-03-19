from abc import abstractmethod
from pydantic import BaseModel
from typing import List, Optional
from prompt_poet import Prompt
from llm import *
from memory.utils import cosine_similarity, get_embedding
class Event(BaseModel):
    event_id:str
    description: str
    embedding: Optional[List[float]] = None
class AgentMemory:
    def __init__(self,
                 max_recent_size:int=10,
                 max_long_term_size:int=100):
        self.temp_memory = []
        self.long_term_memory = []
        self.max_recent_size = max_recent_size
        self.max_long_term_size = max_long_term_size
        self.llm =  OpenAIChatCompletions(
            params = OpenAIChatCompletionsParams(
                model="gpt-4o-mini",
                temperature=0.0,
                max_tokens=1000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
        )
    def add_event(self,event:Event):
        self.temp_memory.append(event)
        if len(self.temp_memory) > self.max_recent_size:
            self.summarize_and_forget()
            self.temp_memory = []
    def add_events(self,events:List[Event]):
        self.temp_memory.extend(events)
        if len(self.temp_memory) > self.max_recent_size:
            self.summarize_and_forget()
            self.temp_memory = []
    async def retrieve(self, query,top_k:int=5):
        embedding = await get_embedding(query)
        # Calculate the cosine similarity between the query embedding and all event embeddings
        similarities = [cosine_similarity(embedding, event.embedding) for event in self.temp_memory]
        # Get the top 5 most similar events
        top_events = sorted(zip(similarities, self.temp_memory), key=lambda x: x[0], reverse=True)[:top_k]
        return top_events
    # Need to implement this function
    async def summarize_and_forget(self):
        # First need to cluster all memory in temp_memory into groups based on their embeddings
            

        pass