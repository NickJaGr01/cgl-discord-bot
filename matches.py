import servers
import database
from bot import bot
import uuid

class Match:
    def __init__(self, team1_name, team1_players, team2_name, team2_players, map, location):
        self.team1_name = team1_name
        self.team1_players = team1_players
        self.team2_name = team2_name
        self.team2_players = team2_players
        self.map = map
        self.location = location
        self.id = uuid.uuid1()

def queue_match(match):
    t1p = ""
    for i in range(len(match.team1_players)):
        t1p += str(match.team1_players[i])
        if i < len(match.team1_players) - 1:
            t1p += ", "
    t2p = ""
    for i in range(len(match.team2_players)):
        t2p += str(match.team2_players[i])
        if i < len(match.team2_players) - 1:
            t2p += ", "
    print(t1p)
    print(t2p)
    database.cur.execute("INSERT INTO matchtable (id, team1name, team1players, team2name, team2players, map, location, finished) VALUES ('%s', '%s', '{%s}', '%s', '{%s}', '%s', '%s', false);" % (match.id, match.team1_name, t1p, match.team2_name, t2p, match.map, match.location))
    database.conn.commit()

def start_match(match):
    serverid = servers.find_open_server()
    if serverid == None:
        return None
    #move the server and start it
    scode = servers.edit_server(serverid, {'location':match.location})
    if scode != 200:
        return None
    scode = servers.start_server(serverid)
    if scode != 200:
        return None
    #tell the server to request the match config from CGL
    scode = servers.put_console(serverid, "get5_loadmatch_url \"https://cgl-discord-bot.herokuapp.com/config/%s\"" % match.id)
    if scode != 200:
        return None
    return servers.server_info(serverid)[0]


async def check_matches():
    database.cur.execute("SELECT team1name, team1players, team2name, team2players, map, team1score, team2score FROM matchtable WHERE finished=true;")
    completed_matches = database.cur.fetchall()
    for team1_name, team1_players, team2_name, team2_players, map, team1_score, team2_score in completed_matches:
        print("match completed")
        t1p = *match.team1_players, sep=", "
        t2p = *match.team2_players, sep=", "
        await bot.appinfo.owner.send("%s (%s) - **%s**\nvs\n%s (%s) - **%s**\n%s" % (team1_name, t1p, team1_score, team2_name, t2p, team2_score, map))
    database.cur.execute("DELETE FROM matchtable WHERE finished=true;")
    database.conn.commit()
