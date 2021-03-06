import tornado.ioloop
import tornado.web
import database
import os
import json

match_config = {
    "matchid": "",
    "num_maps": 1,
    "players_per_team": 5,
    "min_players_to_ready": 1,
    "min_spectators_to_ready": 0,
    "skip_veto": True,
    "veto_first": "team1",
    "side_type": "standard",
    "spectators": {
        "players": []
    },
    "maplist": [],
    "team1": {
        "name": "",
        "tag": "",
        "flag": "us",
        "logo": "nip",
        "players": {}
    },
    "team2": {
        "name": "",
        "tag": "",
        "flag": "us",
        "logo": "nip"#,
        #"players": {}
    },
    "cvars": {
        "hostname": "CGL Server",
        "mp_overtime_enable": "1",
        "mp_overtime_maxrounds": "6",
        "mp_overtime_startmoney": "10000"
    }
}

def generate_config(team1_name, team1_players, team2_name, team2_players, map):
    config = match_config.copy()
    config['matchid'] = "%s vs %s" % (team1_name, team2_name)
    config['num_maps'] = 1
    config['maplist'] = []
    config['maplist'].append(map)
    config['team1']['name'] = team1_name
    config['team2']['name'] = team2_name
    for p in team1_players:
        config['team1']['players'][database.steamid(p)] = database.username(p)
    #for p in team2_players:
    #    config['team2']['players'][database.steamid(p)] = database.username(p)
    return config

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello World!")
        print("ping received")

class ConfigHandler(tornado.web.RequestHandler):
    def get(self, matchid):
        print("request received")
        database.cur.execute("SELECT team1name, team1players, team2name, team2players, map FROM matchtable WHERE id='%s';" % matchid)
        team1_name, team1_players, team2_name, team2_players, map = database.cur.fetchone()
        print("creating config")
        config = generate_config(team1_name, team1_players, team2_name, team2_players, map)
        #self.content_type='application/json'
        print("sending config")
        self.set_status(200)
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(config))

class ResultHandler(tornado.web.RequestHandler):
    def post(self, matchid, score):
        print("result received")
        scores = score.split("-")
        print("team1: %s\nteam2: %s" % (scores[0], scores[1]))


def make_app():
    return tornado.web.Application([
    (r"/", MainHandler),
    (r"/config/([0-9a-z+-]+)", ConfigHandler),
    (r"/result/([0-9a-z+-]+)/([0-9]+-[0-9]+)", ResultHandler)
    ])

app = make_app()
port = int(os.environ['PORT'])
app.listen(port)
print("listening to port %s" % port)
tornado.ioloop.IOLoop.current().start()
