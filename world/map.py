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
    def get_arenas_in_sector(self,sector:str):
        all_locations = self.get_tile_by_location(sector,"sector")
        all_arenas = []
        for location in all_locations:
            if self.maze[location[1]][location[0]]["arena"] != "empty" and self.maze[location[1]][location[0]]["arena"] not in all_arenas:
                all_arenas.append(self.maze[location[1]][location[0]]["arena"])
        return all_arenas
    def get_tile_by_location(self,sector,arena):
        all_locations = []
        for i in range(len(self.maze)):
            for j in range(len(self.maze[i])):
                if self.maze[i][j]["sector"] == sector and self.maze[i][j]["arena"] == arena:
                    all_locations.append((i,j))
        return all_locations
    def get_all_locations(self,level:str):
        all_locations = []
        for i in range(len(self.maze)):
            for j in range(len(self.maze[i])):
                if self.maze[i][j][level] != "empty" and self.maze[i][j][level] not in all_locations:
                    all_locations.append(self.maze[i][j][level])
        return all_locations
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
        nearby_tiles_events = []
        for i in range(y-radius, y+radius+1):
            for j in range(x-radius, x+radius+1):
                if 0 <= i < len(self.maze) and 0 <= j < len(self.maze[i]):
                    if 'events' in self.maze[i][j]:
                        nearby_tiles_events.extend(self.maze[i][j]['events'])
        return nearby_tiles_events
    def set_event(self,x:int,y:int,event:ObservationEvent):
        if 'events' not in self.maze[y][x]:
            self.maze[y][x]['events'] = []
        self.maze[y][x]['events'].append(event)
        # TODO: Implement the event setting
    def clear_events(self):
        for i in range(len(self.maze)):
            for j in range(len(self.maze[i])):
                if 'events' in self.maze[i][j]:
                    self.maze[i][j]['events'] = []
if __name__ == "__main__":
    map = Map(map_dir=map_dir)
    print(map.access_tile(x=120,y=52))
    
