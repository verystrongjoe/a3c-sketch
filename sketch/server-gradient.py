'''
websocket server
https://gist.github.com/timsavage/d412d9e321e9f6d358abb335c8d41c63
https://os.mbed.com/cookbook/Websockets-Server
'''
import logging
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import gen
from tornado.queues import LifoQueue as LQ
from tornado.queues import QueueEmpty
from tornado.queues import QueueFull
from tornado.queues import Queue as Q
from tornado.options import define, options
import numpy as np
# import collections

define("port", default=9045, help="run on the given port", type=int)

# we gonna store clients in dictionary..
clients = dict()

# q = collections.deque(maxlen=100)
grads_q = Q(100)
weight_q = LQ(1)


# class IndexHandler(tornado.web.RequestHandler):
#     @tornado.web.asynchronous
#     def get(self):
#         self.write("This is RL Global Network Server")
#         self.finish()

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/", WebSocketHandler),
                    (r"/send", WebSocketHandler)
                    ]

        settings = dict(debug=True)
        tornado.web.Application.__init__(self, handlers, **settings)

class WebSocketHandler(tornado.websocket.WebSocketHandler):

    _lock = False
    _recent_weight = None
    # _recent_weight = 3333333333333

    def open(self, *args):
        logging.info("A client connected.")
        self.local_agent_id = self.get_argument("local_agent_id")
        print('self.local_agent_id  : ' ,self.local_agent_id)
        self.stream.set_nodelay(True)
        clients[self.local_agent_id] = {"local_agent_id": self.local_agent_id, "object": self}

    @gen.coroutine
    def consume_weights_of_network(self):
        """
        in here, we may manage a list having last sent weights of each agent to make it sure that we send new weights
        but, for now I won't consider about it. just develop it so simple
        :return:
        """
        try:
            recent_weight = weight_q.get_nowait()
            self._recent_weight = recent_weight
            print('get new weight {}'.format(self._recent_weight))
        except QueueEmpty:
            print('no weights in weight queue')
            pass

        yield self.write_message(self._recent_weight)

    @gen.coroutine
    def calculate_mean_gradient(self):

        if not self._lock :
            self._lock = True

            num_min_threshold = 10

            # here it is best place and moment to calculate the weights
            if grads_q.qsize() >= 10:
                grads_items = []
                # while grads_q.empty():
                cnt = 0
                while cnt < num_min_threshold  :
                    i = yield grads_q.get()
                    grads_items.append(i)
                    cnt = cnt + 1
                # mean = np.mean(grads_items, axis=0)

                print('calculating neural net weight using gradients and remained {} items in queue'.format(grads_q.qsize()))

                # let's suppose that we get the weight from network
                weight_q.put('weight_calculated')
            else:
                pass

            self._lock = False

    @gen.coroutine
    def on_message(self, message):
        """
        when we receive some message we want some message handler..
        for this example i will just print message to console
        """
        logging.info("message: {}".format(message))

        if message == 'send' :
            print('Server is going to send weight!! in q {}'.format(grads_q))

            ## here is replaced by couroutine function for async programming
            yield self.consume_weights_of_network()
        else:
            yield grads_q.put(message)
            yield self.calculate_mean_gradient()

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