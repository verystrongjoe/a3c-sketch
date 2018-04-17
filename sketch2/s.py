import tornado.ioloop
import tornado.web
import tornado.websocket
import os
from tornado import gen


class EchoWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        self.write_message('hello')

    @gen.coroutine
    def on_message(self, message):
        self.write_message(message)
        self.write_message('notification')

    def on_close(self):
        print("A client disconnected!!")

if __name__ == "__main__":
    app = tornado.web.Application([(r"/", EchoWebSocket)])
    app.listen(os.getenv('PORT', 8344))
    tornado.ioloop.IOLoop.instance().start()

