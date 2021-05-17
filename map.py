import os

map_ascent = []
map_bind = []
map_heaven = []
map_icebox = []
map_split = []

class Map():
    __slots__ = 'agent', 'ability', 'map_name', 'start', 'dest',  'gif'
    def __init__(self, _agent, _ability, _map_name, _start, _dest, _gif):
        self.agent = _agent
        self.ability = _ability
        self.map_name = _map_name
        self.start = _start
        self.dest = _dest
        self.gif = _gif
    
    def get_agent(self):
        return self.agent

    def get_ability(self):
        return self.ability

    def get_map_name(self):
        return self.map_name

    def get_start(self):
        return self.start

    def get_dest(self):
        return self.dest

    def get_gif(self):
        return self.gif


def load_data():
    file_name = os.listdir("data")
    for f in file_name:
        agent = f.split(".")[0]
        lines = open("data/" + f, "r").readlines()
        for line in lines:
            tokens = line.strip().split(",")
            map_name = tokens[0].split("-")[0]
            m = Map(agent, tokens[3], map_name, tokens[1], tokens[2], tokens[4])
            if map_name == "ascent":
                map_ascent.append(m)
            elif map_name == "bind":
                map_bind.append(m)
            elif map_name == "heaven":
                map_heaven.append(m)
            elif map_name == "icebox":
                map_icebox.append(m)
            elif map_name == "split":
                map_split.append(m)
            else:
                continue

def select_map(map_name):
    data = []
    if map_name == "ascent":
        data = map_ascent
    elif map_name == "bind":
        data = map_bind
    elif map_name == "heaven":
        data = map_heaven
    elif map_name == "icebox":
        data = map_icebox
    elif map_name == "split":
        data = map_split
    return data

def search(agent, ability, map_name, start, dest):
    match = []
    data = select_map(map_name)
    for d in data:
        if d.get_agent() != agent or d.get_ability() != ability:
            continue
        if start != None and dest != None:
            if d.get_start() == start and d.get_dest() == dest:
                match.append(d)
        else:
            if start != None:
                if d.get_start() == start:
                    match.append(d)
            elif dest != None:
                if d.get_dest() == dest:
                    match.append(d)
            else:
                match.append(d)
    if len(match) == 0:
        match.append(False)
    return match