'''
websocket server
https://gist.github.com/timsavage/d412d9e321e9f6d358abb335c8d41c63
https://os.mbed.com/cookbook/Websockets-Server
'''
import threading

import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.options import define, options, parse_command_line
import socket

import local


define("port", default=8888, help="run on the given port", type=int)

# we gonna store clients in dictionary..
clients = dict()

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.write("This is your response")
        self.finish()
class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        print('new connection')
        self.id = self.get_argument("Id")
        self.stream.set_nodelay(True)
        clients[self.id] = {"id": self.id, "object": self}

    def on_message(self, message):
        """
        when we receive some message we want some message handler..
        for this example i will just print message to console
        """
        print("Client %s received a message : %s" % (self.id, message))

    def on_close(self):
        if self.id in clients:
            del clients[self.id]

app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/', WebSocketHandler),
])


if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8888)
    myIP = socket.gethostbyname(socket.gethostname())
    print('*** Websocket Server Started at %s***' % myIP)

    # http://pythonstudy.xyz/python/article/24-%EC%93%B0%EB%A0%88%EB%93%9C-Thread
    # thread1 = local.localAgent(1, '10.0.75.1', 8888)
    # thread2 = local.localAgent(2, '10.0.75.1', 8888)
    # thread1.start()
    # thread2.start()

    tornado.ioloop.IOLoop.instance().start()

