import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get():
        self.write("Hello World!")

def make_app():
    return tornado.web.Application([(r"/", MainHandler),])

app = make_app()
app.listen(8888)
tornado.ioloop.IOLoop.current().start()
