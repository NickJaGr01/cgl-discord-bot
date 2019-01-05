import tornado.ioloop
import tornado.web
import os
import redis

REDIS_URL = os.environ['REDIS_URL']
r = redis.Redis.from_url(REDIS_URL)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello World!")
        r.publish('requests', "Hello World!")

def make_app():
    return tornado.web.Application([(r"/", MainHandler),])

app = make_app()
port = int(os.environ['PORT'])
app.listen(port)
print("listening to port %s" % port)
tornado.ioloop.IOLoop.current().start()
