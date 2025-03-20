
from pydantic import BaseModel
from typing import List, Optional


class Agent(BaseModel):
    name: str
    gender: str
    age: int
    lifestyle: str
    description: str
    goal: str 
    example_utterances: Optional[List[str]] = []
    all_available_actions: Optional[List[str]] = []
    init_memory: List[str] = []
    def get_information(self):
        infor = ""
        infor += f"Description: {self.description}\n"
        infor += f"Gender: {self.gender}\n"
        infor += f"Age: {self.age}\n"
        infor += f"Lifestyle: {self.lifestyle}\n"
        infor += f"Example Utterances: {self.example_utterances}\n"
        return infor
