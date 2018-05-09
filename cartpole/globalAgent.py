'''
Global Agent

This class can be used to do for things below.
 a. create global network using network.py
 b. create websocket connection and keep it alive to interact with its local agents
 c. create global network and give same synchronize weights of global network to other local networks of local agents.
 e. update weights from gradients update which is received from local agents.
 f. send weights of global network to local networks to its agent

Design
 - Local Agent can request separately because each agent interacts with different environment and each episode duration is different. I think global agent has to have their own interval period to mean all gradients that they have received right after it get mean value

for this, we can set a few variables like below
num_size_grads_queue
 : which means the maximum count hainvg gradients of local agents in a queue
num_min_threshold
 : once the queue size is over this value, we will calculate mean calculation of graidents.
'''

import logging
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.options import define, options

from tornado.queues import LifoQueue as LQ
from tornado.queues import QueueEmpty
from tornado.queues import QueueFull
from tornado.queues import Queue as Q

import collections
from tornado import gen
import cartpole.util as util
import cartpole.network as network
import  gym
import cartpole.config as config
#import websockets
import asyncio
from threading import Thread
from queue import LifoQueue # use manager to use this lifoqueue in multiprocessing! http://hamait.tistory.com/755
from asyncio import Queue
import  numpy as np
from  cartpole.optimizer import SGD_custom
import pickle


define("port", default=9044, help="run on the given port", type=int)

#q = collections.deque(maxlen=100)
# grads_q = collections.deque(maxlen=3)
grads_q = Q(100)
weight_q = LQ(1)

clients = {}

env = gym.make(config.A3C_ENV['env_name'])

action_size = env.action_space.n
state_size = env.observation_space.shape[0]

actor, critic = network.build_model(state_size, action_size, 24, 24, False)  # declaring here is to share this between WShanlder and global agent


logging.basicConfig(level=logging.INFO)


class Application(tornado.web.Application):
    def __init__(self):
        logging.debug('Application init')
        handlers = [(r"/", WSHandler)
                    ]
        settings = dict(debug=True)
        tornado.web.Application.__init__(self, handlers, **settings)



class WSHandler(tornado.websocket.WebSocketHandler):

    _lock = False
    _recent_weight = None

    def __init__(self, application, request, **kwargs):
        logging.debug('WsHandler init')

        super(WSHandler, self).__init__(application, request, **kwargs)
        self.ws_connection = None
        self.close_code = None
        self.close_reason = None
        self.stream = None
        self._on_close_called = False
        self.q = asyncio.Queue(5)

    def open(self, *args):
        global clients

        self.local_agent_id = self.get_argument("local_agent_id")
        logging.debug('self.local_agent_id  : {}'.format(self.local_agent_id))
        # self.stream.set_nodelay(True)
        clients[self.local_agent_id] = self

    @gen.coroutine
    def consume_weights_of_network(self):
        """
        in here, we may manage a list having last sent weights of each agent to make it sure that we send new weights
        but, for now I won't consider about it. just develop it so simple
        :return:
        """
        logging.debug('consume_weights_of_network')
        try:
            if self._recent_weight is None:
                recent_weight = yield weight_q.get()
            else :
                recent_weight = weight_q.get_nowait()

            self._recent_weight = recent_weight
            logging.debug('new weight {}'.format(self._recent_weight))

        except QueueEmpty:
            logging.debug('no weights in weight queue')
            pass

        yield self.write_message(self._recent_weight, binary=True)

    @gen.coroutine
    def calculate_mean_gradient(self):
        logging.debug('start calculating mean gradient!!')

        if not self._lock:

            self._lock = True

            try:

                num_min_threshold = 10

                # here it is best place and moment to calculate the weights
                if grads_q.qsize() >= 10:
                    grads_actor_items, grads_critic_items = [], []
                    # while grads_q.empty():
                    cnt = 0
                    while cnt < num_min_threshold:
                        i = yield grads_q.get()
                        (a, c) = pickle.loads(i)
                        grads_actor_items.append(a)
                        grads_critic_items.append(c)
                        cnt = cnt + 1
                    mean_actor = np.mean(grads_actor_items, axis=0)
                    mean_critic = np.mean(grads_critic_items, axis=0)

                    logging.debug('----------------------------------------------------------')
                    logging.debug('calculating neural net weight using mean gradients {}'.format(mean_actor))
                    logging.debug('----------------------------------------------------------')
                    logging.debug('calculating neural net weight using mean gradients {}'.format(mean_critic))
                    logging.debug('----------------------------------------------------------')

                    # TODO: update target network using mean gradient
                    train_actor = network.get_func_train_actor_with_grads(actor)
                    train_critic = network.get_func_train_critic_with_grads(critic)

                    train_actor([i for i in mean_actor])
                    train_critic([i for i in mean_critic])

                    logging.debug('remained {} items in queue'.format(grads_q.qsize()))
                    weight_q.put(util.get_weight_with_serialized_data(actor, critic))
                else:
                    pass
            except Exception as e:
                logging.error(e)
            finally:
                self._lock = False

    @gen.coroutine
    def on_message(self, message):
        """
        when we receive some message we want some message handler..
        for this example i will just print message to console
        """
        logging.debug("on_message: {}".format(message))

        if message == 'send' :
            logging.debug('Server is going to send weight!! in q {}'.format(weight_q))
            yield self.consume_weights_of_network()
        else:
            yield grads_q.put(message)
            logging.debug('grads_q is increasing.. size :{}'.format(grads_q.qsize()))
            yield self.calculate_mean_gradient()

        # if message == 'send':
        #     if len(q) == 0:
        #         #raise RuntimeError("No weight in queue")
        #         while True:
        #             if len(q) != 0:
        #                 break
        #
        #     #TODO : in here, we need to change its data as weight
        #     yield self.write_message(q[len(q) - 1], binary=True)
        #     print('Server sent weight of actor/critic model. Weight : {} '.format(str(q[len(q) - 1])))
        # else:
        #     print('Server received weight from local: {} '.format(message))
        #     q.append(message)

    def on_close(self):
        # clients.popitem(self)
        logging.info("A client disconnected!!")

class globalAgent():

    '''
        start server for receiving and sending information
    '''
    def __init__(self, ip=None, port=None):

        logging.debug('global agent init')

        # first weight of two models must be appended to the queue
        # q.append(util.get_weight_with_serialized_data(actor, critic))
        weight_q.put(util.get_weight_with_serialized_data(actor, critic))

        logging.debug('finished putting weight into a queue')

        # tornado.options.parse_command_line()
        app = Application()

        logging.debug('about to listen.')


        if port is None :
            app.listen(options.port)
        else:
            app.listen(port)

        logging.debug('event loop start')

        tornado.ioloop.IOLoop.instance().start()


def process_global_agent(q, ip=None, port=None) :
    # first weight of two models must be appended to the queue
    q.append(util.get_weight_with_serialized_data(actor, critic))

    tornado.options.parse_command_line()
    app = Application()
    if port is None:
        app.listen(options.port)
    else:
        app.listen(port)

    tornado.ioloop.IOLoop.instance().start()


if __name__ =="__main__":

    # p = Thread(target=generating_weight, args=(grads_q,))
    # p.start()

    logging.debug('main')

    globalAgent()
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete()
    # loop.close()

