from abc import ABC, abstractmethod

# After cognitive controller choose the action and update to the agent state (action_name, duration)
# The action executor will execute the action
class BaseActionExecutor:
    @classmethod
    def execute(self, agent_state):
        raise NotImplementedError("Subclasses must implement this method")
    
# Currently will have move, talk, find, maybe intimate. 