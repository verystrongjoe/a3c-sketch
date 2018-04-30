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
from tornado import gen
import websockets

import cartpole.util as util
import cartpole.network as network
import  gym
import cartpole.config as config

import asyncio

define("port", default=9044, help="run on the given port", type=int)

q = collections.deque(maxlen=100)
clients = {}

env = gym.make(config.A3C_ENV['env_name'])

action_size = env.action_space.n
state_size = env.observation_space.shape[0]

actor, critic = network.build_model(state_size, action_size, 24, 24, True)  # declaring here is to share this between WShanlder and global agent


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/", WSHandler)
                    ]
        settings = dict(debug=True)
        tornado.web.Application.__init__(self, handlers, **settings)

class WSHandler(tornado.websocket.WebSocketHandler):

    def open(self, *args):
        global clients

        self.local_agent_id = self.get_argument("local_agent_id")
        print('self.local_agent_id  : {}'.format(self.local_agent_id))
        # self.stream.set_nodelay(True)
        clients[self.local_agent_id] = self

    @gen.coroutine
    def on_message(self, message):
        # logging.info("on_message: {}".format(message))

        if message == 'send':
            if len(q) == 0:
                #raise RuntimeError("No weight in queue")
                while True:
                    if len(q) != 0:
                        break

            #TODO : in here, we need to change its data as weight
            yield self.write_message(q[len(q) - 1], binary=True)
            print('Server sent weight of actor/critic model. Weight : {} '.format(str(q[len(q) - 1])))
        else:
            print('Server received weight from local: {} '.format(message))
            q.append(message)

    def on_close(self):
        # clients.popitem(self)
        logging.info("A client disconnected!!")

class globalAgent():

    '''
        start server for receiving and sending information
    '''
    def __init__(self, ip=None, port=None):

        # first weight of two models must be appended to the queue
        q.append(util.get_weight_with_serialized_data(actor, critic))

        tornado.options.parse_command_line()
        app = Application()
        if port is None :
            app.listen(options.port)
        else:
            app.listen(port)

        tornado.ioloop.IOLoop.instance().start()

if __name__ =="__main__":
    globalAgent()