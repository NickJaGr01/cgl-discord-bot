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
		"logo": "nip",
		"players": {}
	},

	"cvars": {
		"hostname": "CGL Server"
	}
}

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello World!")
        print("ping received")

class ConfigHandler(tornado.web.RequestHandler):
    def get(self, matchid):
        database.cur.execute("SELECT team1name, team1players, team2name, team2players, map FROM matchtable WHERE id=%s;" % matchid)
        team1_name, team1_players, team2_name, team2_players, map = database.cur.fetchone()
        config = generate_config(team1_name, team1_players, team2_name, team2_players, map)
		self.write(json.dumps(config))

def make_app():
    return tornado.web.Application([
    (r"/", MainHandler),
    (r"/config/([0-9]+)", ConfigHandler)
    ])

app = make_app()
port = int(os.environ['PORT'])
app.listen(port)
print("listening to port %s" % port)
tornado.ioloop.IOLoop.current().start()



def generate_config(team1_name, team1_players, team2_name, team2_players, map):
    config = match_config.copy()
	config['matchid'] = "%s vs %s" % (team1_name, team2_name)
	config['num_maps'] = 1
	config['maplist'].append(map)
	config['team1']['name'] = team1_name
	config['team2']['name'] = team2_name
	for p in team1_players:
		config['team1']['players'][database.steamid(p)] = database.username(p)
	for p in team2_players:
		config['team2']['players'][database.steamid(p)] = database.username(p)
	return config
