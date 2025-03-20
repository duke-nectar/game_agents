from typing import List
abilities = {
    'talk':{
        'description':'Talk to a person',
        'sub_action':['move']
    },
    'move':{
        'description':'Move to a location or a person'
    },
    'chosse_destination':{
        'description':'Chosse a destination',
        'sub_action':['move']
    }
}


# Handle the action config and get the available actions
# Each action will have a description and following sub-actions
class Actions:
    def __init__(self,
                 action_available:List[str]):
        self.action_list = list(abilities.keys())
        self.current_action = {
            "previous_action":None,
            "name":"idle",
            "lifespan":0
        }
        self.sub_action = {k:v['sub_action'] for k,v in abilities.items()}
    def get_available_actions(self,agent_state):
        # If the action is leaf-action, return  None
        if agent_state.action['action'] not in self.sub_action.keys():
            return None
        # If the action is not expired, return the sub-actions of the current action
        # Else return all available actions
        if agent_state.action['expired']:
            return self.action_list
        else:
            return self.sub_action[agent_state.action['action']]
    # if new action is added, update the current action
    # else, decrease the lifespan of the current action
    def update(self,action):
        if action != None:
            self.current_action = action

        else:
            self.current_action['lifespan'] -= 1



