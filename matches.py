import servers
import database
from bot import bot
import uuid

class Match:
    def __init__(self, team1_name, team1_players, team2_name, team2_players, map, location):
        self.team1_name = team1_name
        self.team1_name = team1_players
        self.team2_name = team2_name
        self.team2_players = team2_players
        self.map = map
        self.location = location
        self.id = uuid.uuid1()

def queue_match(match):
    database.cur.execute("INSERT INTO matchtable (id, team1name, team1players, team2name, team2players, map, location, finished) VALUES ('%s', '%s', '{%s}', '%s', '{%s}', '%s', '%s', false);" % (match.id, match.team1_name, (*match.team1_players, sep=", "), match.team2_name, (*match.team2_players, sep=", "), match.map, match.location))
    database.conn.commit()

def start_match(match):
    serverid = servers.find_open_server()
    if serverid == None:
        return False
    #move the server and start it
    scode = servers.edit_server(serverid, {'location':match.location})
    if scode != 200:
        return False
    scode = servers.start_server(serverid)
    if scode != 200:
        return False
    #tell the server to request the match config from CGL
    scode = servers.put_console(serverid, "get5_loadmatch_url https://cgl-discord-bot.herokuapp.com/config/%s" % match.id)
    if scode != 200:
        return False
    return True


async def check_matches():
    database.cur.execute("SELECT team1name, team1players, team2name, team2players, map, team1score, team2score FROM matchtable WHERE finished=true;")
    completed_matches = database.cur.fetchall()
    for team1_name, team1_players, team2_name, team2_players, map, team1_score, team2_score in completed_matches:
        print("match completed")
        await bot.appinfo.owner.send("%s (%s) - **%s**\nvs\n%s (%s) - **%s**\n%s" % (team1_name, (*team1_players, sep=", "), team1_score, team2_name, (*team2_players, sep=", "), team2_score, map))
    database.cur.execute("DELETE FROM matchtable WHERE finished=true;")
    database.conn.commit()
