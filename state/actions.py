from typing import List
abilities = [
    {
        "name":"talk",
        "description":"Talk to a person",   
        "lifespan": 8  # most 8 utterance for each conversation 
    },
    {
        "name":"move",
        "description":"Move to a location",
        "lifespan":1000 # set higher lifespan, terminated when go to the target location
    },
    {
        "name":"find",
        "description":"Find a person",
        "lifespan":1000 # set higher lifespan, terminated when find the target person
    },
    {
        "name":"reflection",
        "description":"Reflect on the current situation (mostly for conversation)",
        "lifespan":1 
    }
]


# Handle the action config and get the available actions
# Currently all agents have ability to talk and move first, can be expand to more actions and specific for each agent later
class Actions:
    def __init__(self,
                 action_available:List[str]=None):
        self.action_list = abilities
        self.current_action = {
            "name":"idle",
            "lifespan":0
        }
        self.goal = None
        self.talking_with = None
        self.planned_path = None
    def get_available_actions(self):
        # If the action is leaf-action, return  None
        available_actions = self.action_list
        if self.talking_with is not None:
            return []
        if self.planned_path is not None:
            return []
        if self.current_action['lifespan'] <= 0:
            if self.current_action['name'] == "talk":
                return ["reflection"]
            return available_actions
        # If the action is not expired, return the sub-actions of the current action
        # Else return all available actions
    # if new action is added, update the current action
    # else, decrease the lifespan of the current action
    def update(self,action,goal= None):
        if action != None:
            for act in self.action_list:
                if act['name'] == action:
                    self.current_action = {
                        "name":action,
                        "lifespan":act['lifespan']
                    }
                    break
            self.goal = goal
        else:
            self.current_action['lifespan'] -= 1
    def receive_utterance(self,utterance:str):
        if self.current_action['name'] != "talk":
            self.current_action = {
                "name":"talk",
                "lifespan":8
            }
        self.current_conversation.append(utterance)



