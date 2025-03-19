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
                 abilities:dict):
        self.action_list = list(abilities.keys())
        self.sub_action = {k:v['sub_action'] for k,v in abilities.items()}
    def get_available_actions(self,agent_state:AgentState):
        # If the action is leaf-action, retunr None
        if agent_state.action['action'] not in self.sub_action.keys():
            return None
        # If the action is not expired, return the sub-actions of the current action
        # Else return all available actions
        if agent_state.action['expired']:
            return self.action_list
        else:
            return self.sub_action[agent_state.action['action']]

