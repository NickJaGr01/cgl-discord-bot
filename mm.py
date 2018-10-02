class MMQueue:
    def __init__(self):
        self.queue = {}

    def in_queue(self):
        l = []
        for id in self.queue.keys():
            if self.queue[id]["lobby"] < 0:
                l.append(id)
        return l

    def lobbies(self):
        d = {}
        for id in self.queue.keys():
            if self.queue[id]["lobby"] >= 0:
                if not self.queue[id]["lobby"] in dict:
                    d[self.queue[id]["lobby"]] = {"time": self.queue[id]["time"], "players": {}}
                d[self.queue[id]["lobby"]]["players"][id] = {"team": self.queue[id]["team"], "confirmed": self.queue[id]["confirmed"]}
        return d

    def step_time(self):
        for id in self.queue.keys():
            self.queue[id]["time"] -= 1

    def push(self, discordID):
        self.queue[discordID] = {"lobby": -1, "confirmed": False, "time": 0, "team": 0}

    def pop(self, discordID):
        del self.queue[discordID]

    def move(self, discordID, lobby, team=0):
        self.queue[discordID]["lobby"] = lobby
        self.queue[discordID]["confirmed"] = False
        self.queue[discordID]["time"] = 30
        self.queue[discordID]["team"] = team
