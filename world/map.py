import json
class Map:
    def __init__(self,map_dir:str):
        self.map_dir = map_dir
        self.load_map()
        self.map = []
    def access_tile(self,x:int,y:int):
        return self.map[y][x]
    def load_map(self):
        with open(self.map_dir, "r") as f:
            self.map = json.load(f)
