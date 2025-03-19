from abc import ABC, abstractmethod
from typing import Dict
class BaseState(ABC):
    def __init__(self,
                 ):
        pass
    @abstractmethod
    def update(self, observation:Dict):
        pass