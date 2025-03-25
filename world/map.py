from utils import map_dir
from state.agent_state import ObservationEvent
from typing import List
from collections import defaultdict
import json
import os
class Map:
    def __init__(self,map_dir:str):
        self.map_dir = map_dir
        maze_meta_info = json.load(open(os.path.join(self.map_dir,"maze_meta_info.json"),"r"))
        self.maze = [[{} for _ in range(maze_meta_info["maze_width"])] for _ in range(maze_meta_info["maze_height"])]
        self.maze_width = maze_meta_info["maze_width"]
        self.maze_height = maze_meta_info["maze_height"]
        print(f"Maze length: {len(self.maze)}, {len(self.maze[0])}")
        self.load_map()
        # load the map matrix from the map_dir
        # self.map[y][x] = {"sector":self.sector_to_str[self.sector_map[y][x]],"arena":self.arena_to_str[self.arena_map[y][x]],"game_object":self.game_object_to_str[self.game_object_map[y][x]],"events":[]}
    # Each tile will have list of events happen on it
    # self.map[y][x] = [Event(description,from_agent,to,type)]
    def access_tile(self,x:int,y:int):
        return self.maze[y][x]
    def set_tile_init(self, level:str):
        level_map = []
        annotation = {}
        with open(os.path.join(self.map_dir,"maze",f"{level}_maze.csv"),"r") as f:
            rows = f.readlines()
            for row in rows:
                row = row.strip().split(',')
                level_map.extend([row[i:i+self.maze_width] for i in range(0,len(row),self.maze_width)])
            
        with open(os.path.join(self.map_dir,"special_blocks",f"{level}_blocks.csv"),"r") as f:
            rows = f.readlines()
            annotation = {}
            for row in rows:
                id, *_, description = row.strip().split(',')
                annotation[str(id)] = description
        for i in range(len(level_map)):
            for j in range(len(level_map[i])):
                block_type = level_map[i][j].strip()
                if str(block_type) == "0":
                    self.maze[i][j][level] = "empty"
                else:
                    block_annotation = annotation[str(block_type)]
                    #print(block_annotation)
                    self.maze[i][j][level] = block_annotation
    def load_map(self):
        self.set_tile_init("sector")
        self.set_tile_init("arena")
        self.set_tile_init("game_object")
        #TODO: Get the collison later, just test with this first
    def get_nearby_tiles(self,x:int,y:int,radius:int=1) -> List[ObservationEvent]:
        # TODO: Implement the nearby tiles
        pass
    def set_event(self,x:int,y:int,event:ObservationEvent):
        if 'events' not in self.maze[y][x]:
            self.maze[y][x]['events'] = []
        self.maze[y][x]['events'].append(event)
        # TODO: Implement the event setting
        pass
if __name__ == "__main__":
    map = Map(map_dir=map_dir)
    print(map.access_tile(x=120,y=52))
    
