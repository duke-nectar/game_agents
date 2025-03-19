from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List, Optional
from memory.base_memory import AgentMemory


class Agent(BaseModel):
    name: str
    gender: str
    age: int
    lifestyle: str
    characteristic: str
    example_dialogue: Optional[List[str]] = []
    all_available_actions: Optional[List[str]] = []

    