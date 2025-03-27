from typing import List
abilities = [
    {
        "name":"talk",
        "description":"Talk to a person",   
        "lifespan": 400  # most 8 utterance for each conversation 
    },
    {
        "name":"move",
        "description":"Move to a location",
        "lifespan": 160 # set higher lifespan, terminated when go to the target location (each utterance stand for 10 steps, so mostly 8 utterance for each of 2)
    },
    {
        "name":"find",
        "description":"Find a person",
        "lifespan": 1000 # set higher lifespan, terminated when find the target person
    },
    {
        "name":"reflection",
        "description":"Reflect on the current situation (mostly for conversation)",
        "lifespan":1 
    }
]
act_to_emoji = {
    "talk":"💬",
    "move":"🚶‍♂️",
    "find":"🔍",
    "reflection":"🤔"
}

# Handle the action config and get the available actions
# Currently all agents have ability to talk and move first, can be expand to more actions and specific for each agent later
class Actions:
    def __init__(self,agent_name:str,
                 action_available:List[str]=None):
        self.action_list = abilities
        self.current_action = {
            "name":"idle",
            "lifespan":0,
            "emoji":None
        }
        self.current_conversation = []
        self.goal = None
        self.talking_with = None
        self.action_history = []
        self.agent_name = agent_name
        self.sector = None
        self.arena = None
        self.planned_path = None
    def get_available_actions(self):
        # If the action is leaf-action, return  None
        available_actions = [x["name"] for x in self.action_list]
        if self.talking_with is not None:
            return []
        if self.current_action['lifespan'] <= 0:
            if self.current_action['name'] == "talk":
                return ["reflection"]
            return available_actions
        return []
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
                        "lifespan":act['lifespan'],
                        "emoji":act_to_emoji[action]
                    }
                    break
            self.goal = goal
            self.action_history.append({"action":action,"goal":goal,"duration":0})
            # Reset the talking with and planned path
            self.talking_with = None
            self.planned_path = None
            if action == "talk":
                self.talking_with = goal.split(":")[0]
        else:
            self.current_action['lifespan'] -= 1
            self.action_history[-1]['duration'] += 1
    def set_lifespan(self,lifespan:int=None):
        if lifespan is not None:
            self.current_action['lifespan'] = lifespan
        else:
            self.current_action['lifespan'] = self.action_list[self.current_action['name']]['lifespan']
    @property
    def action_str(self):
        if self.goal is not None:
            return f"Action from {self.agent_name}: {self.current_action['name']}, Goal: {self.goal}"
        else:
            return f"Action from {self.agent_name}: {self.current_action['name']}"

