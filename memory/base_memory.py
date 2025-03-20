from abc import abstractmethod
from pydantic import BaseModel
from typing import List, Optional
from prompt_poet import Prompt
from llm import *
import uuid
from memory.utils import cosine_similarity, get_embedding, dbscan_cluster
from datetime import datetime
from state.agent_state import AgentState
class Event(BaseModel):
    curr_time: datetime
    event_id:str
    description: str
    embedding: Optional[List[float]] = None
class AgentMemory:
    def __init__(self,
                 init_memory:List[str] = [],
                 max_recent_size:int=10,
                 max_long_term_size:int=100):
        self.temp_memory = []
        self.work_memory = []
        self.long_term_memory = init_memory
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
    async def add_event(self,description:str):
        if description not in [event.description for event in self.temp_memory] + [event.description for event in self.long_term_memory]:
            event_id = str(uuid.uuid4())
            embedding = await get_embedding(description)
            event = Event(event_id=event_id,description=description,embedding=embedding)
            self.work_memory.append(event)
    async def add_events(self,descriptions:Optional[List[str]],agent_state:AgentState):
        if descriptions is None:
            return 
        for description in descriptions:
            await self.add_event(description)
        if len(self.work_memory) > self.max_workmem_size:
            await self.monitoring(agent_state.current_goal)
            self.work_memory = []
        if len(self.temp_memory) > self.max_recent_size:
            await self.summarize_and_forget()
            self.temp_memory = []
    async def retrieve(self, query,top_k:int=5):
        embedding = await get_embedding(query)
        # Calculate the cosine similarity between the query embedding and all event embeddings
        similarities = [cosine_similarity(embedding, event.embedding) for event in self.long_term_memory]
        # Get the top 5 most similar events
        top_events = sorted(zip(similarities, self.long_term_memory), key=lambda x: x[0], reverse=True)[:top_k]
        return top_events
    # Need to implement this function
    async def monitoring(self,current_goal:str):
        prompt = Prompt(
            template_path="configs/template/monitoring.yml.j2",
            template_data={
                "current_goal":current_goal,
                "summary":"\n".join([event.description for event in self.work_memory]),
                "new_events":"\n".join([event.description for event in self.temp_memory])
            }
        )
        response = await self.llm(prompt)
        return response.choices[0].message.content
    async def summarize_and_forget(self):
        # First need to cluster all memory in temp_memory into groups based on their embeddings
        embeddings = [event.embedding for event in self.temp_memory]
        labels = dbscan_cluster(embeddings)
        # Then, for each group, summarize the events and keep the most important one
        # Then, forget the rest
        # Then, add the summarized event to the long_term_memory
        # Then, forget the events in the long_term_memory that are no longer relevant
        clusters = {}
        for label, event in zip(labels, self.temp_memory):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(event)
        for label, events in clusters.items():
            group_sumarize = await self.summarize_events(events)

    async def summarize_events(self,events:List[Event]):
        prompt = Prompt(
            template_path="configs/template/summarize_memory.yml.j2",
            template_data={
                "memory_str":"\n".join([event.description for event in events])
            }
        )   
        response = await self.llm(prompt)
        return response.choices[0].message.content
