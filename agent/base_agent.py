
from pydantic import BaseModel
from typing import List, Optional


class Agent(BaseModel):
    name: str
    gender: str
    age: int
    lifestyle: str
    summary: str
    goal: str 
    example_utterances: Optional[List[str]] = []
    all_available_actions: Optional[List[str]] = []
    init_memory: List[str] = []
    def get_information(self):
        infor = ""
        infor += f"Summary of {self.name} (from first person perspective): {self.summary}\n"
        infor += f"Gender: {self.gender}\n"
        infor += f"Age: {self.age}\n"
        infor += f"Lifestyle: {self.lifestyle}\n"
        infor += f"Example Utterances: {self.example_utterances}\n"
        return infor
