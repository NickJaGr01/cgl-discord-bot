import tornado.ioloop
import tornado.web
import database
import os

match_config = {
	"matchid": "example_match",
	"num_maps": 3,
	"players_per_team": 1,
	"min_players_to_ready": 1,
	"min_spectators_to_ready": 0,
	"skip_veto": False,
	"veto_first": "team1",
	"side_type": "standard",

	"spectators": {
		"players": []
	},

	"maplist": [],

	"team1": {
		"name": "EnvyUs",
		"tag": "EnvyUs",
		"flag": "FR",
		"logo": "nv",
		"players": {}
	},

	"team2": {
		"name": "",
		"tag": "",
		"flag": "",
		"logo": "",
		"players": []
	},

	"cvars": {
		"hostname": "Match server #1"
	}
}

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello World!")
        print("ping received")

class ConfigHandler(tornado.web.RequestHandler):
    def get(self, matchid):
        self.write(matchid)
        #database.cur.execute("SELECT team1name, team1players, team2name, team2players, map FROM matchtable WHERE id='%s';" % matchid)
        #team1_name, team1_players, team2_name, team2_players, map = database.cur.fetchone()
        #config = generate_config(team1_name, team1_players, team2_name, team2_players, map)

def make_app():
    return tornado.web.Application([
    (r"/", MainHandler),
    (r"/config/*", ConfigHandler)
    ])

app = make_app()
port = int(os.environ['PORT'])
app.listen(port)
print("listening to port %s" % port)
tornado.ioloop.IOLoop.current().start()



def generate_config(team1_name, team1_players, team2_name, team2_players, map):
    pass
