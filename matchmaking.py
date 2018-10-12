import math
import asyncio
import random

from bot import bot
from bot import CGL_server
from bot import lobby_category
import database

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
                if self.queue[id]["lobby"] not in d:
                    d[self.queue[id]["lobby"]] = {"time": self.queue[id]["time"], "last message time": self.queue[id]["last message time"], "players": {}}
                d[self.queue[id]["lobby"]]["players"][id] = {"team": self.queue[id]["team"], "confirmed": self.queue[id]["confirmed"]}
        return d

    def step_time(self):
        for id in self.queue:
            self.queue[id]["time"] -= delta_time

    def push(self, discordID):
        self.queue[discordID] = {"lobby": -1, "confirmed": False, "time": 0, "team": 0}

    def pop(self, discordID):
        del self.queue[discordID]

    def move(self, discordID, lobby, team=0):
        self.queue[discordID]["lobby"] = lobby
        self.queue[discordID]["confirmed"] = False
        self.queue[discordID]["time"] = 30
        self.queue[discordID]["last message time"] = 30
        self.queue[discordID]["team"] = team

available_lobbies = [i for i in range(20)]

mmqueue = MMQueue()
matches = {}

MAP_LIST = ["dust2", "mirage", "cache", "inferno", "nuke", "overpass", "cobblestone"]

MESSAGE_TIME_DIFFERENCE = 5

delta_time = 0

async def mm_thread():
    global delta_time
    loop = asyncio.get_event_loop()
    last_time = loop.time()
    while True:
        now = loop.time()
        delta_time = now - last_time
        last_time = now
        await cycle_queue()
        await cycle_matches()
        await asyncio.sleep(.1)

async def cycle_queue():
    inq = mmqueue.in_queue()
    lobby = 0
    #for i in range(math.floor(len(inq)/10)*10):
    for i in range(len(inq)):
        #if i%10 == 0:
        if i%1 == 0:
            if len(available_lobbies) == 0:
                break
            lobby = available_lobbies[0]
            available_lobbies.pop(0)
        id = inq[i]
        team = 1
        if i%10/5 >= 1:
            team = 2
        mmqueue.move(id, lobby, team)
        user = bot.get_user(id)
        await user.send("A game has been found! Type \"!accept\" to confirm.")
        await user.send("30 seconds remaining")
    mmqueue.step_time()
    lobbies = mmqueue.lobbies()
    for l in lobbies.keys():
        ready = True
        for id in lobbies[l]["players"]:
            if lobbies[l]["last message time"] - lobbies[l]["time"] >= MESSAGE_TIME_DIFFERENCE:
                user = bot.get_user(id)
                mmqueue.queue[id]["last message time"] = lobbies[l]["last message time"] - MESSAGE_TIME_DIFFERENCE
                await user.send("%s seconds remaining" % mmqueue.queue[id]["last message time"])
            if not lobbies[l]["players"][id]["confirmed"]:
                ready = False
        #begin the game if all players have confirmed the match
        if ready:
            #create the lobbies for the teams
            guild = bot.get_guild(CGL_server)
            cat = guild.get_channel(lobby_category)
            textchat = await guild.create_text_channel("Game Chat", category=cat)
            teamchat = [None, None]
            teamchat[0] = await guild.create_voice_channel("Your Team", category=cat)
            teamchat[1] = await guild.create_voice_channel("Your Team", category=cat)
            matches[l] = {"map": MAP_LIST.copy(), "votes": {}, "time": 30, "last message time": 30+MESSAGE_TIME_DIFFERENCE, "channels": {0: textchat, 1: teamchat[0], 2: teamchat[1]}, "players": {}}
            host = list(lobbies[l]["players"].keys())[0]
            host_rep = database.player_rep(host)
            for id in lobbies[l]["players"]:
                this_rep = database.player_rep(id)
                if this_rep > host_rep:
                    host = id
                    host_rep = this_rep
                team = mmqueue.queue[id]["team"]
                matches[l]["players"][id] = {"team": team}
                user = guild.get_member(id)
                await textchat.set_permissions(user, read_messages=True)
                await teamchat[team-1].set_permissions(user, connect=True)
                await user.edit(voice_channel=teamchat[team-1])
                await user.send("Your match is ready. Please return to the CGL Dicord server to vote for the map.")
            matches[l]["host"] = host
            mapliststring = "maps remaining:"
            for mv in matches[l]["map"]:
                mapliststring += "\n    %s" % mv
            await matches[l]["channels"][0].send("%s\nType \"vote map_name\" to vote to eliminate a map." % mapliststring)
            continue
        if lobbies[l]["time"] <= 0:
            for id in lobbies[l]["players"]:
                if lobbies[l]["players"][id]["confirmed"]:
                    mmqueue.move(id, -1)
                    user = bot.get_user(id)
                    user.send("One or more players in your lobby failed to confirm the match. You have been added back to the queue.")
                else:
                    mmqueue.pop(id)
                    user = bot.get_user(id)
                    await user.send("You failed to confirm your match. You have been removed from the queue.")
            available_lobbies.append(l)

ELO_K_FACTOR = 16

async def cycle_matches():
    for m in matches:
        if type(matches[m]["map"]) is list:
            if matches[m]["last message time"] - matches[m]["time"] >= MESSAGE_TIME_DIFFERENCE:
                matches[m]["last message time"] = matches[m]["last message time"] - MESSAGE_TIME_DIFFERENCE
                await matches[m]["channels"][0].send("%s seconds remaining" % matches[m]["last message time"])
            matches[m]["time"] -= delta_time
            #if len(matches[m]["votes"]) == 10 or matches[m]["time"] <= 0:
            if len(matches[m]["votes"]) == 1 or matches[m]["time"] <= 0:
                #determine most popular vote
                track = {}
                maxvote = 0
                map = ""
                for vote in matches[m]["votes"]:
                    value = matches[m]["votes"][vote]
                    if value not in track:
                        track[value] = 1
                    else:
                        track[value] += 1
                    if track[value] > maxvote:
                        maxvote = track[value]
                        map = value
                if maxvote == 0:
                    map = matches[m]["map"][random.randint(0, len(matches[m]["map"])-1)]
                matches[m]["votes"] = {}
                matches[m]["map"].remove(map)
                matches[m]["time"] = 30
                matches[m]["last message time"] = 30+MESSAGE_TIME_DIFFERENCE
                if len(matches[m]["map"]) == 1:
                    matches[m]["time"] = 300
                    matches[m]["map"] = matches[m]["map"][0]
                    await matches[m]["channels"][0].send("The match will be played on %s.\nThe match host is %s.\nPlease create a lobby on popflash.site and paste the link in this channel.\nWhen the game has finished, all players must report the result by typing \"result win\" or \"result lose\"." % (matches[m]["map"], bot.get_user(matches[m]["host"]).mention))
                else:
                    mapliststring = "maps remaining:"
                    for mv in matches[m]["map"]:
                        mapliststring += "\n    %s" % mv
                    await matches[m]["channels"][0].send("%s\nType \"vote map_name\" to vote to eliminate a map." % mapliststring)
        else:
            if len(matches[m]["votes"]) > 0:
                matches[m]["time"] -= delta_time
                if matches[m]["time"] == 0 or len(matches[m]["votes"]) == 1:
                    for channel in matches[m]["channels"]:
                        channel.delete()
                    available_lobbies.append(m)
                    result = 0 #positive - team 1 wins; negative - team 2 wins
                    for id in matches[m]["votes"]:
                        vote = 0
                        if matches[m]["votes"][vote] == "win":
                            vote = 1
                        elif matches[m]["votes"][vote] == "lose":
                            vote = -1
                        if matches[m]["players"][id]["team"] == 2:
                            vote *= -1
                        result += vote
                    winners = {}
                    winner_average = 0
                    losers = {}
                    loser_average = 0
                    for id in matches[m]["players"]:
                        elo = database.player_elo(id)
                        team = 0
                        if matches[m]["players"][id]["team"] == 1:
                            team = 1
                        elif matches[m]["players"][id]["team"] == 2:
                            team = -1
                        if result < 0:
                            team *= -1
                        if team == 1:
                            winners[id] = elo
                            winner_average += elo
                        elif team == -1:
                            losers[id] = elo
                            loser_average += elo
                    winner_average /= 5
                    loser_average /= 5
                    for id in winners:
                        expected_score = 1/(1+pow(10, (loser_average-winners[id])/400))
                        new_elo = winners[id] + ELO_K_FACTOR*(1-expected_score)
                        database.cur.execute("UPDATE playerTable SET elo=%s WHERE discordID=%s;" % (new_elo, id))
                        user = bot.get_user(id)
                        await user.send("Your last match has been recorded as a win.")
                    for id in losers:
                        expected_score = 1/(1+pow(10, (loser_average-winners[id])/400))
                        new_elo = winners[id] + ELO_K_FACTOR*(0-expected_score)
                        database.cur.execute("UPDATE playerTable SET elo=%s WHERE discordID=%s;" % (new_elo, id))
                        user = bot.get_user(id)
                        await user.send("Your last match has been recorded as a loss.")
                    database.conn.commit()
                    del matches[m]


async def process_match_commands(msg):
    is_game_chat = False
    lobby = None
    for l in matches:
        if matches[l]["channels"][0].id == msg.channel.id:
            is_game_chat = True
            lobby = l
            break
    if is_game_chat:
        if msg.content.startswith("vote "):
            if msg.author.id not in matches[lobby]["votes"]:
                map = msg.content[5:]
                if map in matches[lobby]["map"]:
                    matches[lobby]["votes"][msg.author.id] = map
                else:
                    await msg.channel.send("%s is not a valid map." % map)
        elif msg.content.startswith("result "):
            if msg.author.id not in matches[lobby]["votes"]:
                result = msg.content[7:]
                if result == "win" or result == "lose":
                    matches[lobby]["votes"][msg.author.id] = map
                else:
                    await msg.channel.send("%s is not a valid match result." % result)
