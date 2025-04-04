import asyncio
from pydantic import BaseModel
from typing import List, Optional
from prompt_poet import Prompt
from llm.openai_client import OpenAIChatCompletions, OpenAIChatCompletionsParams
import uuid
from memory.utils import cosine_similarity, get_embedding, dbscan_cluster
from datetime import datetime
class Event(BaseModel):
    #curr_time: str
    event_id:str
    description: str
    embedding: Optional[List[float]] = None

# memory structure for the agent, including temp memory and long term memory
# temp memory is used for store the self-monitoring summaries (the summary in first person perspective of the what the agent has seen and done)
class AgentMemory:
    def __init__(self, name, max_recent_size=20, init_memory=None):
        self.name = name
        self.max_recent_size = max_recent_size
        self.temp_memory = []
        self.long_term_memory = []
        self.work_memory = []
        self.init_memory = init_memory or []
        # Store init_memory for later async initialization
        self.threshold = 0.8 # First initial value, can be changed later
        self.llm =  OpenAIChatCompletions()
        self.llm.params = OpenAIChatCompletionsParams(
            model="gpt-4o-mini",
            temperature=0.0,
            max_tokens=1000,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        if init_memory is not None:
            loop = asyncio.get_running_loop()
            self.init_task = loop.create_task(self.add_events(init_memory,long_term=True))
        else:
            self.init_task = asyncio.create_task(asyncio.sleep(0))
    async def add_event(self,description:str,long_term = False):
        if description not in [event.description for event in self.temp_memory] + [event.description for event in self.long_term_memory]:
            print(f"Adding event: {description} to {self.name}'s memory")
            event_id = str(uuid.uuid4())
            embedding = await get_embedding(description)
            similarities = [cosine_similarity(embedding, event.embedding) for event in self.temp_memory]
            if len(similarities) > 0:
                max_similarity = max(similarities)
                max_similarity_index = similarities.index(max_similarity)
                if max_similarity > self.threshold:
                    del self.temp_memory[max_similarity_index]
            event = Event(event_id=event_id,description=description,embedding=embedding)
            if long_term:
                self.long_term_memory.append(event)
            else:
                self.temp_memory.append(event)
    async def add_events(self,descriptions:Optional[List[str]],long_term:bool=False):
        if descriptions is None:
            return 
        for description in descriptions:
            await self.add_event(description,long_term=long_term)
        if len(self.temp_memory) > self.max_recent_size:
            await self.summarize_and_forget()
            self.temp_memory = []
    async def retrieve(self, queries:List[str],top_k:int=5):
        all_related_events = []
        for query in queries:
            embedding = await get_embedding(query)

            # Calculate the cosine similarity between the query embedding and all event embeddings
            similarities = [cosine_similarity(embedding, event.embedding) for event in (self.long_term_memory + self.temp_memory)]
            # Get the top 5 most similar events
            top_events = sorted(zip(similarities, self.long_term_memory), key=lambda x: x[0], reverse=True)[:top_k]
            all_related_events.extend([event[1] for event in top_events])
            #print(all_related_events)
        return list(set([event.description for event in all_related_events]))
    # Need to implement this function
    # TODO: Change it to the interaction/monitoring.py
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
            await self.add_event(group_sumarize,long_term=True)
            #TODO: Complete it
    async def summarize_events(self,events:List[Event]):
        prompt = Prompt(
            template_path="configs/template/summarize_memory.yml.j2",
            template_data={
                "memory_str":"\n".join([event.description for event in events])
            }
        )   
        response = await self.llm(prompt)
        return response.choices[0].message.content
    def get_all_events_description(self):
        return [event.description for event in self.temp_memory] + [event.description for event in self.long_term_memory]

