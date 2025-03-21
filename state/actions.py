from typing import List
abilities = {
    'talk':{
        'description':'Talk to a person',
    },
    'move':{
        'description':'Move to a location or a person'
    },
}


# Handle the action config and get the available actions
# Each action will have a description and following sub-actions
# Currently all agents have ability to talk and move first, can be expand to more actions and specific for each agent later
class Actions:
    def __init__(self,
                 action_available:List[str]):
        self.action_list = list(abilities.keys())
        self.current_action = {
            "root_action":None,
            "name":"idle",
            "lifespan":0
        }
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
            return available_actions
        # If the action is not expired, return the sub-actions of the current action
        # Else return all available actions
    # if new action is added, update the current action
    # else, decrease the lifespan of the current action
    def update(self,action):
        if action != None:
            self.current_action = action
        else:
            self.current_action['lifespan'] -= 1



