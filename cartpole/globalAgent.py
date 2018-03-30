'''
Global Agent

This class can be used to do for things below.
 a. create global network using network.py
 b. create websocket connection and keep it alive to interact with its local agents
 c. create global network and give same synchronize weights of global network to other local networks of local agents.
 e. update weights from gradients update which is received from local agents.
 f. send weights of global network to local networks to its agent
'''

import logging
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.options import define, options
import collections

import cartpole.util as util
import cartpole.network as network

define("port", default=9044, help="run on the given port", type=int)

q = collections.deque(maxlen=100)
actor, critic = network.build_model()

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/get", WSHandler)
                    ]
        settings = dict(debug=True)
        tornado.web.Application.__init__(self, handlers, **settings)

class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        print('self.local_agent_id  : ' ,self.local_agent_id)
        self.stream.set_nodelay(True)

    def on_message(self, message):
        logging.info("message: {}".format(message))

        if message == 'send_actor_model' :
            print('Server is going to send weight of actor model'.format(q))
            if len(q) == 0:
                self.write_message(str(0))
            else:
                self.write_message(str(q[len(q)-1]))
        elif message == 'request_critic_model':

        elif message == 'request_actor_model':
            q.append(message)

    def on_close(self):
        logging.info("A client disconnected")


class globalAgent():
    '''
        start server for receiving and sending information
    '''
    def __init__(self, ip, port):
        tornado.options.parse_command_line()
        app = Application()
        app.listen(options.port)
        tornado.ioloop.IOLoop.instance().start()



if __name__ == "__main__":





