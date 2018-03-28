'''
websocket server
https://gist.github.com/timsavage/d412d9e321e9f6d358abb335c8d41c63
https://os.mbed.com/cookbook/Websockets-Server
'''
import threading
import logging
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.options import define, options, parse_command_line
import socket
import local
import time
import collections

define("port", default=9044, help="run on the given port", type=int)

# we gonna store clients in dictionary..
clients = dict()

q = collections.deque(maxlen=100)

# class IndexHandler(tornado.web.RequestHandler):
#     @tornado.web.asynchronous
#     def get(self):
#         self.write("This is RL Global Network Server")
#         self.finish()

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/", WebSocketHandler)]
        settings = dict(debug=True)
        tornado.web.Application.__init__(self, handlers, **settings)

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        logging.info("A client connected.")
        self.local_agent_id = self.get_argument("local_agent_id")
        print('self.local_agent_id  : ' ,self.local_agent_id)
        self.stream.set_nodelay(True)
        clients[self.local_agent_id] = {"local_agent_id": self.local_agent_id, "object": self}

    def on_message(self, message):
        """
        when we receive some message we want some message handler..
        for this example i will just print message to console
        """
        logging.info("message: {}".format(message))

        if message == 'send' :
            print('Server is going to send weight!! in q {}'.format(q))
            if len(q) == 0:
                self.write_message(str(0))
            else:
                self.write_message(str(q[len(q)-1]))
        else:
            q.append(message)

    def on_close(self):
        logging.info("A client disconnected")
        pass
        # if self.id in clients:
        #     del clients[self.id]

if __name__ == "__main__":

    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

    print('listening...')

    # http://pythonstudy.xyz/python/article/24-%EC%93%B0%EB%A0%88%EB%93%9C-Thread
    # thread1 = local.localAgent(1, '10.0.75.1', 8888)
    # thread2 = local.localAgent(2, '10.0.75.1', 8888)
    # thread1.start()
    # thread2.start()

