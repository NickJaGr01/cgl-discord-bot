import tornado.ioloop
import tornado.web
import os

class MainHandler(tornado.web.RequestHandler):
    def get():
        self.write("Hello World!")

def make_app():
    return tornado.web.Application([(r"/", MainHandler),])

app = make_app()
app.listen(os.environ['PORT'])
tornado.ioloop.IOLoop.current().start()
